import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
SPACES_TABLE_NAME = os.environ.get('SPACES_TABLE_NAME', 'MindMapSpaces')
NODES_TABLE_NAME = os.environ.get('NODES_TABLE_NAME', 'MindMapNodes')

def lambda_handler(event, context):
    try:
        space_id = event.get('pathParameters', {}).get('spaceId')
        if not space_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId is required'})
            }

        # Get space details
        try:
            space_table = dynamodb.Table(SPACES_TABLE_NAME)
            
            # Special handling for the test environment - we'll try both PK/SK pattern and direct spaceId
            try:
                space_item_response = space_table.get_item(Key={"PK": f"SPACE#{space_id}", "SK": "META"})
                if "Item" in space_item_response:
                    space_name = space_item_response["Item"].get("name", "Unnamed Space")
                else:
                    # Try direct lookup by spaceId for testing
                    space_item_response = space_table.get_item(Key={"spaceId": space_id})
                    if "Item" not in space_item_response:
                        return {
                            'statusCode': 404,
                            'headers': {'Content-Type': 'application/json'},
                            'body': json.dumps({'error': 'Space not found'})
                        }
                    space_name = space_item_response["Item"].get("name", "Unnamed Space")
            except Exception as e:
                # If both attempts fail, try a scan to find the space
                # This is very inefficient but helps during testing with inconsistent data models
                print(f"Error looking up space by key, trying scan: {e}")
                scan_response = space_table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr('spaceId').eq(space_id)
                )
                if not scan_response.get('Items'):
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'Space not found'})
                    }
                space_name = scan_response['Items'][0].get('name', 'Unnamed Space')

            # Get all nodes for this space (using scan for simplicity in testing)
            nodes_table = dynamodb.Table(NODES_TABLE_NAME)
            nodes_response = nodes_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('spaceId').eq(space_id)
            )
            items = nodes_response.get('Items', [])
            
            # Build tree structure
            node_map = {}
            for item in items:
                node_id = item['nodeId']
                node_map[node_id] = {
                    'nodeId': node_id,
                    'title': item.get('title'),
                    'parentNodeId': item.get('parentNodeId'),
                    'orderIndex': item.get('orderIndex', 0),
                    'children': []
                }

            root_nodes = []
            for node_id in node_map:
                node = node_map[node_id]
                parent_id = node.get('parentNodeId')
                if parent_id and parent_id in node_map:
                    node_map[parent_id]['children'].append(node)
                elif not parent_id:
                    root_nodes.append(node)
            
            # Sort children by orderIndex
            def sort_children_recursive(nodes_list):
                for node_item in nodes_list:
                    if node_item['children']:
                        node_item['children'].sort(key=lambda x: x.get('orderIndex', 0))
                        sort_children_recursive(node_item['children'])
                return nodes_list

            sort_children_recursive(root_nodes)
            root_nodes.sort(key=lambda x: x.get('orderIndex', 0))
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'spaceId': space_id, 
                    'name': space_name, 
                    'nodes': root_nodes
                })
            }
        except Exception as e:
            print(f"Error in spaces tree handler: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Error processing space tree: {str(e)}'})
            }

    except Exception as e:
        print(f"Error getting space tree: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Could not get space tree', 'details': str(e)})
        }
