# Lambda Handlers Documentation

## Overview
This document provides detailed documentation for all Lambda function handlers in the Mind Map Explorer application.

## Handler Structure
Each handler follows a consistent pattern:
1. **Input Validation**: Validate incoming event data
2. **Business Logic**: Execute core functionality
3. **Error Handling**: Catch and handle exceptions
4. **Logging**: Log operations and results
5. **Response Formatting**: Return standardized response

## Common Utilities

### Logging Setup
```python
import logging
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(event_type, details, context):
    """Standard logging function for all handlers"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "request_id": context.aws_request_id,
        "function_name": context.function_name,
        "details": details
    }
    logger.info(json.dumps(log_entry))
```

### Response Formatting
```python
def create_response(status_code, body, context):
    """Standard response format for all handlers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps({
            'data': body if status_code < 400 else None,
            'error': body if status_code >= 400 else None,
            'timestamp': datetime.utcnow().isoformat(),
            'requestId': context.aws_request_id
        })
    }
```

## Spaces Handlers

### spaces_create_handler.py

**Purpose**: Creates a new mind map space

**Input Event Structure**:
```json
{
  "httpMethod": "POST",
  "path": "/spaces",
  "body": "{\"title\": \"My Space\", \"description\": \"Description\", \"ownerId\": \"user-123\"}",
  "headers": { "Content-Type": "application/json" }
}
```

**Function Flow**:
```python
def lambda_handler(event, context):
    try:
        # 1. Log incoming request
        log_event("spaces_create_start", {
            "method": event.get('httpMethod'),
            "path": event.get('path')
        }, context)
        
        # 2. Parse and validate input
        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        description = body.get('description', '')
        owner_id = body.get('ownerId')
        
        if not title or not owner_id:
            log_event("spaces_create_validation_error", {
                "error": "Missing required fields"
            }, context)
            return create_response(400, {"error": "Title and ownerId are required"}, context)
        
        # 3. Generate space ID and timestamps
        space_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # 4. Create space item
        space_item = {
            'PK': f'SPACE#{space_id}',
            'SK': 'METADATA',
            'spaceId': space_id,
            'title': title,
            'description': description,
            'ownerId': owner_id,
            'createdAt': current_time,
            'updatedAt': current_time,
            'isPublic': body.get('isPublic', False),
            'tags': body.get('tags', [])
        }
        
        # 5. Save to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['SPACES_TABLE_NAME'])
        
        table.put_item(Item=space_item)
        
        # 6. Log success
        log_event("spaces_create_success", {
            "space_id": space_id,
            "owner_id": owner_id
        }, context)
        
        # 7. Return created space
        return create_response(201, space_item, context)
        
    except Exception as e:
        # 8. Log error
        log_event("spaces_create_error", {
            "error": str(e),
            "error_type": type(e).__name__
        }, context)
        
        return create_response(500, {
            "error": "Internal server error",
            "message": str(e)
        }, context)
```

**Output**:
```json
{
  "statusCode": 201,
  "body": {
    "data": {
      "spaceId": "space-uuid",
      "title": "My Space",
      "description": "Description",
      "ownerId": "user-123",
      "createdAt": "2025-05-28T10:30:00Z",
      "updatedAt": "2025-05-28T10:30:00Z"
    },
    "timestamp": "2025-05-28T10:30:00Z",
    "requestId": "request-id"
  }
}
```

### spaces_list_handler.py

**Purpose**: Lists all spaces for a user or all public spaces

**Input Event Structure**:
```json
{
  "httpMethod": "GET",
  "path": "/spaces",
  "queryStringParameters": {
    "ownerId": "user-123",
    "limit": "10",
    "offset": "0"
  }
}
```

**Function Flow**:
```python
def lambda_handler(event, context):
    try:
        # 1. Log request
        log_event("spaces_list_start", {
            "query_params": event.get('queryStringParameters', {})
        }, context)
        
        # 2. Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        owner_id = query_params.get('ownerId')
        limit = int(query_params.get('limit', 50))
        
        # 3. Query DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['SPACES_TABLE_NAME'])
        
        if owner_id:
            # Query by owner
            response = table.query(
                IndexName='OwnerIdIndex',
                KeyConditionExpression=Key('ownerId').eq(owner_id),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
        else:
            # Scan for public spaces
            response = table.scan(
                FilterExpression=Attr('isPublic').eq(True),
                Limit=limit
            )
        
        spaces = response.get('Items', [])
        
        # 4. Log results
        log_event("spaces_list_success", {
            "spaces_count": len(spaces),
            "owner_id": owner_id
        }, context)
        
        # 5. Return spaces
        return create_response(200, {
            "spaces": spaces,
            "count": len(spaces)
        }, context)
        
    except Exception as e:
        log_event("spaces_list_error", {
            "error": str(e)
        }, context)
        
        return create_response(500, {
            "error": "Failed to list spaces"
        }, context)
```

### spaces_tree_handler.py

**Purpose**: Retrieves a space with its complete node hierarchy

**Input Event Structure**:
```json
{
  "httpMethod": "GET",
  "path": "/spaces/space-uuid",
  "pathParameters": {
    "spaceId": "space-uuid"
  }
}
```

**Function Flow**:
```python
def lambda_handler(event, context):
    try:
        # 1. Log request
        space_id = event['pathParameters']['spaceId']
        log_event("spaces_tree_start", {"space_id": space_id}, context)
        
        # 2. Get space metadata
        dynamodb = boto3.resource('dynamodb')
        spaces_table = dynamodb.Table(os.environ['SPACES_TABLE_NAME'])
        nodes_table = dynamodb.Table(os.environ['NODES_TABLE_NAME'])
        
        # Get space
        space_response = spaces_table.get_item(
            Key={'PK': f'SPACE#{space_id}', 'SK': 'METADATA'}
        )
        
        if 'Item' not in space_response:
            log_event("spaces_tree_not_found", {"space_id": space_id}, context)
            return create_response(404, {"error": "Space not found"}, context)
        
        space = space_response['Item']
        
        # 3. Get all nodes for the space
        nodes_response = nodes_table.query(
            IndexName='SpaceIdNodesIndex',
            KeyConditionExpression=Key('spaceId').eq(space_id)
        )
        
        nodes = nodes_response.get('Items', [])
        
        # 4. Build node hierarchy
        def build_tree(parent_id=None):
            children = []
            for node in nodes:
                if node.get('parentNodeId') == parent_id:
                    node['children'] = build_tree(node['nodeId'])
                    children.append(node)
            return sorted(children, key=lambda x: x.get('orderIndex', 0))
        
        # 5. Attach root nodes to space
        space['nodes'] = build_tree()
        
        log_event("spaces_tree_success", {
            "space_id": space_id,
            "nodes_count": len(nodes)
        }, context)
        
        return create_response(200, space, context)
        
    except Exception as e:
        log_event("spaces_tree_error", {
            "space_id": space_id,
            "error": str(e)
        }, context)
        
        return create_response(500, {"error": "Failed to get space tree"}, context)
```

## Node Handlers

### nodes_add_handler.py

**Purpose**: Adds a new node to a space

**Input Event Structure**:
```json
{
  "httpMethod": "POST",
  "path": "/spaces/space-uuid/nodes",
  "pathParameters": {
    "spaceId": "space-uuid"
  },
  "body": "{\"title\": \"New Node\", \"content\": \"Node content\", \"parentNodeId\": \"parent-uuid\"}"
}
```

**Function Flow**:
```python
def lambda_handler(event, context):
    try:
        # 1. Log request
        space_id = event['pathParameters']['spaceId']
        log_event("nodes_add_start", {"space_id": space_id}, context)
        
        # 2. Parse input
        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        content = body.get('content', '')
        parent_node_id = body.get('parentNodeId')
        
        if not title:
            return create_response(400, {"error": "Title is required"}, context)
        
        # 3. Generate node data
        node_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # 4. Calculate order index
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['NODES_TABLE_NAME'])
        
        # Get highest order index for siblings
        if parent_node_id:
            response = table.query(
                IndexName='ParentNodeIdIndex',
                KeyConditionExpression=Key('parentNodeId').eq(parent_node_id),
                ScanIndexForward=False,
                Limit=1
            )
        else:
            response = table.query(
                IndexName='SpaceIdNodesIndex',
                KeyConditionExpression=Key('spaceId').eq(space_id),
                FilterExpression=Attr('parentNodeId').not_exists(),
                ScanIndexForward=False,
                Limit=1
            )
        
        next_order = 1
        if response['Items']:
            next_order = response['Items'][0].get('orderIndex', 0) + 1
        
        # 5. Create node item
        node_item = {
            'nodeId': node_id,
            'spaceId': space_id,
            'title': title,
            'content': content,
            'contentType': body.get('contentType', 'text'),
            'orderIndex': next_order,
            'createdAt': current_time,
            'updatedAt': current_time
        }
        
        if parent_node_id:
            node_item['parentNodeId'] = parent_node_id
        
        # 6. Save to DynamoDB
        table.put_item(Item=node_item)
        
        # 7. Store content in S3 if large
        if len(content) > 1000:  # Store large content in S3
            s3_key = f"spaces/{space_id}/nodes/{node_id}/content.txt"
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=os.environ['CONTENT_BUCKET_NAME'],
                Key=s3_key,
                Body=content,
                ContentType='text/plain'
            )
            node_item['contentS3Key'] = s3_key
            node_item['content'] = f"[Content stored in S3: {s3_key}]"
        
        log_event("nodes_add_success", {
            "node_id": node_id,
            "space_id": space_id,
            "parent_node_id": parent_node_id
        }, context)
        
        return create_response(201, node_item, context)
        
    except Exception as e:
        log_event("nodes_add_error", {
            "space_id": space_id,
            "error": str(e)
        }, context)
        
        return create_response(500, {"error": "Failed to add node"}, context)
```

### nodes_update_handler.py

**Purpose**: Updates an existing node

**Input Event Structure**:
```json
{
  "httpMethod": "PUT",
  "path": "/spaces/space-uuid/nodes/node-uuid",
  "pathParameters": {
    "spaceId": "space-uuid",
    "nodeId": "node-uuid"
  },
  "body": "{\"title\": \"Updated Title\", \"content\": \"Updated content\"}"
}
```

**Function Flow**:
```python
def lambda_handler(event, context):
    try:
        # 1. Log request
        space_id = event['pathParameters']['spaceId']
        node_id = event['pathParameters']['nodeId']
        
        log_event("nodes_update_start", {
            "space_id": space_id,
            "node_id": node_id
        }, context)
        
        # 2. Parse updates
        body = json.loads(event.get('body', '{}'))
        
        # 3. Build update expression
        update_expression = "SET updatedAt = :updated_at"
        expression_values = {
            ':updated_at': datetime.utcnow().isoformat()
        }
        
        if 'title' in body:
            update_expression += ", title = :title"
            expression_values[':title'] = body['title']
        
        if 'content' in body:
            update_expression += ", content = :content"
            expression_values[':content'] = body['content']
        
        if 'metadata' in body:
            update_expression += ", metadata = :metadata"
            expression_values[':metadata'] = body['metadata']
        
        # 4. Update in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['NODES_TABLE_NAME'])
        
        response = table.update_item(
            Key={'nodeId': node_id, 'spaceId': space_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_node = response.get('Attributes')
        
        log_event("nodes_update_success", {
            "node_id": node_id,
            "space_id": space_id,
            "updated_fields": list(body.keys())
        }, context)
        
        return create_response(200, updated_node, context)
        
    except Exception as e:
        log_event("nodes_update_error", {
            "node_id": node_id,
            "space_id": space_id,
            "error": str(e)
        }, context)
        
        return create_response(500, {"error": "Failed to update node"}, context)
```

## Error Handling Patterns

### Input Validation
```python
def validate_required_fields(body, required_fields):
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in body or not body[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
```

### DynamoDB Error Handling
```python
def handle_dynamodb_error(error, context):
    """Handle common DynamoDB errors"""
    error_code = error.response['Error']['Code']
    
    if error_code == 'ConditionalCheckFailedException':
        log_event("dynamodb_conditional_check_failed", {
            "error_code": error_code
        }, context)
        return create_response(409, {"error": "Resource already exists or condition not met"}, context)
    
    elif error_code == 'ResourceNotFoundException':
        log_event("dynamodb_resource_not_found", {
            "error_code": error_code
        }, context)
        return create_response(404, {"error": "Resource not found"}, context)
    
    else:
        log_event("dynamodb_error", {
            "error_code": error_code,
            "error_message": str(error)
        }, context)
        return create_response(500, {"error": "Database error"}, context)
```

## Performance Optimization

### Connection Reuse
```python
# Initialize outside handler for connection reuse
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Use pre-initialized clients
    table = dynamodb.Table(os.environ['SPACES_TABLE_NAME'])
    # ... rest of handler
```

### Batch Operations
```python
def batch_get_nodes(node_ids, table):
    """Get multiple nodes in a single batch request"""
    with table.batch_reader() as batch:
        for node_id in node_ids:
            batch.get_item(Key={'nodeId': node_id})
    
    return [item for item in batch]
```

### Caching Strategy
```python
import functools
import time

@functools.lru_cache(maxsize=100)
def get_cached_space(space_id, ttl_hash=None):
    """Cache space metadata with TTL"""
    # Implementation here
    pass

def get_ttl_hash(seconds=300):
    """Generate TTL hash for cache invalidation"""
    return round(time.time() / seconds)
```

---

This documentation provides comprehensive coverage of all Lambda handlers with detailed logging, error handling, and performance considerations.
