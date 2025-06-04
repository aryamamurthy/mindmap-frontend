import json
import boto3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    # Log event information
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Get table name from environment variable
        SPACES_TABLE_NAME = os.environ.get('SPACES_TABLE_NAME', 'MindMapSpaces')
        logger.info(f"Using table name: {SPACES_TABLE_NAME}")
        
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(SPACES_TABLE_NAME)
        
        # owner_id would come from event['requestContext']['authorizer']['claims']['sub'] if using Cognito JWT
        owner_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'ANONYMOUS_USER')
        logger.info(f"Owner ID: {owner_id}")
        
        # Check if running in local environment
        is_local = os.environ.get('IS_LOCAL', False) or 'localhost' in str(event.get('headers', {}))
        
        if is_local:
            # For local development, return mock data
            logger.info("Running in local environment, returning mock data")
            mock_spaces = [
                {
                    'spaceId': 'mock-space-1',
                    'name': 'Mock Space 1',
                    'description': 'This is a mock space for local development',
                    'createdAt': '2025-05-22T00:00:00.000Z',
                    'ownerId': owner_id
                },
                {
                    'spaceId': 'mock-space-2',
                    'name': 'Mock Space 2',
                    'description': 'Another mock space for testing',
                    'createdAt': '2025-05-22T00:00:00.000Z',
                    'ownerId': owner_id
                }
            ]
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(mock_spaces)
            }
            
        # For production, query the actual DynamoDB table
        try:
            # Check if the table exists
            dynamodb_client = boto3.client('dynamodb')
            dynamodb_client.describe_table(TableName=SPACES_TABLE_NAME)
            
            # First try to use GSI if available
            try:
                logger.info("Attempting to query with GSI OwnerIdIndex")
                params = {
                    'IndexName': 'OwnerIdIndex',
                    'KeyConditionExpression': boto3.dynamodb.conditions.Key('ownerId').eq(owner_id)
                }
                response = table.query(**params)
            except Exception as e:
                logger.info(f"GSI query failed, falling back to scan: {str(e)}")
                # Fall back to scan with filter if GSI is not available
                params = {
                    'FilterExpression': boto3.dynamodb.conditions.Attr('ownerId').eq(owner_id) & 
                                        boto3.dynamodb.conditions.Attr('SK').eq('META')
                }
                response = table.scan(**params)
                
            # Process results
            spaces = response['Items']
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], **params)
                spaces.extend(response['Items'])
                
            # Transform the items to a simpler format for the response
            result = []
            for space in spaces:
                result.append({
                    'spaceId': space.get('spaceId'),
                    'name': space.get('name'),
                    'description': space.get('description'),
                    'createdAt': space.get('createdAt'),
                    'ownerId': space.get('ownerId')
                })
                
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
            
        except dynamodb_client.exceptions.ResourceNotFoundException:
            # Table doesn't exist
            logger.error(f"Table {SPACES_TABLE_NAME} not found")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f"Table {SPACES_TABLE_NAME} not found"})
            }
            
    except Exception as e:
        logger.error(f"Error listing spaces: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Could not list spaces', 'details': str(e)})
        }
