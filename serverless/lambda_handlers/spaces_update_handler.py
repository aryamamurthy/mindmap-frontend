import json
import boto3
import os
import datetime
import decimal

# Helper class to convert Decimal to float/int for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # Convert decimal to int or float
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

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

        # Use the correct key format for the Spaces table
        params = {
            'Key': {
                'PK': f"SPACE#{space_id}",
                'SK': "META"
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ReturnValues': 'ALL_NEW'  # Return all attributes of the updated item
        }
        if expression_attribute_names: # Add if there are any reserved keywords used
            params['ExpressionAttributeNames'] = expression_attribute_names

        # Update the item
        response = spaces_table.update_item(**params)
        attributes = response.get('Attributes', {})

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(attributes, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error updating space: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
