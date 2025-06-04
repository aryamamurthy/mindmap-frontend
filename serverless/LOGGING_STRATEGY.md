# Comprehensive Logging Strategy for Mind Map Serverless Application

## Table of Contents
1. [Overview](#overview)
2. [Logging Architecture](#logging-architecture)
3. [Log Levels and Categories](#log-levels-and-categories)
4. [Structured Logging Implementation](#structured-logging-implementation)
5. [CloudWatch Integration](#cloudwatch-integration)
6. [X-Ray Tracing](#x-ray-tracing)
7. [Monitoring and Alerting](#monitoring-and-alerting)
8. [Log Analysis and Troubleshooting](#log-analysis-and-troubleshooting)
9. [Performance Metrics](#performance-metrics)
10. [Security Logging](#security-logging)

## Overview

This document outlines the comprehensive logging strategy for the Mind Map Serverless application deployed on AWS. The application consists of 10 Lambda functions handling CRUD operations for spaces and nodes, with integrated DynamoDB storage and S3 content management.

### Application Architecture
- **Service**: mindmap-explorer-sls
- **Runtime**: Python 3.9
- **Functions**: 10 Lambda functions
- **Storage**: 2 DynamoDB tables, 1 S3 bucket
- **Tracing**: AWS X-Ray enabled
- **Framework**: Serverless Framework v4

## Logging Architecture

### Current Configuration
```yaml
provider:
  tracing:
    apiGateway: true
    lambda: true
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: "arn:aws:logs:*:*:*"
        - Effect: Allow
          Action:
            - xray:PutTraceSegments
            - xray:PutTelemetryRecords
          Resource: "*"
```

### Log Groups Structure
Each Lambda function creates its own CloudWatch Log Group:
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

## Log Levels and Categories

### Log Levels
1. **ERROR**: System errors, exceptions, failures
2. **WARN**: Performance issues, fallbacks, deprecated usage
3. **INFO**: Business logic flow, successful operations
4. **DEBUG**: Detailed execution flow, variable states

### Log Categories
1. **REQUEST**: Incoming request details
2. **RESPONSE**: Outgoing response details
3. **DATABASE**: DynamoDB operations
4. **S3**: S3 operations
5. **BUSINESS**: Business logic execution
6. **PERFORMANCE**: Timing and metrics
7. **SECURITY**: Authentication and authorization
8. **ERROR**: Exception handling

## Structured Logging Implementation

### Standard Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "category": "REQUEST",
  "requestId": "abc123-def456-ghi789",
  "functionName": "MindMapSpacesCreateSls-dev",
  "message": "Creating new space",
  "metadata": {
    "spaceId": "uuid-here",
    "userId": "user-123",
    "requestBody": {...}
  },
  "traceId": "1-5e1b4151-bd7c7ca8d1a6b8a2b9c3d4e5"
}
```

### Implementation Pattern for Each Handler
```python
import json
import logging
import os
import uuid
import time
from datetime import datetime

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_structured(level, category, message, metadata=None, request_id=None):
    """Create structured log entry"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "category": category,
        "message": message,
        "functionName": os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'unknown'),
        "requestId": request_id or str(uuid.uuid4()),
        "metadata": metadata or {}
    }
    
    if level == "ERROR":
        logger.error(json.dumps(log_entry))
    elif level == "WARN":
        logger.warning(json.dumps(log_entry))
    elif level == "DEBUG":
        logger.debug(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

def lambda_handler(event, context):
    start_time = time.time()
    request_id = context.aws_request_id
    
    # Log incoming request
    log_structured("INFO", "REQUEST", "Function invoked", {
        "path": event.get('path'),
        "httpMethod": event.get('httpMethod'),
        "headers": event.get('headers', {}),
        "pathParameters": event.get('pathParameters', {}),
        "body": event.get('body')
    }, request_id)
    
    try:
        # Business logic here
        result = process_request(event, context, request_id)
        
        # Log successful response
        execution_time = (time.time() - start_time) * 1000
        log_structured("INFO", "RESPONSE", "Function completed successfully", {
            "statusCode": result['statusCode'],
            "executionTimeMs": execution_time
        }, request_id)
        
        return result
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        log_structured("ERROR", "ERROR", f"Function failed: {str(e)}", {
            "errorType": type(e).__name__,
            "errorMessage": str(e),
            "executionTimeMs": execution_time
        }, request_id)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'requestId': request_id
            })
        }
```

## CloudWatch Integration

### Log Retention Policy
- **Production**: 30 days
- **Development**: 7 days
- **Critical errors**: 90 days (separate log group)

### CloudWatch Insights Queries

#### 1. Error Analysis
```sql
fields @timestamp, level, category, message, metadata.errorType
| filter level = "ERROR"
| stats count() by metadata.errorType
| sort count desc
```

#### 2. Performance Monitoring
```sql
fields @timestamp, functionName, metadata.executionTimeMs
| filter metadata.executionTimeMs > 5000
| stats avg(metadata.executionTimeMs), max(metadata.executionTimeMs) by functionName
```

#### 3. Request Volume Analysis
```sql
fields @timestamp, functionName
| filter category = "REQUEST"
| stats count() by functionName
| sort count desc
```

#### 4. Database Operation Monitoring
```sql
fields @timestamp, message, metadata.tableName, metadata.operation
| filter category = "DATABASE"
| stats count() by metadata.operation, metadata.tableName
```

### Custom Metrics
Create custom CloudWatch metrics for:
- Request count per function
- Error rate per function
- Average execution time
- DynamoDB operation counts
- S3 operation counts

## X-Ray Tracing

### Trace Segments
Each Lambda function creates the following segments:
1. **Lambda Runtime**: Function execution
2. **DynamoDB**: Database operations
3. **S3**: File operations
4. **External APIs**: Event publishing

### Custom Annotations
```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('space_creation')
def create_space(space_data, request_id):
    xray_recorder.put_annotation('spaceId', space_data['spaceId'])
    xray_recorder.put_annotation('operation', 'create_space')
    xray_recorder.put_metadata('request_details', space_data)
```

### Service Map
The X-Ray service map shows:
- API Gateway → Lambda Functions
- Lambda Functions → DynamoDB Tables
- Lambda Functions → S3 Bucket
- Lambda Functions → EventBridge (for content generation)

## Monitoring and Alerting

### CloudWatch Alarms

#### 1. Error Rate Alarm
```yaml
ErrorRateAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: MindMap-HighErrorRate
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
```

#### 2. High Latency Alarm
```yaml
LatencyAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: MindMap-HighLatency
    MetricName: Duration
    Namespace: AWS/Lambda
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10000
    ComparisonOperator: GreaterThanThreshold
```

#### 3. DynamoDB Throttling Alarm
```yaml
DynamoDBThrottleAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: MindMap-DynamoDB-Throttling
    MetricName: UserErrors
    Namespace: AWS/DynamoDB
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```

### Dashboard Configuration
Create CloudWatch Dashboard with:
1. Function invocation count
2. Error rates by function
3. Average duration by function
4. DynamoDB read/write capacity
5. S3 request metrics
6. X-Ray service map

## Log Analysis and Troubleshooting

### Common Error Patterns

#### 1. DynamoDB Errors
```json
{
  "level": "ERROR",
  "category": "DATABASE",
  "message": "DynamoDB operation failed",
  "metadata": {
    "errorType": "ResourceNotFoundException",
    "tableName": "mindmap-explorer-sls-dev-spaces",
    "operation": "put_item"
  }
}
```

#### 2. Validation Errors
```json
{
  "level": "ERROR",
  "category": "BUSINESS",
  "message": "Invalid request data",
  "metadata": {
    "missingFields": ["name"],
    "providedData": {...}
  }
}
```

#### 3. S3 Errors
```json
{
  "level": "ERROR",
  "category": "S3",
  "message": "S3 operation failed",
  "metadata": {
    "bucket": "mindmap-explorer-sls-dev-content-bucket",
    "key": "content/uuid.html",
    "operation": "put_object"
  }
}
```

### Troubleshooting Workflow
1. **Check CloudWatch Logs** for error details
2. **Review X-Ray traces** for distributed request flow
3. **Analyze CloudWatch Metrics** for patterns
4. **Check DynamoDB** table status and metrics
5. **Verify S3 permissions** and bucket policies
6. **Review API Gateway** logs for request/response issues

## Performance Metrics

### Key Performance Indicators (KPIs)
1. **Function Duration**: < 5 seconds for 95th percentile
2. **Error Rate**: < 1% across all functions
3. **DynamoDB Latency**: < 100ms for single item operations
4. **S3 Upload Time**: < 2 seconds for typical content
5. **Cold Start Rate**: < 5% of invocations

### Performance Logging
```python
def log_performance_metrics(operation, duration_ms, success, metadata=None):
    log_structured("INFO", "PERFORMANCE", f"{operation} completed", {
        "operation": operation,
        "durationMs": duration_ms,
        "success": success,
        "metadata": metadata or {}
    })

# Usage example
start = time.time()
try:
    table.put_item(Item=item)
    log_performance_metrics("dynamodb_put_item", 
                           (time.time() - start) * 1000, 
                           True, 
                           {"tableName": table.name})
except Exception as e:
    log_performance_metrics("dynamodb_put_item", 
                           (time.time() - start) * 1000, 
                           False, 
                           {"error": str(e)})
```

## Security Logging

### Security Events to Log
1. **Authentication failures**
2. **Authorization violations**
3. **Suspicious request patterns**
4. **Data access events**
5. **Configuration changes**

### Security Log Format
```json
{
  "level": "WARN",
  "category": "SECURITY",
  "message": "Unauthorized access attempt",
  "metadata": {
    "sourceIP": "192.168.1.1",
    "userAgent": "Mozilla/5.0...",
    "resource": "/spaces/uuid",
    "method": "DELETE",
    "userId": "anonymous"
  }
}
```

### Compliance Considerations
- **Data Privacy**: Ensure no PII in logs
- **Retention**: Follow compliance requirements
- **Access Control**: Restrict log access to authorized personnel
- **Encryption**: Logs encrypted at rest and in transit

## Implementation Checklist

### Phase 1: Basic Logging
- [ ] Implement structured logging in all handlers
- [ ] Add request/response logging
- [ ] Configure CloudWatch log groups
- [ ] Set up basic error alerting

### Phase 2: Enhanced Monitoring
- [ ] Implement performance metrics logging
- [ ] Add custom CloudWatch metrics
- [ ] Configure X-Ray tracing annotations
- [ ] Create CloudWatch dashboard

### Phase 3: Advanced Analysis
- [ ] Set up CloudWatch Insights queries
- [ ] Implement log aggregation
- [ ] Add security event logging
- [ ] Configure compliance reporting

### Phase 4: Optimization
- [ ] Optimize log volume and costs
- [ ] Implement log sampling for high-volume operations
- [ ] Add predictive alerting
- [ ] Integrate with external monitoring tools

## Maintenance and Updates

### Regular Tasks
1. **Review log retention policies** monthly
2. **Update CloudWatch Insights queries** as needed
3. **Optimize alarm thresholds** based on historical data
4. **Review security logs** weekly
5. **Update documentation** with new patterns

### Cost Optimization
- Use log sampling for high-volume, low-value logs
- Implement tiered storage for historical logs
- Regular cleanup of unused log groups
- Monitor CloudWatch costs and optimize accordingly

This logging strategy provides comprehensive visibility into the Mind Map serverless application, enabling effective monitoring, troubleshooting, and optimization of the system.
