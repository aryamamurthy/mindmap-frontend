import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes')
nodes_table = dynamodb.Table(nodes_table_name)
s3_client = boto3.client('s3')
content_bucket_name = os.environ.get('CONTENT_BUCKET_NAME', 'mindmap-content-bucket')

def lambda_handler(event, context):
    """
    Retrieves a specific node's details, including its content from S3 if available.
    Required path parameters: spaceId, nodeId
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

        # Get node metadata from DynamoDB
        response = nodes_table.get_item(
            Key={
                'nodeId': node_id,
                'spaceId': space_id # Assuming composite key (nodeId, spaceId)
            }
        )

        node_item = response.get('Item')

        if not node_item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Node not found'})
            }

        # If there's an S3 key, fetch the content from S3
        s3_key = node_item.get('s3Key')
        content_html = None
        if s3_key:
            try:
                s3_response = s3_client.get_object(
                    Bucket=content_bucket_name,
                    Key=s3_key
                )
                content_html = s3_response['Body'].read().decode('utf-8')
            except Exception as e:
                print(f"Error fetching content from S3 for key {s3_key}: {e}")
                # Decide if this should be a critical error or just return node without content
                # For now, let's return the node metadata even if S3 fetch fails, with a note.
                node_item['contentError'] = f'Failed to fetch content from S3: {str(e)}'
        
        node_item['contentHTML'] = content_html # Add contentHTML to the response

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(node_item)
        }

    except Exception as e:
        print(f"Error getting node: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
