import json
import boto3
import os
import datetime

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
        body = json.loads(event.get('body', '{}'))
        update_expr = []
        expr_attr_vals = {}
        expr_attr_names = {}
        for field in ['name', 'email']:
            if field in body:
                if field == 'name':
                    update_expr.append('#n = :n')
                    expr_attr_vals[':n'] = body['name']
                    expr_attr_names['#n'] = 'name'
                else:
                    update_expr.append('email = :e')
                    expr_attr_vals[':e'] = body['email']
        if not update_expr:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No updatable fields provided'})
            }
        update_expr.append('updatedAt = :u')
        expr_attr_vals[':u'] = datetime.datetime.utcnow().isoformat()
        table = dynamodb.Table(USERS_TABLE_NAME)
        update_kwargs = {
            'Key': {'Id': user_id},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_attr_vals,
            'ReturnValues': 'ALL_NEW'
        }
        if expr_attr_names:
            update_kwargs['ExpressionAttributeNames'] = expr_attr_names
        resp = table.update_item(**update_kwargs)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(resp.get('Attributes', {}))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
