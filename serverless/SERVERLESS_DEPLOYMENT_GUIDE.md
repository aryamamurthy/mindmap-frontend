# Serverless Framework Deployment Guide

This guide explains how to deploy the Mind Map Explorer application using the Serverless Framework.

## Key Features

- All resource names differ from the SAM deployment to avoid conflicts
- Service name: `mindmap-explorer-sls` (vs. original `mind-map-explorer`)
- Tables and Lambda functions have "Sls" suffix to distinguish them

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Node.js and npm installed
3. Serverless Framework installed globally (`npm install -g serverless`)

## Deployment Steps

1. Install dependencies:
   ```powershell
   cd "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\serverless"
   npm install
   ```

2. Deploy to AWS:
   ```powershell
   # Using the deployment script
   .\deploy-sls.ps1 dev

   # Or using npm script
   npm run deploy:dev
   ```

3. View service information:
   ```powershell
   npm run info
   ```

## Resource Naming

The following resources will be created with unique names to avoid conflicts with the SAM deployment:

| Resource Type | Serverless Framework Name | Original SAM Name |
|---------------|---------------------------|-------------------|
| DynamoDB Table | SpacesTableSls | MindMapSpacesTable |
| DynamoDB Table | NodesTableSls | MindMapNodesTable |
| S3 Bucket | ContentBucketSls | ContentBucket |
| IAM Role | MindMapLambdaExecutionRoleSls | MindMapLambdaExecutionRoleSAM |
| Lambda Functions | MindMapSpacesCreateSls, etc. | MindMapSpacesCreateSAM, etc. |

## API Endpoints

The API endpoints will follow the same URL pattern as the SAM deployment:

- POST /spaces
- GET /spaces
- GET /spaces/{spaceId}
- PUT /spaces/{spaceId}
- DELETE /spaces/{spaceId}
- POST /spaces/{spaceId}/nodes
- GET /spaces/{spaceId}/nodes/{nodeId}
- PUT /spaces/{spaceId}/nodes/{nodeId}
- DELETE /spaces/{spaceId}/nodes/{nodeId}
- POST /spaces/{spaceId}/nodes/reorder

## Removing the Deployment

To remove all deployed resources:

```powershell
npm run remove -- --stage dev
```
