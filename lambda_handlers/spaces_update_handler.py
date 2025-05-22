import json
import boto3
import os
import datetime

dynamodb = boto3.resource('dynamodb')
spaces_table_name = os.environ.get('SPACES_TABLE_NAME', 'Spaces') # Default to 'Spaces' if not set
spaces_table = dynamodb.Table(spaces_table_name)

def lambda_handler(event, context):
    """
    Updates an existing space's attributes (name, description).
    Required path parameter: spaceId
    Required body attributes: name, description
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

        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        description = body.get('description')

        if not name and not description:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'At least name or description must be provided for update'})
            }

        # Construct the update expression
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {} # For attributes that are reserved keywords

        if name:
            update_expression_parts.append('#n = :n')
            expression_attribute_values[':n'] = name
            expression_attribute_names['#n'] = 'name' # 'name' is a reserved keyword
        
        if description is not None: # Allow empty string for description
            update_expression_parts.append('description = :d')
            expression_attribute_values[':d'] = description
        
        update_expression_parts.append('updatedAt = :ua')
        expression_attribute_values[':ua'] = datetime.datetime.utcnow().isoformat()

        update_expression = 'SET ' + ', '.join(update_expression_parts)

        params = {
            'Key': {
                'spaceId': space_id
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ReturnValues': 'UPDATED_NEW'
        }
        if expression_attribute_names: # Add if there are any reserved keywords used
            params['ExpressionAttributeNames'] = expression_attribute_names


        # Check if the item exists before updating
        # Note: A more robust check might involve a GetItem first or conditional update
        # For simplicity, we proceed with the update and handle potential errors.
        # A ConditionExpression like 'attribute_exists(spaceId)' could be used.

        response = spaces_table.update_item(**params)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response.get('Attributes', {}))
        }

    except Exception as e:
        print(f"Error updating space: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
