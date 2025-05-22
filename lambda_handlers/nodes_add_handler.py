import json
import boto3
import os
import uuid
import datetime

dynamodb = boto3.resource('dynamodb')
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes') # Default to 'Nodes'
nodes_table = dynamodb.Table(nodes_table_name)
s3_client = boto3.client('s3')
content_bucket_name = os.environ.get('CONTENT_BUCKET_NAME', 'mindmap-content-bucket') # Default bucket name

def lambda_handler(event, context):
    """
    Adds a new node to a space.
    Required path parameter: spaceId
    Required body attributes: title, contentHTML (optional), parentNodeId (optional, for sub-nodes), orderIndex (optional)
    """
    try:
        path_parameters = event.get('pathParameters', {})
        space_id = path_parameters.get('spaceId')

        if not space_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId is required'})
            }

        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        content_html = body.get('contentHTML') # This is the actual HTML content
        parent_node_id = body.get('parentNodeId') # Can be null for root nodes
        order_index = body.get('orderIndex', 0) # Default orderIndex if not provided

        if not title:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'title is required'})
            }

        node_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        s3_key = None

        # If contentHTML is provided, upload it to S3
        if content_html is not None:
            s3_key = f"{space_id}/{node_id}.html"
            try:
                s3_client.put_object(
                    Bucket=content_bucket_name,
                    Key=s3_key,
                    Body=content_html.encode('utf-8'),
                    ContentType='text/html'
                )
            except Exception as e:
                print(f"Error uploading to S3: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Failed to upload content to S3: {str(e)}'})
                }

        node_item = {
            'nodeId': node_id,
            'spaceId': space_id,
            'title': title,
            's3Key': s3_key, # Store S3 key, will be null if no contentHTML
            'parentNodeId': parent_node_id,
            'orderIndex': order_index,
            'createdAt': created_at,
            'updatedAt': created_at,
            'children': [] # Initialize with empty children list, though this might be dynamically constructed on read
        }

        nodes_table.put_item(Item=node_item)

        # Remove 'children' for the response as it's not stored directly in this item usually
        # Or, decide if the API should return it. For now, returning the created item as stored.
        # If children are dynamically populated, this field in the DB item might be redundant.
        # For simplicity, let's return what was put into DB.

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Location': f"/spaces/{space_id}/nodes/{node_id}"
            },
            'body': json.dumps(node_item)
        }

    except Exception as e:
        print(f"Error adding node: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
