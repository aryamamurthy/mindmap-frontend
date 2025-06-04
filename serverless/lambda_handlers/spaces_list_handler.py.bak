import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
SPACES_TABLE_NAME = os.environ.get('SPACES_TABLE_NAME', 'MindMapSpaces')

def lambda_handler(event, context):
    try:
        # owner_id would come from event['requestContext']['authorizer']['claims']['sub'] if using Cognito JWT
        owner_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'ANONYMOUS_USER')

        table = dynamodb.Table(SPACES_TABLE_NAME)
        
        # This assumes a GSI on ownerId named 'OwnerIdIndex' for efficient querying.
        # PK for GSI: ownerId
        # If no GSI and not many users, a scan might be acceptable for very small tables, but not recommended.
        # For simplicity without immediate GSI setup, we'll filter on ownerId. 
        # THIS WILL SCAN THE WHOLE TABLE if ownerId is not part of a GSI or primary key.
        # Consider adding a GSI: GlobalSecondaryIndexes=[{'IndexName': 'OwnerIdIndex', 'KeySchema': [{'AttributeName': 'ownerId', 'KeyType': 'HASH'}], 'Projection': {'ProjectionType': 'ALL'}}] 

        params = {
            'FilterExpression': boto3.dynamodb.conditions.Attr('ownerId').eq(owner_id) & boto3.dynamodb.conditions.Attr('SK').eq('META')
        }
        # If you have an OwnerIdIndex GSI:
        # params = {
        # 'IndexName': 'OwnerIdIndex',
        # 'KeyConditionExpression': boto3.dynamodb.conditions.Key('ownerId').eq(owner_id)
        # }
        
        response = table.scan(**params) # Use query if using GSI
        
        items = response.get('Items', [])
        
        spaces = []
        for item in items:
            spaces.append({
                'spaceId': item.get('spaceId'),
                'name': item.get('name'),
                'description': item.get('description'),
                'createdAt': item.get('createdAt')
            })

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(spaces)
        }

    except Exception as e:
        print(f"Error listing spaces: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not list spaces', 'details': str(e)})
        }
