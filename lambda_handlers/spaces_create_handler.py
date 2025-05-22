import json
import boto3
import uuid
import datetime
import os

dynamodb = boto3.resource('dynamodb')
SPACES_TABLE_NAME = os.environ.get('SPACES_TABLE_NAME', 'MindMapSpaces') # Get from environment variables

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        description = body.get('description')

        if not name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Name is required'})
            }

        space_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        # owner_id would come from event['requestContext']['authorizer']['claims']['sub'] if using Cognito JWT
        owner_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'ANONYMOUS_USER')


        item = {
            'PK': f'SPACE#{space_id}',
            'SK': 'META',
            'spaceId': space_id,
            'name': name,
            'description': description,
            'ownerId': owner_id,
            'createdAt': created_at,
            'updatedAt': created_at # Initially same as createdAt
        }

        table = dynamodb.Table(SPACES_TABLE_NAME)
        table.put_item(Item=item)

        response_body = {
            'spaceId': space_id,
            'name': name,
            'description': description,
            'createdAt': created_at,
            'ownerId': owner_id
        }

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Location': f"/spaces/{space_id}"
            },
            'body': json.dumps(response_body)
        }

    except Exception as e:
        print(f"Error creating space: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not create space', 'details': str(e)})
        }
