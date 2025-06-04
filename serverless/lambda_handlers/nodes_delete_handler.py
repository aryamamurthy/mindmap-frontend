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
    Deletes a node and its content from S3. 
    Also needs to handle deletion of child nodes recursively.
    Required path parameters: spaceId, nodeId
    """
    try:
        path_parameters = event.get('pathParameters', {})
        space_id = path_parameters.get('spaceId')
        node_id_to_delete = path_parameters.get('nodeId')

        if not space_id or not node_id_to_delete:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId and nodeId are required in path parameters'})
            }

        # Store all nodes to be deleted (target node + all its descendants)
        all_nodes_to_delete_keys = [] # List of Key dicts for batch_delete
        all_s3_keys_to_delete = [] # List of S3 keys

        # Recursive function to find all child nodes
        def find_and_collect_children(current_node_id, current_space_id):
            # Get the node itself to check for s3Key
            try:
                node_response = nodes_table.get_item(Key={'nodeId': current_node_id, 'spaceId': current_space_id})
                node_item = node_response.get('Item')
                if node_item:
                    all_nodes_to_delete_keys.append({'nodeId': current_node_id, 'spaceId': current_space_id})
                    if node_item.get('s3Key'):
                        all_s3_keys_to_delete.append(node_item['s3Key'])
            except Exception as e:
                print(f"Error fetching node {current_node_id} for deletion prep: {e}")
                # Continue, try to delete what we can

            # Find direct children of the current node
            # This requires a GSI on parentNodeId or a scan.
            # Assuming a GSI: ParentNodeIdIndex with hash key parentNodeId and range key spaceId (or just parentNodeId if globally unique)
            # For now, using a scan for simplicity, but this is inefficient.
            # A better approach for tree structures in DynamoDB might involve adjacency lists or materialized paths.
            
            # Scan for children - INEFFICIENT for large tables without GSI
            children_response = nodes_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('parentNodeId').eq(current_node_id) & boto3.dynamodb.conditions.Attr('spaceId').eq(current_space_id)
            )
            children = children_response.get('Items', [])
            
            for child in children:
                find_and_collect_children(child['nodeId'], child['spaceId'])

        # Start collection from the initially targeted node
        find_and_collect_children(node_id_to_delete, space_id)

        # Delete S3 objects if any
        if all_s3_keys_to_delete:
            delete_s3_objects = [{'Key': s3_key} for s3_key in all_s3_keys_to_delete]
            try:
                s3_client.delete_objects(
                    Bucket=content_bucket_name,
                    Delete={'Objects': delete_s3_objects}
                )
                print(f"Deleted {len(delete_s3_objects)} S3 objects.")
            except Exception as e:
                print(f"Error deleting S3 objects: {e}")
                # Log error but continue to attempt DynamoDB deletion

        # Delete DynamoDB items (nodes)
        deleted_count = 0
        if all_nodes_to_delete_keys:
            with nodes_table.batch_writer() as batch:
                for key in all_nodes_to_delete_keys:
                    batch.delete_item(Key=key)
                    deleted_count += 1
            print(f"Deleted {deleted_count} nodes from DynamoDB.")
        
        if deleted_count == 0 and not all_s3_keys_to_delete: # Check if the root node to delete was even found
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Node {node_id_to_delete} not found or no associated data to delete.'})
            }

        return {
            'statusCode': 204,
            'headers': {'Content-Type': 'application/json'},
            'body': ''
        }

    except Exception as e:
        print(f"Error deleting node: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
