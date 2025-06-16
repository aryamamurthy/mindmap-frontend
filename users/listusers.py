import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'users')

def lambda_handler(event, context):
    try:
        table = dynamodb.Table(USERS_TABLE_NAME)
        resp = table.scan()
        users = resp.get('Items', [])
        # Optionally, rename 'Id' to 'userId' in the response for clarity
        for user in users:
            if 'Id' in user:
                user['userId'] = user.pop('Id')
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(users)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
