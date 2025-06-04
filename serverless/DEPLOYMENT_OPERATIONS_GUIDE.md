# Deployment and Operations Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Process](#deployment-process)
4. [Configuration Management](#configuration-management)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Cost Management](#cost-management)

## Prerequisites

### Required Tools
```bash
# Node.js and npm
node --version  # v18.x or higher
npm --version   # v8.x or higher

# Serverless Framework
npm install -g serverless@4.15.1
serverless --version

# AWS CLI
aws --version  # v2.x recommended
aws configure  # Set up credentials

# Python
python --version  # 3.9 required
pip --version
```

### AWS Permissions
Required IAM permissions for deployment:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "s3:*",
        "iam:*",
        "logs:*",
        "events:*",
        "xray:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd CRUD-mindmap/serverless

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
pip install -r lambda_handlers/requirements.txt

# Verify structure
ls -la lambda_handlers/
# Should show all 10 handler files
```

## Environment Setup

### Environment Variables
Create `.env` files for different stages:

**.env.dev**:
```bash
STAGE=dev
REGION=us-east-1
SERVICE_NAME=mindmap-explorer-sls
SPACES_TABLE_NAME=mindmap-explorer-sls-dev-spaces
NODES_TABLE_NAME=mindmap-explorer-sls-dev-nodes
CONTENT_BUCKET_NAME=mindmap-explorer-sls-dev-content-bucket
EVENT_BUS_NAME=mindmap-events-bus-dev
LOG_LEVEL=INFO
```

**.env.prod**:
```bash
STAGE=prod
REGION=us-east-1
SERVICE_NAME=mindmap-explorer-sls
SPACES_TABLE_NAME=mindmap-explorer-sls-prod-spaces
NODES_TABLE_NAME=mindmap-explorer-sls-prod-nodes
CONTENT_BUCKET_NAME=mindmap-explorer-sls-prod-content-bucket
EVENT_BUS_NAME=mindmap-events-bus-prod
LOG_LEVEL=WARN
```

### Stage Configuration
Update `serverless.yml` for stage-specific settings:
```yaml
provider:
  stage: ${opt:stage, 'dev'}
  environment:
    SPACES_TABLE_NAME: ${self:service}-${self:provider.stage}-spaces
    NODES_TABLE_NAME: ${self:service}-${self:provider.stage}-nodes
    CONTENT_BUCKET_NAME: ${self:custom.contentBucketName}
    LOG_LEVEL: ${env:LOG_LEVEL, 'INFO'}
```

## Deployment Process

### Pre-Deployment Checklist
- [ ] AWS credentials configured
- [ ] Serverless Framework installed (v4.15.1)
- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Lambda handlers present in `lambda_handlers/` directory
- [ ] `serverless.yml` validated

### Deployment Commands

#### 1. Validate Configuration
```bash
# Validate serverless.yml syntax
serverless config validate

# Check AWS credentials
aws sts get-caller-identity

# Verify Python dependencies
python -c "import boto3, json, uuid, datetime; print('All imports successful')"
```

#### 2. Deploy to Development
```bash
# Deploy with verbose output
serverless deploy --stage dev --verbose

# Deploy specific function (for updates)
serverless deploy function --function spacesCreateSls --stage dev

# Package without deploying (for inspection)
serverless package --stage dev
```

#### 3. Deploy to Production
```bash
# Deploy to production
serverless deploy --stage prod --verbose

# Deploy with specific AWS profile
serverless deploy --stage prod --aws-profile production
```

### Deployment Scripts

**deploy.sh** (Linux/macOS):
```bash
#!/bin/bash
set -e

STAGE=${1:-dev}
echo "Deploying Mind Map API to stage: $STAGE"

# Validate configuration
echo "Validating configuration..."
serverless config validate

# Install dependencies
echo "Installing dependencies..."
npm install
pip install -r requirements.txt

# Deploy
echo "Deploying to AWS..."
serverless deploy --stage $STAGE --verbose

# Get outputs
echo "Deployment outputs:"
serverless info --stage $STAGE

echo "Deployment complete!"
```

**deploy.ps1** (Windows PowerShell):
```powershell
param(
    [string]$Stage = "dev"
)

Write-Host "Deploying Mind Map API to stage: $Stage" -ForegroundColor Green

try {
    Write-Host "Validating configuration..." -ForegroundColor Yellow
    serverless config validate

    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    pip install -r requirements.txt

    Write-Host "Deploying to AWS..." -ForegroundColor Yellow
    serverless deploy --stage $Stage --verbose

    Write-Host "Getting deployment info..." -ForegroundColor Yellow
    serverless info --stage $Stage

    Write-Host "Deployment complete!" -ForegroundColor Green
}
catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    exit 1
}
```

### Post-Deployment Verification

#### 1. Check CloudFormation Stack
```bash
# List stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Get stack outputs
aws cloudformation describe-stacks --stack-name mindmap-explorer-sls-dev
```

#### 2. Test API Endpoints
```bash
# Get API Gateway URL
API_URL=$(serverless info --stage dev --verbose | grep "endpoints:" -A 10 | grep "https" | awk '{print $2}')
echo "API URL: $API_URL"

# Test health endpoint
curl -X GET "$API_URL/spaces" -H "Content-Type: application/json"

# Create test space
curl -X POST "$API_URL/spaces" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Space","description":"Deployment test"}'
```

#### 3. Verify Lambda Functions
```bash
# List functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `MindMap`)].FunctionName'

# Test function invocation
aws lambda invoke --function-name MindMapSpacesListSls-dev response.json
cat response.json
```

#### 4. Check DynamoDB Tables
```bash
# List tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `mindmap-explorer-sls`)]'

# Describe table
aws dynamodb describe-table --table-name mindmap-explorer-sls-dev-spaces
```

#### 5. Verify S3 Bucket
```bash
# List buckets
aws s3 ls | grep mindmap-explorer-sls

# Check bucket configuration
aws s3api get-bucket-cors --bucket mindmap-explorer-sls-dev-content-bucket
```

## Configuration Management

### Serverless.yml Best Practices

#### 1. Environment-Specific Configuration
```yaml
custom:
  stages:
    dev:
      memorySize: 256
      timeout: 30
      logLevel: INFO
    prod:
      memorySize: 512
      timeout: 60
      logLevel: WARN
  
  currentStage: ${self:custom.stages.${self:provider.stage}}

provider:
  memorySize: ${self:custom.currentStage.memorySize}
  timeout: ${self:custom.currentStage.timeout}
  environment:
    LOG_LEVEL: ${self:custom.currentStage.logLevel}
```

#### 2. Resource Naming Conventions
```yaml
custom:
  resourcePrefix: ${self:service}-${self:provider.stage}
  
resources:
  Resources:
    SpacesTableSls:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.resourcePrefix}-spaces
```

#### 3. IAM Role Management
```yaml
provider:
  iam:
    role:
      name: ${self:custom.resourcePrefix}-lambda-role
      statements:
        - Effect: Allow
          Action:
            - dynamodb:PutItem
            - dynamodb:GetItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Scan
            - dynamodb:Query
          Resource:
            - Fn::GetAtt: [SpacesTableSls, Arn]
            - Fn::GetAtt: [NodesTableSls, Arn]
```

### Secrets Management
```bash
# Store secrets in AWS Systems Manager Parameter Store
aws ssm put-parameter \
  --name "/mindmap/dev/api-key" \
  --value "your-secret-key" \
  --type "SecureString"

# Reference in serverless.yml
provider:
  environment:
    API_KEY: ${ssm:/mindmap/${self:provider.stage}/api-key}
```

## Monitoring and Maintenance

### CloudWatch Dashboards
Create custom dashboard for monitoring:
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", "FunctionName", "MindMapSpacesCreateSls-dev"],
          ["AWS/Lambda", "Errors", "FunctionName", "MindMapSpacesCreateSls-dev"],
          ["AWS/Lambda", "Duration", "FunctionName", "MindMapSpacesCreateSls-dev"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Lambda Metrics"
      }
    }
  ]
}
```

### Automated Monitoring Scripts

**health-check.sh**:
```bash
#!/bin/bash
API_URL="https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev"

echo "Running health check..."

# Test spaces endpoint
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/spaces")
if [ $RESPONSE -eq 200 ]; then
    echo "✅ Spaces endpoint healthy"
else
    echo "❌ Spaces endpoint failed (HTTP $RESPONSE)"
    exit 1
fi

# Test with actual space creation
SPACE_RESPONSE=$(curl -s -X POST "$API_URL/spaces" \
  -H "Content-Type: application/json" \
  -d '{"name":"Health Check","description":"Automated health check"}')

if echo "$SPACE_RESPONSE" | grep -q "spaceId"; then
    echo "✅ Space creation successful"
    
    # Extract space ID and clean up
    SPACE_ID=$(echo "$SPACE_RESPONSE" | grep -o '"spaceId":"[^"]*' | cut -d'"' -f4)
    curl -s -X DELETE "$API_URL/spaces/$SPACE_ID" > /dev/null
    echo "✅ Cleanup completed"
else
    echo "❌ Space creation failed"
    echo "Response: $SPACE_RESPONSE"
    exit 1
fi

echo "🎉 All health checks passed!"
```

### Log Analysis
```bash
# Real-time log monitoring
serverless logs --function spacesCreateSls --stage dev --tail

# Search for errors in logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/MindMapSpacesCreateSls-dev \
  --filter-pattern "ERROR"

# Get performance metrics
aws logs start-query \
  --log-group-name /aws/lambda/MindMapSpacesCreateSls-dev \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @duration | filter @type = "REPORT" | sort @timestamp desc'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Deployment Failures

**Error**: `ServerlessError: Stack with id mindmap-explorer-sls-dev does not exist`
```bash
# Solution: First deployment failed, retry
serverless remove --stage dev
serverless deploy --stage dev
```

**Error**: `Cannot resolve serverless.yml`
```bash
# Solution: Ensure you're in the correct directory
pwd  # Should end with /serverless
ls serverless.yml  # Should exist
```

**Error**: `Handler 'lambda_handlers/spaces_create_handler.lambda_handler' missing`
```bash
# Solution: Verify handler files exist
ls lambda_handlers/spaces_create_handler.py
# Check handler path in serverless.yml
grep -n "handler:" serverless.yml
```

#### 2. Runtime Errors

**Error**: `[ERROR] Runtime.ImportModuleError: Unable to import module 'lambda_handlers/spaces_create_handler'`
```bash
# Solution: Check Python dependencies
pip install -r lambda_handlers/requirements.txt
# Verify package structure
serverless package --stage dev
unzip .serverless/mindmap-explorer-sls.zip -d temp/
ls temp/lambda_handlers/
```

**Error**: `AccessDenied: User is not authorized to perform: dynamodb:PutItem`
```bash
# Solution: Check IAM permissions
aws iam get-role-policy --role-name mindmap-explorer-sls-dev-us-east-1-lambdaRole --policy-name dev-mindmap-explorer-sls-lambda
```

#### 3. API Gateway Issues

**Error**: `{"message": "Internal server error"}`
```bash
# Solution: Check Lambda logs
serverless logs --function spacesCreateSls --stage dev

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs
```

#### 4. DynamoDB Issues

**Error**: `ResourceNotFoundException: Requested resource not found`
```bash
# Solution: Verify table exists and names match
aws dynamodb list-tables
aws dynamodb describe-table --table-name mindmap-explorer-sls-dev-spaces
```

### Debug Mode Deployment
```bash
# Deploy with debug output
SLS_DEBUG=* serverless deploy --stage dev --verbose

# Enable Lambda debug logging
serverless deploy --stage dev --verbose --debug
```

### Health Check Commands
```bash
# Complete system health check
echo "Checking AWS connectivity..."
aws sts get-caller-identity

echo "Checking Lambda functions..."
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `MindMap`)].{Name:FunctionName,Runtime:Runtime,State:State}'

echo "Checking DynamoDB tables..."
aws dynamodb list-tables --query 'TableNames[?contains(@, `mindmap-explorer-sls`)]'

echo "Checking S3 buckets..."
aws s3 ls | grep mindmap-explorer-sls

echo "Testing API endpoints..."
curl -s https://40ni2bsruc.execute-api.us-east-1.amazonaws.com/dev/spaces | jq .
```

## Rollback Procedures

### Automated Rollback
```bash
# Rollback to previous version
serverless rollback --timestamp 1642248000000 --stage dev

# Rollback specific function
serverless rollback function --function spacesCreateSls --version-number 2 --stage dev
```

### Manual Rollback
```bash
# List CloudFormation stack events
aws cloudformation describe-stack-events --stack-name mindmap-explorer-sls-dev

# Rollback CloudFormation stack
aws cloudformation cancel-update-stack --stack-name mindmap-explorer-sls-dev
```

### Database Rollback
```bash
# Restore DynamoDB table from backup
aws dynamodb restore-table-from-backup \
  --target-table-name mindmap-explorer-sls-dev-spaces-restore \
  --backup-arn arn:aws:dynamodb:us-east-1:account:table/mindmap-explorer-sls-dev-spaces/backup/backup-id
```

## Security Considerations

### API Security
```yaml
# Add API key requirement
provider:
  apiGateway:
    apiKeys:
      - name: mindmap-api-key
        description: API key for Mind Map application
    usagePlan:
      quota:
        limit: 10000
        period: DAY
      throttle:
        rateLimit: 100
        burstLimit: 200

functions:
  spacesCreateSls:
    events:
      - http:
          path: /spaces
          method: post
          private: true  # Require API key
```

### Environment Variables Security
```bash
# Use AWS Systems Manager for secrets
aws ssm put-parameter \
  --name "/mindmap/dev/database-encryption-key" \
  --value "your-encryption-key" \
  --type "SecureString" \
  --key-id "alias/aws/ssm"
```

### VPC Configuration (Optional)
```yaml
provider:
  vpc:
    securityGroupIds:
      - sg-xxxxxxxxx
    subnetIds:
      - subnet-xxxxxxxxx
      - subnet-yyyyyyyyy
```

## Performance Optimization

### Lambda Configuration
```yaml
functions:
  spacesCreateSls:
    memorySize: 512  # Increase for better performance
    timeout: 30
    reservedConcurrency: 10  # Limit concurrent executions
    provisionedConcurrency: 2  # Keep warm instances
```

### DynamoDB Optimization
```yaml
resources:
  Resources:
    SpacesTableSls:
      Type: AWS::DynamoDB::Table
      Properties:
        BillingMode: ON_DEMAND  # or PROVISIONED with auto-scaling
        PointInTimeRecoverySpecification:
          PointInTimeRecoveryEnabled: true
        StreamSpecification:
          StreamViewType: NEW_AND_OLD_IMAGES
```

### Caching Strategy
```python
# Lambda function with caching
import functools
import time

@functools.lru_cache(maxsize=128)
def get_cached_data(key):
    # Expensive operation
    return expensive_database_call(key)

# Use ElastiCache for distributed caching
import redis
redis_client = redis.Redis(host='your-elasticache-endpoint')
```

## Cost Management

### Cost Monitoring
```bash
# Get cost estimate
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Set up billing alerts
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json
```

### Cost Optimization
1. **Lambda**: Use appropriate memory allocation
2. **DynamoDB**: Use on-demand billing for variable workloads
3. **CloudWatch**: Set appropriate log retention periods
4. **S3**: Use lifecycle policies for content archival

### Resource Cleanup
```bash
# Remove development resources
serverless remove --stage dev

# Clean up orphaned resources
aws cloudformation list-stacks --stack-status-filter DELETE_FAILED
aws s3 rb s3://orphaned-bucket --force
```

This comprehensive deployment and operations guide provides everything needed to successfully deploy, monitor, and maintain the Mind Map serverless application.
