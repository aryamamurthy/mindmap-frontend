import boto3
import os
import logging
from datetime import datetime
import json

def update_node_with_content(node_id, space_id, s3_key):
    table_name = os.environ.get('NODES_TABLE_NAME')
    dynamodb = boto3.client('dynamodb')
    now = datetime.utcnow().isoformat()
    try:
        dynamodb.update_item(
            TableName=table_name,
            Key={
                'nodeId': {'S': node_id},
                'spaceId': {'S': space_id}
            },
            UpdateExpression="SET s3Key = :s, contentVersion = :v, updatedAt = :u",
            ExpressionAttributeValues={
                ':s': {'S': s3_key},
                ':v': {'S': now},
                ':u': {'S': now}
            }
        )
        # Publish EventBridge event after successful update
        eventbridge = boto3.client('events')
        event_bus_name = os.environ.get('EVENT_BUS_NAME', 'mindmap-events-bus-dev')
        event_detail = {
            'nodeId': node_id,
            'spaceId': space_id,
            's3Key': s3_key,
            'status': 'ContentGenerated',
            'timestamp': now
        }
        event = {
            'Source': 'mindmap-content-events',
            'DetailType': 'MindMapNode ContentGenerated',
            'Detail': json.dumps(event_detail),
            'EventBusName': event_bus_name
        }
        response = eventbridge.put_events(Entries=[event])
        logging.info(f"Published ContentGenerated event for node {node_id}: {response}")
    except Exception as e:
        logging.error(f"Failed to update DynamoDB node or publish event: {e}")
        raise
