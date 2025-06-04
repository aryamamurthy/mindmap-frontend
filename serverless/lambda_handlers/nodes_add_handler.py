import json
import boto3
import os
import uuid
import datetime
import time
import traceback
from utils.logger import StructuredLogger, PerformanceTracker, extract_correlation_id, extract_user_id

# Initialize structured logger
logger = StructuredLogger('nodes_add_handler')

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
nodes_table_name = os.environ.get('NODES_TABLE_NAME', 'Nodes')
nodes_table = dynamodb.Table(nodes_table_name)
s3_client = boto3.client('s3')
content_bucket_name = os.environ.get('CONTENT_BUCKET_NAME', 'mindmap-content-bucket')
eventbridge_client = boto3.client('events')
event_bus_name = os.environ.get('EVENT_BUS_NAME', 'mindmap-events-bus-dev')

def lambda_handler(event, context):
    """
    Adds a new node to a space.
    Required path parameter: spaceId
    Required body attributes: title, contentHTML (optional), parentNodeId (optional, for sub-nodes), orderIndex (optional)
    """
    start_time = time.time()
    correlation_id = extract_correlation_id(event)
    user_id = extract_user_id(event)
    
    try:
        # Log incoming request
        logger.request(
            method=event.get('httpMethod', 'POST'),
            path=event.get('path', '/spaces/{spaceId}/nodes'),
            correlation_id=correlation_id,
            user_id=user_id,
            body=json.loads(event.get('body', '{}')),
            headers=event.get('headers', {})
        )
        
        # Extract and validate path parameters
        path_parameters = event.get('pathParameters', {})
        space_id = path_parameters.get('spaceId')

        if not space_id:
            logger.business_logic(
                message="Node creation failed: spaceId is required",
                correlation_id=correlation_id,
                operation="validate_path_params",
                additional_data={"validation_error": "missing_space_id"}
            )
            
            response = {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'spaceId is required'})
            }
            
            logger.response(
                status_code=400,
                correlation_id=correlation_id,
                response_size=len(response['body'])
            )
            
            return response

        # Parse and validate request body
        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        content_html = body.get('contentHTML')
        parent_node_id = body.get('parentNodeId')
        order_index = body.get('orderIndex', 0)

        if not title:
            logger.business_logic(
                message="Node creation failed: title is required",
                correlation_id=correlation_id,
                operation="validate_input",
                additional_data={"validation_error": "missing_title", "space_id": space_id}
            )
            
            response = {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'title is required'})
            }
            
            logger.response(
                status_code=400,
                correlation_id=correlation_id,
                response_size=len(response['body'])
            )
            
            return response

        # Generate node data
        node_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()

        logger.business_logic(
            message=f"Creating new node: {title}",
            correlation_id=correlation_id,
            operation="node_creation",
            additional_data={
                "node_id": node_id,
                "space_id": space_id,
                "node_title": title,
                "parent_node_id": parent_node_id,
                "has_content": bool(content_html)
            }
        )        # Create the node_item dictionary
        node_item = {
            'nodeId': node_id,
            'spaceId': space_id,
            'title': title,
            'orderIndex': order_index,
            'createdAt': created_at,
            'updatedAt': created_at,
        }
        
        # Handle content storage
        content_stored_in_s3 = False
        if content_html is not None:
            if len(content_html) > 1000:  # Store large content in S3
                try:
                    with PerformanceTracker(logger, 's3_put_object', correlation_id):
                        s3_key = f"nodes/{node_id}/content.html"
                        s3_client.put_object(
                            Bucket=content_bucket_name,
                            Key=s3_key,
                            Body=content_html,
                            ContentType='text/html'
                        )
                    
                    logger.s3_operation(
                        operation="put_object",
                        bucket=content_bucket_name,
                        key=s3_key,
                        correlation_id=correlation_id,
                        object_size=len(content_html)
                    )
                    
                    node_item['contentS3Key'] = s3_key
                    node_item['contentPreview'] = content_html[:100]
                    content_stored_in_s3 = True
                    
                except Exception as s3_error:
                    logger.error(
                        error_type="S3Error",
                        message=f"Failed to store content in S3: {str(s3_error)}",
                        correlation_id=correlation_id,
                        additional_context={"s3_key": s3_key, "content_size": len(content_html)}
                    )
                    # Fallback to storing preview in DynamoDB
                    node_item['contentPreview'] = content_html[:100]
            else:
                # Store small content directly in DynamoDB
                node_item['contentPreview'] = content_html
        
        # Only add parentNodeId if it's not None to avoid index issues
        if parent_node_id is not None:
            node_item['parentNodeId'] = parent_node_id

        # Store item in DynamoDB
        with PerformanceTracker(logger, 'dynamodb_put_item', correlation_id):
            nodes_table.put_item(Item=node_item)
            
        logger.database_operation(
            operation="put_item",
            table_name=nodes_table_name,
            correlation_id=correlation_id,
            item_count=1
        )

        # Publish event for content generation (only if no content provided)
        if not content_html:
            try:
                event_detail = {
                    'nodeId': node_id,
                    'spaceId': space_id,
                    'title': title,
                    'parentNodeId': parent_node_id,
                    'orderIndex': order_index,
                    'createdAt': created_at
                }
                
                with PerformanceTracker(logger, 'eventbridge_put_events', correlation_id):
                    eventbridge_client.put_events(
                        Entries=[
                            {
                                'Source': 'mindmap-content-events',
                                'DetailType': 'MindMapNode Created',
                                'Detail': json.dumps(event_detail),
                                'EventBusName': event_bus_name
                            }
                        ]
                    )
                
                logger.business_logic(
                    message=f"Published node creation event for {node_id}",
                    correlation_id=correlation_id,
                    operation="event_publishing",
                    additional_data={"event_bus": event_bus_name, "node_id": node_id}
                )
                
            except Exception as e:
                logger.error(
                    error_type="EventBridgeError",
                    message=f"Failed to publish event: {str(e)}",
                    correlation_id=correlation_id,
                    additional_context={"event_bus": event_bus_name, "node_id": node_id}
                )
                # Don't fail the whole operation if event publishing fails

        # Prepare successful response
        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Location': f"/spaces/{space_id}/nodes/{node_id}",
                'X-Correlation-ID': correlation_id
            },
            'body': json.dumps(node_item)
        }

        # Log successful response
        execution_time_ms = (time.time() - start_time) * 1000
        logger.response(
            status_code=201,
            correlation_id=correlation_id,
            response_size=len(response['body']),
            execution_time_ms=execution_time_ms
        )

        logger.business_logic(
            message=f"Node created successfully: {node_id}",
            correlation_id=correlation_id,
            operation="node_creation_complete",
            additional_data={
                "node_id": node_id,
                "space_id": space_id,
                "content_stored_in_s3": content_stored_in_s3
            }
        )

        return response

    except json.JSONDecodeError as e:
        logger.error(
            error_type="JSONDecodeError",
            message="Invalid JSON in request body",
            correlation_id=correlation_id,
            error_code="INVALID_JSON",
            additional_context={"raw_body": event.get('body', '')}
        )
        
        response = {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
        
        logger.response(
            status_code=400,
            correlation_id=correlation_id,
            response_size=len(response['body'])
        )
        
        return response

    except Exception as e:
        logger.error(
            error_type=type(e).__name__,
            message=f"Error adding node: {str(e)}",
            correlation_id=correlation_id,
            stack_trace=traceback.format_exc(),
            error_code="NODE_CREATION_FAILED",
            additional_context={
                "space_id": space_id if 'space_id' in locals() else None,
                "node_title": title if 'title' in locals() else None
            }
        )
        
        response = {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Could not create node', 'details': str(e)})
        }
        
        logger.response(
            status_code=500,
            correlation_id=correlation_id,
            response_size=len(response['body'])
        )
        
        return response
