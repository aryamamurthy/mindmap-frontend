import boto3
import json
import os
import uuid
import argparse
from datetime import datetime

def publish_node_event(node_id=None, space_id=None, title=None, parent_node_id=None, event_type='MindMapNode Created'):
    """
    Publish a node creation or update event to EventBridge
    
    Args:
        node_id (str): The ID of the node. If not provided, a random UUID will be generated.
        space_id (str): The ID of the space. If not provided, a random UUID will be generated.
        title (str): The title of the node. Defaults to a sample title if not provided.
        parent_node_id (str, optional): The ID of the parent node, if any.
        event_type (str): The type of event ('MindMapNode Created' or 'MindMapNode Updated')
    
    Returns:
        dict: The response from the EventBridge PutEvents API call
    """
    # Load environment variables or use defaults
    event_bus_name = os.environ.get('EVENT_BUS_NAME', 'mindmap-events-bus-dev')
    
    # Generate random IDs if not provided
    if not node_id:
        node_id = str(uuid.uuid4())
    if not space_id:
        space_id = str(uuid.uuid4())
    if not title:
        title = f"Sample Node {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
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
        'DetailType': event_type,
        'Detail': json.dumps(event_detail),
        'EventBusName': event_bus_name
    }
    
    # Initialize EventBridge client
    events_client = boto3.client('events')
    
    # Send the event
    print(f"Sending event to {event_bus_name}:")
    print(json.dumps(event, indent=2))
    
    response = events_client.put_events(
        Entries=[event]
    )
    
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish node events to EventBridge')
    parser.add_argument('--node-id', help='Node ID (optional, random UUID if not provided)')
    parser.add_argument('--space-id', help='Space ID (optional, random UUID if not provided)')
    parser.add_argument('--title', help='Node title (optional)')
    parser.add_argument('--parent-node-id', help='Parent Node ID (optional)')
    parser.add_argument('--event-type', default='MindMapNode Created', 
                        choices=['MindMapNode Created', 'MindMapNode Updated'],
                        help='Event type (default: MindMapNode Created)')
    
    args = parser.parse_args()
    
    response = publish_node_event(
        node_id=args.node_id,
        space_id=args.space_id,
        title=args.title,
        parent_node_id=args.parent_node_id,
        event_type=args.event_type
    )
    
    print("Event published successfully:")
    print(json.dumps(response, indent=2))
