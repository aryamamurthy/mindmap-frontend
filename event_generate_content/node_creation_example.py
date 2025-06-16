"""
Example of how to integrate with the EventBridge-based content generation system
from another Lambda function in your project.
"""

import os
import boto3
import json
import uuid
import time

def publish_node_created_event(node_id, space_id, title, parent_node_id=None):
    """
    Publish a node creation event to EventBridge.
    This should be called from your node creation Lambda after creating a node.
    """
    # Get EventBridge event bus name from environment or use default
    event_bus_name = os.environ.get('EVENT_BUS_NAME', 'mindmap-events-bus-dev')
    
    # Create event detail
    event_detail = {
        'nodeId': node_id,
        'spaceId': space_id,
        'title': title,
    }
    
    # Add parent node ID if provided
    if parent_node_id:
        event_detail['parentNodeId'] = parent_node_id
    
    # Create the event
    event = {
        'Source': 'mindmap-content-events',
        'DetailType': 'MindMapNode Created',
        'Detail': json.dumps(event_detail),
        'EventBusName': event_bus_name
    }
    
    # Initialize EventBridge client
    events_client = boto3.client('events')
    
    # Send the event
    response = events_client.put_events(
        Entries=[event]
    )
    
    return response

def example_node_creation_handler(event, context):
    """
    Example Lambda handler that creates a node and then publishes an event
    to trigger content generation.
    """
    # Parse input
    body = json.loads(event.get('body', '{}'))
    
    # Extract node details from the request
    space_id = body.get('spaceId')
    title = body.get('title', 'Untitled Node')
    parent_node_id = body.get('parentNodeId')
    
    # Generate a new node ID
    node_id = str(uuid.uuid4())
    
    # Create timestamp for creation/update fields
    timestamp = int(time.time() * 1000)
    
    # Create node item
    node_item = {
        'nodeId': node_id,
        'spaceId': space_id,
        'title': title,
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    
    if parent_node_id:
        node_item['parentNodeId'] = parent_node_id
    
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('NODES_TABLE_NAME', 'MindMapNodes')
        table = dynamodb.Table(table_name)
        
        # Save the node to DynamoDB
        table.put_item(Item=node_item)
        
        # Publish event to trigger content generation
        publish_node_created_event(
            node_id=node_id,
            space_id=space_id,
            title=title,
            parent_node_id=parent_node_id
        )
        
        # Return success response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'nodeId': node_id,
                'message': 'Node created successfully and content generation triggered'
            })
        }
    except Exception as e:
        # Handle errors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to create node'
            })
        }

# Example: How your Lambda should include EventBridge IAM permissions
"""
In your serverless.yml or template.yaml for the Lambda that creates nodes:

provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - events:PutEvents
          Resource: "arn:aws:events:${self:provider.region}:${aws:accountId}:event-bus/mindmap-events-bus-*"
"""
