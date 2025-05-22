import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
spaces_table_name = os.environ.get('SPACES_TABLE_NAME', 'Spaces')
spaces_table = dynamodb.Table(spaces_table_name)
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes')
nodes_table = dynamodb.Table(nodes_table_name)

def lambda_handler(event, context):
    """
    Deletes a space and all its associated nodes.
    Required path parameter: spaceId
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

        # 1. Delete all nodes associated with the spaceId
        # We need to query all nodes for the space first, then delete them.
        # A GSI on spaceId for the Nodes table would be efficient here.
        # For now, we'll scan, which is not ideal for large tables.
        # Consider if Nodes table has a GSI on spaceId for efficient querying.
        
        # Query for nodes belonging to the space
        # If a GSI `SpaceIdIndex` exists on `Nodes` table with `spaceId` as its hash key:
        # response_nodes = nodes_table.query(
        #     IndexName='SpaceIdIndex', # Assuming a GSI named 'SpaceIdIndex'
        #     KeyConditionExpression=boto3.dynamodb.conditions.Key('spaceId').eq(space_id)
        # )
        # For now, using scan as a fallback (less efficient)
        response_nodes = nodes_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('spaceId').eq(space_id)
        )
        
        nodes_to_delete = response_nodes.get('Items', [])

        if nodes_to_delete:
            with nodes_table.batch_writer() as batch:
                for node in nodes_to_delete:
                    batch.delete_item(
                        Key={
                            'nodeId': node['nodeId'],
                            'spaceId': node['spaceId'] # Assuming composite key for Nodes table
                        }
                    )
            print(f"Deleted {len(nodes_to_delete)} nodes for space {space_id}")

        # 2. Delete the space itself
        spaces_table.delete_item(
            Key={
                'spaceId': space_id
            }
        )

        return {
            'statusCode': 204,
            'headers': {'Content-Type': 'application/json'},
            'body': ''
        }

    except Exception as e:
        print(f"Error deleting space: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
