import json
import boto3
import os
import datetime

dynamodb = boto3.resource('dynamodb')
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes')
nodes_table = dynamodb.Table(nodes_table_name)

def lambda_handler(event, context):
    """
    Reorders sibling nodes under a common parent or root nodes within a space.
    Required path parameter: spaceId
    Required body: an array of objects, each with nodeId and newOrderIndex.
    Example body: [{ "nodeId": "id1", "newOrderIndex": 0 }, { "nodeId": "id2", "newOrderIndex": 1 }]
    All nodes in the list MUST share the same parentNodeId (or be root nodes of the same space).
    """
    try:
        path_parameters = event.get('pathParameters', {})
        space_id = path_parameters.get('spaceId')

        if not space_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId is required in path parameters'})
            }

        body = json.loads(event.get('body', '[]'))
        if not isinstance(body, list) or not all(isinstance(item, dict) and 'nodeId' in item and 'newOrderIndex' in item for item in body):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Request body must be a list of objects, each with nodeId and newOrderIndex'})
            }
        
        if not body:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Node reorder list cannot be empty'})
            }

        # For simplicity, this handler assumes all nodes in the list are siblings
        # (i.e., share the same parentNodeId or are all root nodes for the given spaceId).
        # A more robust implementation would verify this by fetching one node and checking its parentNodeId,
        # then ensuring all other nodes in the list share it.
        # It also assumes that the provided orderIndexes are valid (e.g., 0 to N-1 for N siblings).

        updated_at = datetime.datetime.utcnow().isoformat()
        failed_updates = []

        # Using BatchWriteItem for updating multiple items is more efficient for DynamoDB,
        # but UpdateItem is used here per node for clarity and individual error handling if needed.
        # For true batching of updates, you'd construct Update operations for a TransactWriteItems or BatchWriteItem (if applicable).
        # However, UpdateItem is fine for a small number of reordered items.

        for item_to_reorder in body:
            node_id = item_to_reorder.get('nodeId')
            new_order_index = item_to_reorder.get('newOrderIndex')

            if node_id is None or new_order_index is None:
                failed_updates.append({'nodeId': node_id, 'error': 'Missing nodeId or newOrderIndex'})
                continue
            
            try:
                nodes_table.update_item(
                    Key={
                        'nodeId': node_id,
                        'spaceId': space_id # Assuming composite key
                    },
                    UpdateExpression='SET orderIndex = :oi, updatedAt = :ua',
                    ExpressionAttributeValues={
                        ':oi': new_order_index,
                        ':ua': updated_at
                    },
                    ConditionExpression='attribute_exists(nodeId)' # Ensure node exists
                )
            except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
                failed_updates.append({'nodeId': node_id, 'error': 'Node not found or condition check failed'})
            except Exception as e:
                print(f"Error reordering node {node_id}: {e}")
                failed_updates.append({'nodeId': node_id, 'error': str(e)})

        if failed_updates:
            return {
                'statusCode': 207, # Multi-Status
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Some nodes failed to reorder.',
                    'failedUpdates': failed_updates
                })
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': f'{len(body)} nodes reordered successfully in space {space_id}'})
        }

    except Exception as e:
        print(f"Error processing node reorder request: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
