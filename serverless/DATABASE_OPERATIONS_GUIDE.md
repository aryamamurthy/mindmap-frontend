# Database Operations Guide

## Overview
This guide covers all database operations for the Mind Map Explorer application, including DynamoDB table design, query patterns, indexing strategies, and operational procedures.

## Table of Contents
1. [Table Schemas](#table-schemas)
2. [Query Patterns](#query-patterns)
3. [Index Usage](#index-usage)
4. [Data Access Patterns](#data-access-patterns)
5. [Performance Optimization](#performance-optimization)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Backup & Recovery](#backup--recovery)

## Table Schemas

### Spaces Table: `mindmap-explorer-sls-{stage}-spaces`

#### Primary Key Structure
- **Partition Key (PK)**: `SPACE#{spaceId}` - Enables direct space lookups
- **Sort Key (SK)**: `METADATA` - Allows future expansion for space-related data

#### Global Secondary Indexes

##### OwnerIdIndex
- **Purpose**: List spaces by owner
- **Partition Key**: `ownerId`
- **Sort Key**: `createdAt`
- **Projection**: ALL
- **Use Case**: User dashboard, space listing

##### SpaceIdIndex  
- **Purpose**: Direct space access by ID
- **Partition Key**: `spaceId`
- **Sort Key**: None
- **Projection**: ALL
- **Use Case**: Space validation, quick lookups

#### Attribute Schema
```json
{
  "PK": "SPACE#550e8400-e29b-41d4-a716-446655440000",
  "SK": "METADATA",
  "spaceId": "550e8400-e29b-41d4-a716-446655440000",
  "ownerId": "user-123",
  "title": "My Mind Map",
  "description": "A comprehensive mind map for project planning",
  "createdAt": "2025-05-28T10:30:00.000Z",
  "updatedAt": "2025-05-28T15:45:30.000Z",
  "isPublic": false,
  "tags": ["project", "planning", "ideas"],
  "settings": {
    "theme": "dark",
    "autoSave": true,
    "collaborationEnabled": false
  },
  "stats": {
    "nodeCount": 25,
    "lastAccessed": "2025-05-28T15:45:30.000Z"
  }
}
```

### Nodes Table: `mindmap-explorer-sls-{stage}-nodes`

#### Primary Key Structure
- **Partition Key**: `nodeId` - Unique node identifier
- **Sort Key**: `spaceId` - Groups nodes by space

#### Global Secondary Indexes

##### SpaceIdNodesIndex
- **Purpose**: List all nodes in a space
- **Partition Key**: `spaceId`
- **Sort Key**: `orderIndex`
- **Projection**: ALL
- **Use Case**: Space tree construction, node ordering

##### ParentNodeIdIndex
- **Purpose**: List child nodes of a parent
- **Partition Key**: `parentNodeId`
- **Sort Key**: `orderIndex`
- **Projection**: ALL
- **Use Case**: Hierarchical tree building, node reordering

#### Attribute Schema
```json
{
  "nodeId": "node-123",
  "spaceId": "550e8400-e29b-41d4-a716-446655440000",
  "parentNodeId": "parent-node-456",
  "title": "Main Idea",
  "content": "Detailed description of the main concept...",
  "contentType": "text",
  "contentS3Key": "spaces/550e8400.../nodes/node-123/content.html",
  "orderIndex": 1,
  "createdAt": "2025-05-28T10:30:00.000Z",
  "updatedAt": "2025-05-28T15:45:30.000Z",
  "metadata": {
    "color": "#FF6B6B",
    "icon": "💡",
    "position": {"x": 100, "y": 200},
    "collapsed": false
  },
  "stats": {
    "viewCount": 15,
    "editCount": 3,
    "lastViewed": "2025-05-28T15:45:30.000Z"
  }
}
```

## Query Patterns

### 1. Space Operations

#### Create Space
```python
def create_space(space_data):
    """Create a new space"""
    item = {
        'PK': f'SPACE#{space_data["spaceId"]}',
        'SK': 'METADATA',
        'spaceId': space_data['spaceId'],
        'ownerId': space_data['ownerId'],
        'title': space_data['title'],
        'description': space_data.get('description', ''),
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat(),
        'isPublic': space_data.get('isPublic', False),
        'tags': space_data.get('tags', [])
    }
    
    table.put_item(
        Item=item,
        ConditionExpression='attribute_not_exists(PK)'  # Prevent overwrites
    )
    return item
```

#### Get Space by ID
```python
def get_space(space_id):
    """Get space by ID"""
    response = table.get_item(
        Key={
            'PK': f'SPACE#{space_id}',
            'SK': 'METADATA'
        },
        ConsistentRead=False  # Eventually consistent for better performance
    )
    return response.get('Item')
```

#### List Spaces by Owner
```python
def list_spaces_by_owner(owner_id, limit=50, last_key=None):
    """List spaces owned by a user"""
    query_params = {
        'IndexName': 'OwnerIdIndex',
        'KeyConditionExpression': Key('ownerId').eq(owner_id),
        'Limit': limit,
        'ScanIndexForward': False  # Most recent first
    }
    
    if last_key:
        query_params['ExclusiveStartKey'] = last_key
    
    response = table.query(**query_params)
    return {
        'spaces': response.get('Items', []),
        'lastKey': response.get('LastEvaluatedKey')
    }
```

#### Update Space
```python
def update_space(space_id, updates):
    """Update space attributes"""
    # Build update expression dynamically
    update_expr = ["updatedAt = :updated_at"]
    expr_values = {':updated_at': datetime.utcnow().isoformat()}
    
    for field, value in updates.items():
        if field in ['title', 'description', 'isPublic', 'tags', 'settings']:
            update_expr.append(f"{field} = :{field}")
            expr_values[f":{field}"] = value
    
    response = table.update_item(
        Key={'PK': f'SPACE#{space_id}', 'SK': 'METADATA'},
        UpdateExpression=f"SET {', '.join(update_expr)}",
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    return response.get('Attributes')
```

### 2. Node Operations

#### Add Node
```python
def add_node(space_id, node_data):
    """Add a new node to a space"""
    # Calculate next order index
    next_order = get_next_order_index(space_id, node_data.get('parentNodeId'))
    
    item = {
        'nodeId': node_data['nodeId'],
        'spaceId': space_id,
        'title': node_data['title'],
        'content': node_data.get('content', ''),
        'contentType': node_data.get('contentType', 'text'),
        'orderIndex': next_order,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    if 'parentNodeId' in node_data:
        item['parentNodeId'] = node_data['parentNodeId']
    
    if 'metadata' in node_data:
        item['metadata'] = node_data['metadata']
    
    table.put_item(Item=item)
    return item

def get_next_order_index(space_id, parent_node_id=None):
    """Calculate the next order index for a node"""
    if parent_node_id:
        # Query children of parent
        response = table.query(
            IndexName='ParentNodeIdIndex',
            KeyConditionExpression=Key('parentNodeId').eq(parent_node_id),
            ScanIndexForward=False,  # Descending order
            Limit=1
        )
    else:
        # Query root nodes in space
        response = table.query(
            IndexName='SpaceIdNodesIndex',
            KeyConditionExpression=Key('spaceId').eq(space_id),
            FilterExpression=Attr('parentNodeId').not_exists(),
            ScanIndexForward=False,
            Limit=1
        )
    
    if response['Items']:
        return response['Items'][0]['orderIndex'] + 1
    return 1
```

#### Get Space Tree
```python
def get_space_tree(space_id):
    """Get complete space with node hierarchy"""
    # Get space metadata
    space = get_space(space_id)
    if not space:
        return None
    
    # Get all nodes in space
    response = table.query(
        IndexName='SpaceIdNodesIndex',
        KeyConditionExpression=Key('spaceId').eq(space_id)
    )
    
    nodes = response.get('Items', [])
    
    # Build tree structure
    node_map = {node['nodeId']: node for node in nodes}
    
    def build_children(parent_id):
        children = []
        for node in nodes:
            if node.get('parentNodeId') == parent_id:
                node['children'] = build_children(node['nodeId'])
                children.append(node)
        return sorted(children, key=lambda x: x.get('orderIndex', 0))
    
    # Build root level
    space['nodes'] = build_children(None)
    return space
```

#### Reorder Nodes
```python
def reorder_nodes(space_id, parent_node_id, node_order):
    """Reorder nodes within a parent"""
    # Use batch write for atomic updates
    with table.batch_writer() as batch:
        for index, node_id in enumerate(node_order):
            batch.update_item(
                Key={'nodeId': node_id, 'spaceId': space_id},
                UpdateExpression='SET orderIndex = :order, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':order': index + 1,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
```

#### Delete Node and Children
```python
def delete_node_recursive(space_id, node_id):
    """Delete a node and all its children"""
    # Get all children recursively
    def get_all_children(parent_id):
        response = table.query(
            IndexName='ParentNodeIdIndex',
            KeyConditionExpression=Key('parentNodeId').eq(parent_id)
        )
        
        children = response.get('Items', [])
        all_children = children.copy()
        
        for child in children:
            all_children.extend(get_all_children(child['nodeId']))
        
        return all_children
    
    # Get all nodes to delete
    children = get_all_children(node_id)
    nodes_to_delete = [node_id] + [child['nodeId'] for child in children]
    
    # Batch delete
    with table.batch_writer() as batch:
        for node_to_delete in nodes_to_delete:
            batch.delete_item(
                Key={'nodeId': node_to_delete, 'spaceId': space_id}
            )
```

## Index Usage Guidelines

### When to Use Each Index

#### OwnerIdIndex
- **Use for**: User dashboards, space listings
- **Query pattern**: `ownerId = :owner AND createdAt BETWEEN :start AND :end`
- **Benefits**: Sorted by creation time, supports pagination
- **Cost**: Additional storage and write capacity

#### SpaceIdIndex
- **Use for**: Quick space validation, existence checks
- **Query pattern**: `spaceId = :space_id`
- **Benefits**: Fast single-item lookups
- **Cost**: Minimal additional storage

#### SpaceIdNodesIndex
- **Use for**: Getting all nodes in a space, tree construction
- **Query pattern**: `spaceId = :space_id`
- **Benefits**: Ordered by orderIndex, complete space view
- **Cost**: Higher storage due to full projection

#### ParentNodeIdIndex
- **Use for**: Getting child nodes, tree traversal
- **Query pattern**: `parentNodeId = :parent_id`
- **Benefits**: Hierarchical queries, ordered children
- **Cost**: Additional write capacity for reordering

### Query Optimization Tips

1. **Use Consistent Read Only When Necessary**
   ```python
   # Good for real-time updates
   response = table.get_item(Key=key, ConsistentRead=True)
   
   # Better for performance in most cases
   response = table.get_item(Key=key, ConsistentRead=False)
   ```

2. **Implement Pagination for Large Results**
   ```python
   def paginated_query(query_params, max_items=1000):
       all_items = []
       last_key = None
       
       while len(all_items) < max_items:
           if last_key:
               query_params['ExclusiveStartKey'] = last_key
           
           response = table.query(**query_params)
           items = response.get('Items', [])
           all_items.extend(items)
           
           last_key = response.get('LastEvaluatedKey')
           if not last_key:
               break
       
       return all_items[:max_items]
   ```

3. **Use Projection Expressions for Large Items**
   ```python
   # Only get needed attributes
   response = table.get_item(
       Key=key,
       ProjectionExpression='title, description, createdAt'
   )
   ```

## Performance Optimization

### 1. Batch Operations
```python
# Batch read
def batch_get_nodes(node_ids, space_id):
    """Get multiple nodes efficiently"""
    request_items = {
        table.name: {
            'Keys': [
                {'nodeId': node_id, 'spaceId': space_id}
                for node_id in node_ids
            ]
        }
    }
    
    response = dynamodb.batch_get_item(RequestItems=request_items)
    return response['Responses'][table.name]

# Batch write
def batch_create_nodes(nodes):
    """Create multiple nodes efficiently"""
    with table.batch_writer() as batch:
        for node in nodes:
            batch.put_item(Item=node)
```

### 2. Connection Pooling
```python
# Initialize outside handler for reuse
import boto3
from botocore.config import Config

config = Config(
    max_pool_connections=50,
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

dynamodb = boto3.resource('dynamodb', config=config)
table = dynamodb.Table(os.environ['TABLE_NAME'])
```

### 3. Caching Strategy
```python
import functools
import time
import json

# Simple TTL cache
cache = {}
CACHE_TTL = 300  # 5 minutes

def cached_get_space(space_id):
    """Cache space metadata"""
    cache_key = f"space:{space_id}"
    now = time.time()
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if now - timestamp < CACHE_TTL:
            return data
    
    # Get from DynamoDB
    space = get_space(space_id)
    cache[cache_key] = (space, now)
    return space
```

## Monitoring & Troubleshooting

### Key Metrics to Monitor

1. **Table Metrics**
   - Read/Write capacity utilization
   - Throttled requests
   - Successful request latency
   - System errors

2. **Query Performance**
   - Items examined vs returned
   - Consumed capacity units
   - Query execution time

3. **Index Health**
   - Index size growth
   - Index utilization
   - Hot partitions

### Common Issues and Solutions

#### 1. Hot Partitions
**Symptom**: High throttling on specific partition keys
**Solution**:
```python
# Add randomization to distribute load
import random

def distributed_space_key(space_id):
    """Distribute space data across partitions"""
    bucket = random.randint(0, 9)  # 10 buckets
    return f"SPACE#{bucket}#{space_id}"
```

#### 2. Large Item Sizes
**Symptom**: Items approaching 400KB limit
**Solution**:
```python
def store_large_content(space_id, node_id, content):
    """Store large content in S3"""
    if len(content) > 100000:  # 100KB threshold
        s3_key = f"spaces/{space_id}/nodes/{node_id}/content.txt"
        s3.put_object(
            Bucket=os.environ['CONTENT_BUCKET'],
            Key=s3_key,
            Body=content
        )
        return s3_key
    return content
```

#### 3. Query Performance Issues
```python
# Monitor query performance
import time

def monitored_query(table, **kwargs):
    """Query with performance monitoring"""
    start_time = time.time()
    response = table.query(**kwargs)
    end_time = time.time()
    
    logger.info({
        'query_time': end_time - start_time,
        'items_returned': len(response.get('Items', [])),
        'consumed_capacity': response.get('ConsumedCapacity'),
        'scanned_count': response.get('ScannedCount'),
        'count': response.get('Count')
    })
    
    return response
```

## Backup & Recovery

### 1. Point-in-Time Recovery
```bash
# Enable PITR (done via serverless.yml)
aws dynamodb put-backup --table-name spaces-table --backup-name manual-backup-$(date +%Y%m%d)
```

### 2. Export to S3
```python
def export_table_to_s3(table_name, s3_bucket, s3_prefix):
    """Export table data to S3"""
    response = dynamodb.export_table_to_point_in_time(
        TableArn=f"arn:aws:dynamodb:us-east-1:account:table/{table_name}",
        S3Bucket=s3_bucket,
        S3Prefix=s3_prefix,
        ExportFormat='JSON'
    )
    return response['ExportDescription']['ExportArn']
```

### 3. Data Migration
```python
def migrate_space_data(old_table, new_table, space_id):
    """Migrate specific space data"""
    # Get space and all nodes
    space_response = old_table.get_item(
        Key={'PK': f'SPACE#{space_id}', 'SK': 'METADATA'}
    )
    
    nodes_response = old_table.query(
        IndexName='SpaceIdNodesIndex',
        KeyConditionExpression=Key('spaceId').eq(space_id)
    )
    
    # Batch write to new table
    with new_table.batch_writer() as batch:
        if 'Item' in space_response:
            batch.put_item(Item=space_response['Item'])
        
        for node in nodes_response.get('Items', []):
            batch.put_item(Item=node)
```

---

This guide provides comprehensive coverage of all database operations with performance optimization and monitoring strategies.
