import json
import os
import uuid
import boto3
import logging
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Initialize X-Ray
patch_all()

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB and S3 clients
spaces_table_name = os.environ.get('SPACES_TABLE_NAME')
nodes_table_name = os.environ.get('NODES_TABLE_NAME')
content_bucket_name = os.environ.get('CONTENT_BUCKET_NAME')

dynamodb = boto3.resource('dynamodb')
spaces_table = dynamodb.Table(spaces_table_name)
nodes_table = dynamodb.Table(nodes_table_name)
s3 = boto3.client('s3')

def generate_id():
    """Generate a unique ID for resources"""
    return str(uuid.uuid4())

def create_response(status_code, body):
    """Create a standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    }

def create_error_response(status_code, message):
    """Create a standardized error response"""
    return create_response(status_code, {'error': message})

def get_timestamp():
    """Get current ISO format timestamp"""
    return datetime.utcnow().isoformat()

def parse_event_body(event):
    """Parse and validate the request body from API Gateway event"""
    try:
        return json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return {}
