import json
import boto3
import os
import datetime

dynamodb = boto3.resource('dynamodb')
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes')
nodes_table = dynamodb.Table(nodes_table_name)
s3_client = boto3.client('s3')
content_bucket_name = os.environ.get('CONTENT_BUCKET_NAME', 'mindmap-content-bucket')
eventbridge_client = boto3.client('events')
event_bus_name = os.environ.get('EVENT_BUS_NAME', 'mindmap-events-bus-dev')

def lambda_handler(event, context):
    """
    Updates a node's attributes (title, contentHTML, parentNodeId, orderIndex).
    Required path parameters: spaceId, nodeId
    Body can contain: title, contentHTML, parentNodeId, orderIndex
    """
    try:
        path_parameters = event.get('pathParameters', {})
        space_id = path_parameters.get('spaceId')
        node_id = path_parameters.get('nodeId')

        if not space_id or not node_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId and nodeId are required in path parameters'})
            }

        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        content_html = body.get('contentHTML') # Raw HTML content
        parent_node_id = body.get('parentNodeId')
        order_index = body.get('orderIndex')

        if not title and content_html is None and parent_node_id is None and order_index is None:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'At least one attribute (title, contentHTML, parentNodeId, orderIndex) must be provided for update'})
            }

        # Fetch existing node to get current s3Key if content is being updated
        # This is also a way to check if the node exists before attempting an update.
        try:
            existing_node_response = nodes_table.get_item(
                Key={
                    'nodeId': node_id,
                    'spaceId': space_id
                }
            )
            existing_node = existing_node_response.get('Item')
            if not existing_node:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Node not found'})
                }
        except Exception as e:
            print(f"Error fetching node for update check: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Error checking node existence: {str(e)}'})
            }

        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {} # For attributes that are reserved keywords

        if title is not None:
            update_expression_parts.append('title = :t')
            expression_attribute_values[':t'] = title

        if parent_node_id is not None:
            update_expression_parts.append('parentNodeId = :pni')
            expression_attribute_values[':pni'] = parent_node_id
        
        if order_index is not None:
            update_expression_parts.append('orderIndex = :oi')
            expression_attribute_values[':oi'] = order_index

        # Handle contentHTML update (S3 part)
        current_s3_key = existing_node.get('s3Key')
        new_s3_key = current_s3_key

        if content_html is not None:
            if content_html == "": # If content is explicitly set to empty, delete S3 object if it exists
                if current_s3_key:
                    try:
                        s3_client.delete_object(Bucket=content_bucket_name, Key=current_s3_key)
                        print(f"Deleted S3 object {current_s3_key} as contentHTML is empty.")
                    except Exception as e:
                        print(f"Error deleting S3 object {current_s3_key}: {e}")
                        # Potentially log this but don't fail the whole update
                new_s3_key = None # Set s3Key to null in DynamoDB
            else: # New or updated content
                # Use existing key if available and makes sense, or generate/use a standard one
                # For simplicity, let's assume s3_key is tied to nodeId and spaceId
                new_s3_key = f"{space_id}/{node_id}.html"
                try:
                    s3_client.put_object(
                        Bucket=content_bucket_name,
                        Key=new_s3_key,
                        Body=content_html.encode('utf-8'),
                        ContentType='text/html'
                    )
                except Exception as e:
                    print(f"Error uploading updated content to S3: {e}")
                    return {
                        'statusCode': 500,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': f'Failed to update content in S3: {str(e)}'})
                    }
            # Update s3Key in DynamoDB if it has changed
            if new_s3_key != current_s3_key:
                 update_expression_parts.append('s3Key = :sk')
                 expression_attribute_values[':sk'] = new_s3_key
            elif new_s3_key is None and current_s3_key is not None: # Handle case where s3Key becomes null
                 update_expression_parts.append('s3Key = :sk')
                 expression_attribute_values[':sk'] = None


        if not update_expression_parts:
             # This case should ideally be caught earlier, but as a safeguard:
            return {
                'statusCode': 200, # Or 304 Not Modified, but 200 with current item is also fine
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(existing_node) # No changes to DynamoDB attributes other than potentially s3Key handled above
            }

        update_expression_parts.append('updatedAt = :ua')
        expression_attribute_values[':ua'] = datetime.datetime.utcnow().isoformat()

        update_expression = 'SET ' + ', '.join(update_expression_parts)
        
        params = {
            'Key': {
                'nodeId': node_id,
                'spaceId': space_id
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,            'ReturnValues': 'UPDATED_NEW'
        }
        if expression_attribute_names:
            params['ExpressionAttributeNames'] = expression_attribute_names

        response = nodes_table.update_item(**params)

        # Publish event for content generation (only if title was updated and no existing content)
        if title is not None and not existing_node.get('s3Key'):
            try:
                event_detail = {
                    'nodeId': node_id,
                    'spaceId': space_id,
                    'title': title,
                    'parentNodeId': existing_node.get('parentNodeId'),
                    'orderIndex': existing_node.get('orderIndex', 0),
                    'updatedAt': expression_attribute_values[':ua']
                }
                
                eventbridge_client.put_events(
                    Entries=[
                        {
                            'Source': 'mindmap-content-events',
                            'DetailType': 'MindMapNode Updated',
                            'Detail': json.dumps(event_detail),
                            'EventBusName': event_bus_name
                        }
                    ]
                )
                print(f"Published node update event for {node_id}")
            except Exception as e:
                print(f"Failed to publish event: {e}")
                # Don't fail the whole operation if event publishing fails

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response.get('Attributes', {}))
        }

    except Exception as e:
        print(f"Error updating node: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
