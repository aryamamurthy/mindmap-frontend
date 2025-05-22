import json
import boto3
import uuid
import datetime
import os

dynamodb = boto3.resource('dynamodb')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'users') # Get from environment variables

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        email = body.get('email')

        if not name or not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Name and email are required'})
            }

        user_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()

        item = {
            'Id': user_id,
            'name': name,
            'email': email,
            'createdAt': created_at,
            'updatedAt': created_at # Initially same as createdAt
        }

        table = dynamodb.Table(USERS_TABLE_NAME)
        table.put_item(Item=item)

        response_body = {
            'Id': user_id,
            'name': name,
            'email': email,
            'createdAt': created_at
        }

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Location': f"/users/{user_id}"
            },
            'body': json.dumps(response_body)
        }

    except Exception as e:
        print(f"Error creating user: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Could not create user', 'details': str(e)})
        }
