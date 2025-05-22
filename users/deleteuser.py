import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'users')

def lambda_handler(event, context):
    try:
        user_id = event.get('pathParameters', {}).get('id')
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'id is required in path'})
            }
        table = dynamodb.Table(USERS_TABLE_NAME)
        resp = table.delete_item(Key={'Id': user_id})
        return {
            'statusCode': 204,
            'headers': {'Content-Type': 'application/json'},
            'body': ''
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
