import json
import boto3
import uuid
import datetime
import os
import time
import traceback
from utils.logger import StructuredLogger, PerformanceTracker, extract_correlation_id, extract_user_id

# Initialize structured logger
logger = StructuredLogger('spaces_create_handler')

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
SPACES_TABLE_NAME = os.environ.get('SPACES_TABLE_NAME', 'MindMapSpaces')

def lambda_handler(event, context):
    start_time = time.time()
    correlation_id = extract_correlation_id(event)
    user_id = extract_user_id(event)
    
    try:
        # Log incoming request
        logger.request(
            method=event.get('httpMethod', 'POST'),
            path=event.get('path', '/spaces'),
            correlation_id=correlation_id,
            user_id=user_id,
            body=json.loads(event.get('body', '{}')),
            headers=event.get('headers', {})
        )
        
        # Parse and validate request body
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        description = body.get('description')

        if not name:
            logger.business_logic(
                message="Space creation failed: name is required",
                correlation_id=correlation_id,
                operation="validate_input",
                additional_data={"validation_error": "missing_name"}
            )
            
            response = {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Name is required'})
            }
            
            logger.response(
                status_code=400,
                correlation_id=correlation_id,
                response_size=len(response['body'])
            )
            
            return response

        # Generate space data
        space_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()
        owner_id = user_id or 'ANONYMOUS_USER'

        logger.business_logic(
            message=f"Creating new space: {name}",
            correlation_id=correlation_id,
            operation="space_creation",
            additional_data={
                "space_id": space_id,
                "space_name": name,
                "owner_id": owner_id
            }
        )

        # Prepare DynamoDB item
        item = {
            'PK': f'SPACE#{space_id}',
            'SK': 'META',
            'spaceId': space_id,
            'name': name,
            'description': description,
            'ownerId': owner_id,
            'createdAt': created_at,
            'updatedAt': created_at
        }

        # Execute database operation with performance tracking
        with PerformanceTracker(logger, 'dynamodb_put_item', correlation_id):
            table = dynamodb.Table(SPACES_TABLE_NAME)
            table.put_item(Item=item)
            
        logger.database_operation(
            operation="put_item",
            table_name=SPACES_TABLE_NAME,
            correlation_id=correlation_id,
            item_count=1
        )

        # Prepare response
        response_body = {
            'spaceId': space_id,
            'name': name,
            'description': description,
            'createdAt': created_at,
            'ownerId': owner_id
        }

        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Location': f"/spaces/{space_id}",
                'X-Correlation-ID': correlation_id
            },
            'body': json.dumps(response_body)
        }

        # Log successful response
        execution_time_ms = (time.time() - start_time) * 1000
        logger.response(
            status_code=201,
            correlation_id=correlation_id,
            response_size=len(response['body']),
            execution_time_ms=execution_time_ms
        )

        logger.business_logic(
            message=f"Space created successfully: {space_id}",
            correlation_id=correlation_id,
            operation="space_creation_complete",
            additional_data={"space_id": space_id}
        )

        return response

    except json.JSONDecodeError as e:
        logger.error(
            error_type="JSONDecodeError",
            message="Invalid JSON in request body",
            correlation_id=correlation_id,
            error_code="INVALID_JSON",
            additional_context={"raw_body": event.get('body', '')}
        )
        
        response = {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
        
        logger.response(
            status_code=400,
            correlation_id=correlation_id,
            response_size=len(response['body'])
        )
        
        return response

    except Exception as e:
        logger.error(
            error_type=type(e).__name__,
            message=f"Error creating space: {str(e)}",
            correlation_id=correlation_id,
            stack_trace=traceback.format_exc(),
            error_code="SPACE_CREATION_FAILED",
            additional_context={
                "space_name": body.get('name') if 'body' in locals() else None,
                "owner_id": owner_id if 'owner_id' in locals() else None
            }
        )
        
        response = {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Could not create space', 'details': str(e)})
        }
        
        logger.response(
            status_code=500,
            correlation_id=correlation_id,
            response_size=len(response['body'])
        )
        
        return response
