import os
import boto3
import json
import logging
from datetime import datetime
from bedrock_client import BedrockClient
from s3_utils import upload_content_to_s3
from dynamo_utils import update_node_with_content

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
# Use the correct table name from serverless config
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'mindmap-explorer-sls-dev-nodes')
dynamodb = boto3.resource('dynamodb')
nodes_table = dynamodb.Table(nodes_table_name)

def get_node_context(space_id, parent_node_id=None):
    """Get additional context about the space and parent node if available"""
    context = {}
    
    # If we have a parent node, get its details
    if parent_node_id:
        try:
            parent_response = nodes_table.get_item(
                Key={
                    'nodeId': parent_node_id,
                    'spaceId': space_id
                }
            )
            if 'Item' in parent_response:
                context['parentNode'] = parent_response['Item']
        except Exception as e:
            logger.warning(f"Could not retrieve parent node {parent_node_id}: {e}")
    
    # Get siblings (other nodes in the same space with same parent)
    try:
        if parent_node_id:
            query_params = {
                'IndexName': 'ParentNodeIdIndex',
                'KeyConditionExpression': 'parentNodeId = :pid',
                'ExpressionAttributeValues': {
                    ':pid': parent_node_id
                },
                'Limit': 5  # Just get a few for context
            }
            sibling_response = nodes_table.query(**query_params)
            if 'Items' in sibling_response:
                context['siblingNodes'] = sibling_response['Items']
    except Exception as e:
        logger.warning(f"Could not retrieve sibling nodes: {e}")
    
    return context

def build_content_prompt(title, context=None):
    """Build a detailed prompt for the AI based on available context"""
    context = context or {}
    
    # Start with the basic prompt
    prompt = f"""Generate concise, informative HTML content for a mind map node titled "{title}".
    
The content should:
1. Provide a brief explanation or definition related to the title
2. Include 2-3 key points or facts relevant to the topic
3. Be formatted as clean HTML with minimal styling
4. Be concise but comprehensive, suitable for a mind map node

"""
    
    # Add parent node context if available
    if 'parentNode' in context:
        parent_title = context['parentNode'].get('title', '')
        prompt += f"\nThis is a child node under the parent topic: \"{parent_title}\"\n"
    
    # Add sibling context if available
    if 'siblingNodes' in context:
        siblings = [node.get('title', '') for node in context['siblingNodes'][:5]]
        if siblings:
            sibling_list = ", ".join([f'"{s}"' for s in siblings if s])
            if sibling_list:
                prompt += f"\nOther related nodes at the same level include: {sibling_list}\n"
    
    return prompt

def lambda_handler(event, context):
    """Handle EventBridge events for node creation/updates"""
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Extract node data from the event detail
        event_detail = event.get('detail', {})
        node_id = event_detail.get('nodeId')
        space_id = event_detail.get('spaceId')
        title = event_detail.get('title', '')
        parent_node_id = event_detail.get('parentNodeId')
        
        if not node_id or not space_id or not title:
            logger.warning(f"Missing required fields in event: {event}")
            return {
                'statusCode': 400,
                'body': 'Missing required node information'
            }
        
        # Skip if already has content
        if event_detail.get('s3Key'):
            logger.info(f"Node {node_id} already has content, skipping")
            return {
                'statusCode': 200,
                'body': 'Node already has content'
            }
        
        logger.info(f"Processing new node: {node_id}, title: {title}")
        
        # Gather context for better AI generation
        node_context = get_node_context(space_id, parent_node_id)
        
        # Build prompt with available context
        prompt = build_content_prompt(title, node_context)
        logger.info(f"Generated prompt for node {node_id}")
        
        # Generate content
        bedrock = BedrockClient()
        content_html = bedrock.generate_content(prompt)
        logger.info(f"AI content generated for node {node_id}")
        
        # Store in S3 and update DynamoDB
        s3_key = upload_content_to_s3(space_id, node_id, content_html)
        update_node_with_content(node_id, space_id, s3_key)
        logger.info(f"Content stored and node updated for {node_id}")
        
        return {
            'statusCode': 200,
            'body': f'Successfully generated and stored content for node {node_id}'
        }
        
    except Exception as e:
        logger.error(f"Failed to process node from event: {e}")
        # Raise to trigger the DLQ for failed events
        raise
