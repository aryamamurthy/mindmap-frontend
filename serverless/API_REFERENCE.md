# Complete API Reference and Functional Documentation

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Spaces Endpoints](#spaces-endpoints)
4. [Nodes Endpoints](#nodes-endpoints)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Response Formats](#response-formats)
8. [Testing Guide](#testing-guide)
9. [Integration Examples](#integration-examples)

## API Overview

### Base Information
- **Base URL**: `https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev`
- **Protocol**: HTTPS
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins
- **Authentication**: Currently using anonymous access (development mode)

### Service Architecture
The Mind Map API is built using serverless architecture on AWS:
- **API Gateway**: HTTP API routing
- **Lambda Functions**: 10 serverless functions
- **DynamoDB**: NoSQL database with GSI indexes
- **S3**: Content storage for HTML and media
- **EventBridge**: Event-driven content generation
- **X-Ray**: Distributed tracing

## Authentication

### Current Implementation
```http
Authorization: Bearer <token>
```

**Note**: Currently in development mode using anonymous access. Production implementation should use:
- AWS Cognito User Pools
- JWT token validation
- Role-based access control (RBAC)

### User Context
User identification is extracted from the request context:
```javascript
// Lambda context extraction
const userId = event?.requestContext?.authorizer?.claims?.sub || 'ANONYMOUS_USER';
```

## Spaces Endpoints

### 1. Create Space
Create a new mind map space.

**Endpoint**: `POST /spaces`

**Request Body**:
```json
{
  "name": "My Mind Map",
  "description": "A comprehensive mind map for project planning"
}
```

**Response** (201 Created):
```json
{
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Mind Map",
  "description": "A comprehensive mind map for project planning",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "ownerId": "ANONYMOUS_USER"
}
```

**Headers**:
- `Location: /spaces/{spaceId}`
- `Content-Type: application/json`

**Lambda Function**: `spaces_create_handler.lambda_handler`

### 2. List Spaces
Retrieve all spaces for the authenticated user.

**Endpoint**: `GET /spaces`

**Query Parameters**:
- `limit` (optional): Maximum number of spaces to return (default: 50)
- `lastEvaluatedKey` (optional): Pagination token

**Response** (200 OK):
```json
{
  "spaces": [
    {
      "spaceId": "123e4567-e89b-12d3-a456-426614174000",
      "name": "My Mind Map",
      "description": "A comprehensive mind map for project planning",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "updatedAt": "2024-01-15T10:30:00.000Z",
      "ownerId": "user-123"
    }
  ],
  "lastEvaluatedKey": "eyJQSyI6IlNQQUNFIzEyM...",
  "count": 1
}
```

**Lambda Function**: `spaces_list_handler.lambda_handler`

### 3. Get Space Tree
Retrieve a complete space with all its nodes in hierarchical structure.

**Endpoint**: `GET /spaces/{spaceId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space

**Response** (200 OK):
```json
{
  "space": {
    "spaceId": "123e4567-e89b-12d3-a456-426614174000",
    "name": "My Mind Map",
    "description": "A comprehensive mind map for project planning",
    "createdAt": "2024-01-15T10:30:00.000Z",
    "updatedAt": "2024-01-15T10:30:00.000Z",
    "ownerId": "user-123"
  },
  "nodes": [
    {
      "nodeId": "node-123",
      "spaceId": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Main Topic",
      "contentHTML": "<p>This is the main topic content</p>",
      "parentNodeId": null,
      "orderIndex": 0,
      "level": 0,
      "createdAt": "2024-01-15T10:35:00.000Z",
      "children": [
        {
          "nodeId": "node-456",
          "title": "Subtopic 1",
          "parentNodeId": "node-123",
          "orderIndex": 0,
          "level": 1,
          "children": []
        }
      ]
    }
  ]
}
```

**Lambda Function**: `spaces_tree_handler.lambda_handler`

### 4. Update Space
Update space metadata (name, description).

**Endpoint**: `PUT /spaces/{spaceId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space

**Request Body**:
```json
{
  "name": "Updated Mind Map Name",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Mind Map Name",
  "description": "Updated description",
  "updatedAt": "2024-01-15T11:00:00.000Z"
}
```

**Lambda Function**: `spaces_update_handler.lambda_handler`

### 5. Delete Space
Delete a space and all its associated nodes.

**Endpoint**: `DELETE /spaces/{spaceId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space

**Response** (200 OK):
```json
{
  "message": "Space deleted successfully",
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "deletedNodes": 5
}
```

**Lambda Function**: `spaces_delete_handler.lambda_handler`

## Nodes Endpoints

### 1. Add Node
Create a new node within a space.

**Endpoint**: `POST /spaces/{spaceId}/nodes`

**Path Parameters**:
- `spaceId`: Unique identifier of the space

**Request Body**:
```json
{
  "title": "New Node Title",
  "contentHTML": "<p>Node content in HTML format</p>",
  "parentNodeId": "parent-node-123",
  "orderIndex": 2,
  "generateContent": true
}
```

**Optional Parameters**:
- `parentNodeId`: If null, creates a root node
- `orderIndex`: Position among siblings (auto-calculated if not provided)
- `generateContent`: Trigger AI content generation

**Response** (201 Created):
```json
{
  "nodeId": "node-789",
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "title": "New Node Title",
  "contentHTML": "<p>Node content in HTML format</p>",
  "parentNodeId": "parent-node-123",
  "orderIndex": 2,
  "level": 1,
  "createdAt": "2024-01-15T10:45:00.000Z",
  "contentGenerationTriggered": true
}
```

**Lambda Function**: `nodes_add_handler.lambda_handler`

### 2. Get Node
Retrieve a specific node with its details.

**Endpoint**: `GET /spaces/{spaceId}/nodes/{nodeId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space
- `nodeId`: Unique identifier of the node

**Response** (200 OK):
```json
{
  "nodeId": "node-789",
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Node Title",
  "contentHTML": "<p>Node content in HTML format</p>",
  "parentNodeId": "parent-node-123",
  "orderIndex": 2,
  "level": 1,
  "createdAt": "2024-01-15T10:45:00.000Z",
  "updatedAt": "2024-01-15T10:45:00.000Z",
  "contentS3Key": "content/node-789.html"
}
```

**Lambda Function**: `nodes_get_handler.lambda_handler`

### 3. Update Node
Update node properties including title and content.

**Endpoint**: `PUT /spaces/{spaceId}/nodes/{nodeId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space
- `nodeId`: Unique identifier of the node

**Request Body**:
```json
{
  "title": "Updated Node Title",
  "contentHTML": "<p>Updated node content</p>",
  "generateContent": false
}
```

**Response** (200 OK):
```json
{
  "nodeId": "node-789",
  "spaceId": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Updated Node Title",
  "contentHTML": "<p>Updated node content</p>",
  "updatedAt": "2024-01-15T11:15:00.000Z"
}
```

**Lambda Function**: `nodes_update_handler.lambda_handler`

### 4. Delete Node
Delete a node and optionally its children.

**Endpoint**: `DELETE /spaces/{spaceId}/nodes/{nodeId}`

**Path Parameters**:
- `spaceId`: Unique identifier of the space
- `nodeId`: Unique identifier of the node

**Query Parameters**:
- `deleteChildren` (optional): `true` to delete all child nodes, `false` to promote children (default: `false`)

**Response** (200 OK):
```json
{
  "message": "Node deleted successfully",
  "nodeId": "node-789",
  "deletedNodes": 1,
  "promotedNodes": 2
}
```

**Lambda Function**: `nodes_delete_handler.lambda_handler`

### 5. Reorder Nodes
Change the order of nodes within the same parent.

**Endpoint**: `POST /spaces/{spaceId}/nodes/reorder`

**Path Parameters**:
- `spaceId`: Unique identifier of the space

**Request Body**:
```json
{
  "parentNodeId": "parent-node-123",
  "nodeOrder": [
    {
      "nodeId": "node-456",
      "orderIndex": 0
    },
    {
      "nodeId": "node-789",
      "orderIndex": 1
    },
    {
      "nodeId": "node-101",
      "orderIndex": 2
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Nodes reordered successfully",
  "updatedNodes": 3,
  "parentNodeId": "parent-node-123"
}
```

**Lambda Function**: `nodes_reorder_handler.lambda_handler`

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error message description",
  "details": "Detailed error information",
  "requestId": "abc123-def456-ghi789",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 200 | OK | Successful GET, PUT, DELETE operations |
| 201 | Created | Successful POST operations |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists or conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary service issues |

### Common Error Scenarios

#### 1. Validation Errors (400)
```json
{
  "error": "Validation failed",
  "details": "Missing required field: name",
  "field": "name",
  "requestId": "abc123"
}
```

#### 2. Resource Not Found (404)
```json
{
  "error": "Space not found",
  "details": "Space with ID 'invalid-id' does not exist",
  "spaceId": "invalid-id",
  "requestId": "abc123"
}
```

#### 3. Database Errors (500)
```json
{
  "error": "Database operation failed",
  "details": "DynamoDB table temporarily unavailable",
  "requestId": "abc123"
}
```

## Rate Limiting

### API Gateway Throttling
- **Burst Limit**: 5000 requests per second
- **Rate Limit**: 2000 requests per second
- **Per-Key Limit**: 100 requests per second per API key

### Lambda Concurrency
- **Reserved Concurrency**: 100 per function
- **Account Limit**: 1000 concurrent executions

### DynamoDB Limits
- **On-Demand Mode**: Automatic scaling
- **Read Capacity**: Scales based on demand
- **Write Capacity**: Scales based on demand

## Response Formats

### Success Response Structure
```json
{
  "data": {
    // Response data
  },
  "metadata": {
    "requestId": "abc123",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "version": "1.0"
  }
}
```

### Pagination Response
```json
{
  "items": [...],
  "pagination": {
    "lastEvaluatedKey": "eyJQSyI6...",
    "hasMore": true,
    "count": 25,
    "scannedCount": 25
  }
}
```

### Headers
All responses include standard headers:
```http
Content-Type: application/json
X-Request-ID: abc123-def456-ghi789
X-API-Version: 1.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

## Testing Guide

### Prerequisites
```bash
# Install dependencies
pip install requests pytest boto3

# Set environment variables
export API_BASE_URL="https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev"
export API_KEY="your-api-key"  # If authentication is enabled
```

### Basic API Testing

#### 1. Create and Test Space
```python
import requests
import json

base_url = "https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev"

# Create space
space_data = {
    "name": "Test Space",
    "description": "API testing space"
}

response = requests.post(f"{base_url}/spaces", json=space_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

space_id = response.json()["spaceId"]

# Get space tree
response = requests.get(f"{base_url}/spaces/{space_id}")
print(f"Space Tree: {response.json()}")
```

#### 2. Create and Test Nodes
```python
# Create root node
node_data = {
    "title": "Root Node",
    "contentHTML": "<p>Root node content</p>",
    "parentNodeId": None,
    "generateContent": True
}

response = requests.post(f"{base_url}/spaces/{space_id}/nodes", json=node_data)
root_node = response.json()
root_node_id = root_node["nodeId"]

# Create child node
child_data = {
    "title": "Child Node",
    "contentHTML": "<p>Child node content</p>",
    "parentNodeId": root_node_id
}

response = requests.post(f"{base_url}/spaces/{space_id}/nodes", json=child_data)
child_node = response.json()
```

### Automated Test Suite
```python
import pytest
import requests
import uuid

class TestMindMapAPI:
    def setup_class(self):
        self.base_url = "https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev"
        self.test_space_id = None
        self.test_node_id = None
    
    def test_create_space(self):
        data = {
            "name": f"Test Space {uuid.uuid4()}",
            "description": "Automated test space"
        }
        response = requests.post(f"{self.base_url}/spaces", json=data)
        assert response.status_code == 201
        assert "spaceId" in response.json()
        self.test_space_id = response.json()["spaceId"]
    
    def test_list_spaces(self):
        response = requests.get(f"{self.base_url}/spaces")
        assert response.status_code == 200
        assert "spaces" in response.json()
    
    def test_get_space_tree(self):
        response = requests.get(f"{self.base_url}/spaces/{self.test_space_id}")
        assert response.status_code == 200
        assert "space" in response.json()
        assert "nodes" in response.json()
    
    def test_create_node(self):
        data = {
            "title": "Test Node",
            "contentHTML": "<p>Test content</p>"
        }
        response = requests.post(f"{self.base_url}/spaces/{self.test_space_id}/nodes", json=data)
        assert response.status_code == 201
        assert "nodeId" in response.json()
        self.test_node_id = response.json()["nodeId"]
    
    def test_update_node(self):
        data = {
            "title": "Updated Test Node",
            "contentHTML": "<p>Updated content</p>"
        }
        response = requests.put(f"{self.base_url}/spaces/{self.test_space_id}/nodes/{self.test_node_id}", json=data)
        assert response.status_code == 200
    
    def test_delete_node(self):
        response = requests.delete(f"{self.base_url}/spaces/{self.test_space_id}/nodes/{self.test_node_id}")
        assert response.status_code == 200
    
    def test_delete_space(self):
        response = requests.delete(f"{self.base_url}/spaces/{self.test_space_id}")
        assert response.status_code == 200
```

## Integration Examples

### Frontend JavaScript Integration
```javascript
class MindMapAPI {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async request(method, endpoint, data = null) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.apiKey) {
            headers['Authorization'] = `Bearer ${this.apiKey}`;
        }
        
        const config = {
            method,
            headers,
            body: data ? JSON.stringify(data) : null
        };
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, config);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    // Space operations
    async createSpace(name, description) {
        return await this.request('POST', '/spaces', { name, description });
    }
    
    async getSpaces() {
        return await this.request('GET', '/spaces');
    }
    
    async getSpace(spaceId) {
        return await this.request('GET', `/spaces/${spaceId}`);
    }
    
    async updateSpace(spaceId, updates) {
        return await this.request('PUT', `/spaces/${spaceId}`, updates);
    }
    
    async deleteSpace(spaceId) {
        return await this.request('DELETE', `/spaces/${spaceId}`);
    }
    
    // Node operations
    async createNode(spaceId, nodeData) {
        return await this.request('POST', `/spaces/${spaceId}/nodes`, nodeData);
    }
    
    async getNode(spaceId, nodeId) {
        return await this.request('GET', `/spaces/${spaceId}/nodes/${nodeId}`);
    }
    
    async updateNode(spaceId, nodeId, updates) {
        return await this.request('PUT', `/spaces/${spaceId}/nodes/${nodeId}`, updates);
    }
    
    async deleteNode(spaceId, nodeId, deleteChildren = false) {
        return await this.request('DELETE', `/spaces/${spaceId}/nodes/${nodeId}?deleteChildren=${deleteChildren}`);
    }
    
    async reorderNodes(spaceId, parentNodeId, nodeOrder) {
        return await this.request('POST', `/spaces/${spaceId}/nodes/reorder`, {
            parentNodeId,
            nodeOrder
        });
    }
}

// Usage example
const api = new MindMapAPI('https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev');

async function createMindMap() {
    try {
        // Create a new space
        const space = await api.createSpace('My Project', 'Project planning mind map');
        console.log('Created space:', space);
        
        // Create root node
        const rootNode = await api.createNode(space.spaceId, {
            title: 'Project Overview',
            contentHTML: '<p>Main project goals and objectives</p>',
            generateContent: true
        });
        
        // Create child nodes
        const tasks = ['Planning', 'Development', 'Testing', 'Deployment'];
        for (const task of tasks) {
            await api.createNode(space.spaceId, {
                title: task,
                contentHTML: `<p>${task} phase details</p>`,
                parentNodeId: rootNode.nodeId
            });
        }
        
        // Get complete space tree
        const spaceTree = await api.getSpace(space.spaceId);
        console.log('Complete mind map:', spaceTree);
        
    } catch (error) {
        console.error('Error creating mind map:', error);
    }
}
```

### Python SDK Integration
```python
import requests
import json
from typing import Optional, Dict, List

class MindMapClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # Space operations
    def create_space(self, name: str, description: str = "") -> Dict:
        return self._request('POST', '/spaces', json={'name': name, 'description': description})
    
    def list_spaces(self, limit: Optional[int] = None) -> Dict:
        params = {'limit': limit} if limit else {}
        return self._request('GET', '/spaces', params=params)
    
    def get_space(self, space_id: str) -> Dict:
        return self._request('GET', f'/spaces/{space_id}')
    
    def update_space(self, space_id: str, **updates) -> Dict:
        return self._request('PUT', f'/spaces/{space_id}', json=updates)
    
    def delete_space(self, space_id: str) -> Dict:
        return self._request('DELETE', f'/spaces/{space_id}')
    
    # Node operations
    def create_node(self, space_id: str, title: str, content_html: str = "", 
                   parent_node_id: Optional[str] = None, generate_content: bool = False) -> Dict:
        data = {
            'title': title,
            'contentHTML': content_html,
            'generateContent': generate_content
        }
        if parent_node_id:
            data['parentNodeId'] = parent_node_id
        
        return self._request('POST', f'/spaces/{space_id}/nodes', json=data)
    
    def get_node(self, space_id: str, node_id: str) -> Dict:
        return self._request('GET', f'/spaces/{space_id}/nodes/{node_id}')
    
    def update_node(self, space_id: str, node_id: str, **updates) -> Dict:
        return self._request('PUT', f'/spaces/{space_id}/nodes/{node_id}', json=updates)
    
    def delete_node(self, space_id: str, node_id: str, delete_children: bool = False) -> Dict:
        params = {'deleteChildren': 'true' if delete_children else 'false'}
        return self._request('DELETE', f'/spaces/{space_id}/nodes/{node_id}', params=params)
    
    def reorder_nodes(self, space_id: str, parent_node_id: str, node_order: List[Dict]) -> Dict:
        data = {
            'parentNodeId': parent_node_id,
            'nodeOrder': node_order
        }
        return self._request('POST', f'/spaces/{space_id}/nodes/reorder', json=data)

# Usage example
client = MindMapClient('https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev')

# Create a complete mind map
space = client.create_space('API Documentation', 'Documentation for the Mind Map API')
root_node = client.create_node(space['spaceId'], 'API Overview', '<p>Complete API documentation</p>')

sections = ['Authentication', 'Endpoints', 'Examples', 'Testing']
for section in sections:
    client.create_node(space['spaceId'], section, f'<p>{section} information</p>', root_node['nodeId'])

# Get the complete structure
mind_map = client.get_space(space['spaceId'])
print(json.dumps(mind_map, indent=2))
```

This comprehensive API reference provides everything needed to integrate with and use the Mind Map serverless application effectively.
