# Mind Map Explorer - Complete End-to-End Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Deployment Guide](#deployment-guide)
3. [Lambda Functions Documentation](#lambda-functions-documentation)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Logging Strategy](#logging-strategy)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
8. [Testing Guide](#testing-guide)

## Architecture Overview

The Mind Map Explorer is a serverless application built on AWS using the Serverless Framework. It consists of:

### Core Components
- **API Gateway**: RESTful API endpoints
- **Lambda Functions**: Business logic handlers (10 functions)
- **DynamoDB**: Data persistence (2 tables)
- **S3**: Content storage
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/Web    │───▶│   API Gateway   │───▶│  Lambda Funcs   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudWatch    │◀───│     X-Ray       │◀───│   DynamoDB      │
│   Logs/Metrics  │    │   Tracing       │    │   Tables        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   S3 Bucket     │
                                               │   Content       │
                                               └─────────────────┘
```

## Deployment Guide

### Prerequisites
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

### Environment Setup
```bash
# Set deployment timestamp (optional)
$env:TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"

# Deploy to development
serverless deploy --stage dev

# Deploy to production
serverless deploy --stage prod
```

### Post-Deployment Verification
```bash
# Get deployment info
serverless info --stage dev

# Test API endpoint
curl https://{api-id}.execute-api.us-east-1.amazonaws.com/dev/spaces
```

## Lambda Functions Documentation

### 1. Spaces Functions

#### spacesCreateSls
- **Purpose**: Create a new mind map space
- **Handler**: `lambda_handlers/spaces_create_handler.lambda_handler`
- **Method**: POST
- **Path**: `/spaces`
- **Input**: JSON body with space details
- **Output**: Created space with ID

**Function Flow:**
1. Validate input parameters
2. Generate unique space ID
3. Create space record in DynamoDB
4. Log operation result
5. Return space details

#### spacesListSls
- **Purpose**: List all spaces for a user
- **Handler**: `lambda_handlers/spaces_list_handler.lambda_handler`
- **Method**: GET
- **Path**: `/spaces`
- **Query Parameters**: `ownerId` (optional)
- **Output**: Array of spaces

#### spacesTreeSls
- **Purpose**: Get complete space tree with nodes
- **Handler**: `lambda_handlers/spaces_tree_handler.lambda_handler`
- **Method**: GET
- **Path**: `/spaces/{spaceId}`
- **Output**: Space with nested node structure

#### spacesUpdateSls
- **Purpose**: Update space metadata
- **Handler**: `lambda_handlers/spaces_update_handler.lambda_handler`
- **Method**: PUT
- **Path**: `/spaces/{spaceId}`
- **Input**: JSON body with updates
- **Output**: Updated space

#### spacesDeleteSls
- **Purpose**: Delete space and all associated nodes
- **Handler**: `lambda_handlers/spaces_delete_handler.lambda_handler`
- **Method**: DELETE
- **Path**: `/spaces/{spaceId}`
- **Output**: Deletion confirmation

### 2. Node Functions

#### nodesAddSls
- **Purpose**: Add a new node to a space
- **Handler**: `lambda_handlers/nodes_add_handler.lambda_handler`
- **Method**: POST
- **Path**: `/spaces/{spaceId}/nodes`
- **Input**: JSON body with node details
- **Output**: Created node with ID

#### nodesGetSls
- **Purpose**: Retrieve a specific node
- **Handler**: `lambda_handlers/nodes_get_handler.lambda_handler`
- **Method**: GET
- **Path**: `/spaces/{spaceId}/nodes/{nodeId}`
- **Output**: Node details

#### nodesUpdateSls
- **Purpose**: Update node content and metadata
- **Handler**: `lambda_handlers/nodes_update_handler.lambda_handler`
- **Method**: PUT
- **Path**: `/spaces/{spaceId}/nodes/{nodeId}`
- **Input**: JSON body with updates
- **Output**: Updated node

#### nodesDeleteSls
- **Purpose**: Delete a node and its children
- **Handler**: `lambda_handlers/nodes_delete_handler.lambda_handler`
- **Method**: DELETE
- **Path**: `/spaces/{spaceId}/nodes/{nodeId}`
- **Output**: Deletion confirmation

#### nodesReorderSls
- **Purpose**: Reorder nodes within a parent
- **Handler**: `lambda_handlers/nodes_reorder_handler.lambda_handler`
- **Method**: POST
- **Path**: `/spaces/{spaceId}/nodes/reorder`
- **Input**: Array of node IDs in new order
- **Output**: Reorder confirmation

## API Reference

### Authentication
All API endpoints expect AWS Signature Version 4 authentication or API Key authentication.

### Request/Response Format
- **Content-Type**: `application/json`
- **Character Encoding**: UTF-8
- **Date Format**: ISO 8601 (e.g., "2025-05-28T10:30:00Z")

### Error Response Format
```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "details": {
    "field": "validation details"
  },
  "timestamp": "2025-05-28T10:30:00Z",
  "requestId": "unique-request-id"
}
```

### Success Response Format
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-05-28T10:30:00Z",
  "requestId": "unique-request-id"
}
```

## Database Schema

### Spaces Table (mindmap-explorer-sls-dev-spaces)

**Primary Key**:
- PK (Hash): `SPACE#{spaceId}`
- SK (Range): `METADATA`

**Global Secondary Indexes**:
- OwnerIdIndex: `ownerId` (Hash) + `createdAt` (Range)
- SpaceIdIndex: `spaceId` (Hash)

**Attributes**:
```json
{
  "PK": "SPACE#space-uuid",
  "SK": "METADATA",
  "spaceId": "space-uuid",
  "ownerId": "user-uuid",
  "title": "My Mind Map",
  "description": "Description of the mind map",
  "createdAt": "2025-05-28T10:30:00Z",
  "updatedAt": "2025-05-28T10:30:00Z",
  "isPublic": false,
  "tags": ["tag1", "tag2"]
}
```

### Nodes Table (mindmap-explorer-sls-dev-nodes)

**Primary Key**:
- nodeId (Hash): Unique node identifier
- spaceId (Range): Space the node belongs to

**Global Secondary Indexes**:
- SpaceIdNodesIndex: `spaceId` (Hash) + `orderIndex` (Range)
- ParentNodeIdIndex: `parentNodeId` (Hash) + `orderIndex` (Range)

**Attributes**:
```json
{
  "nodeId": "node-uuid",
  "spaceId": "space-uuid",
  "parentNodeId": "parent-node-uuid",
  "title": "Node Title",
  "content": "Node content text",
  "contentType": "text",
  "contentS3Key": "spaces/space-uuid/nodes/node-uuid/content.html",
  "orderIndex": 1,
  "createdAt": "2025-05-28T10:30:00Z",
  "updatedAt": "2025-05-28T10:30:00Z",
  "metadata": {
    "color": "#FF0000",
    "icon": "📝"
  }
}
```

## Logging Strategy

### Log Levels
- **ERROR**: System errors, exceptions, failed operations
- **WARN**: Non-critical issues, validation warnings
- **INFO**: Business logic events, successful operations
- **DEBUG**: Detailed execution information (dev only)

### Log Format
```python
import logging
import json
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_api_request(event, context):
    logger.info(json.dumps({
        "event_type": "api_request",
        "method": event.get('httpMethod'),
        "path": event.get('path'),
        "request_id": context.aws_request_id,
        "function_name": context.function_name,
        "timestamp": datetime.utcnow().isoformat()
    }))

def log_api_response(status_code, response_body, context):
    logger.info(json.dumps({
        "event_type": "api_response",
        "status_code": status_code,
        "request_id": context.aws_request_id,
        "response_size": len(str(response_body)),
        "timestamp": datetime.utcnow().isoformat()
    }))
```

### CloudWatch Log Groups
Each Lambda function creates its own log group:
- `/aws/lambda/MindMapSpacesCreateSls-dev`
- `/aws/lambda/MindMapSpacesListSls-dev`
- `/aws/lambda/MindMapSpacesTreeSls-dev`
- `/aws/lambda/MindMapSpacesUpdateSls-dev`
- `/aws/lambda/MindMapSpacesDeleteSls-dev`
- `/aws/lambda/MindMapNodesAddSls-dev`
- `/aws/lambda/MindMapNodesGetSls-dev`
- `/aws/lambda/MindMapNodesUpdateSls-dev`
- `/aws/lambda/MindMapNodesDeleteSls-dev`
- `/aws/lambda/MindMapNodesReorderSls-dev`

## Monitoring & Troubleshooting

### Key Metrics to Monitor
1. **API Gateway Metrics**
   - Request count
   - Error rate (4xx, 5xx)
   - Latency (p50, p95, p99)

2. **Lambda Metrics**
   - Invocation count
   - Duration
   - Error count
   - Throttle count
   - Cold start frequency

3. **DynamoDB Metrics**
   - Read/Write capacity utilization
   - Throttled requests
   - User errors
   - System errors

4. **S3 Metrics**
   - Request count
   - Error rate
   - Transfer metrics

### Common Issues & Solutions

#### 1. Lambda Timeout
**Symptom**: Functions timing out after 30 seconds
**Solution**: 
- Check DynamoDB query efficiency
- Optimize batch operations
- Consider increasing timeout limit

#### 2. DynamoDB Throttling
**Symptom**: ThrottlingException errors
**Solution**:
- Check if queries are using proper indexes
- Consider enabling auto-scaling
- Implement exponential backoff retry

#### 3. Cold Start Latency
**Symptom**: High latency on first requests
**Solution**:
- Use provisioned concurrency for critical functions
- Optimize import statements
- Consider keeping connections warm

### Debugging Commands
```bash
# View function logs
serverless logs --function spacesCreateSls --stage dev

# Follow logs in real-time
serverless logs --function spacesCreateSls --stage dev --tail

# Invoke function locally
serverless invoke local --function spacesCreateSls --data '{"body": "{}"}'

# Get deployment information
serverless info --stage dev

# Check function configuration
aws lambda get-function --function-name MindMapSpacesCreateSls-dev
```

## Testing Guide

### Unit Testing
Located in `/tests/` directory:
- `test_spaces_api.py` - Spaces endpoint tests
- `test_nodes_api.py` - Nodes endpoint tests
- `test_complete_workflow.py` - End-to-end workflow tests

### Running Tests
```bash
# Install test dependencies
pip install pytest requests

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_complete_workflow.py -v

# Run with detailed output
python -m pytest tests/ -v -s
```

### Test Configuration
Update `tests/config.py` with your deployed API endpoint:
```python
API_BASE_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"
```

### Performance Testing
```bash
# Load test with curl
for i in {1..100}; do
  curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/spaces &
done
wait

# Monitor performance
aws logs filter-log-events --log-group-name /aws/lambda/MindMapSpacesListSls-dev --start-time $(date -d '5 minutes ago' +%s)000
```

---

For more specific documentation on individual components, see:
- [Lambda Handlers Documentation](./LAMBDA_HANDLERS_DOCUMENTATION.md)
- [Database Operations Guide](./DATABASE_OPERATIONS_GUIDE.md)
- [API Testing Guide](./API_TESTING_GUIDE.md)
