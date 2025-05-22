# Mind Map Explorer - Serverless Implementation

This is the Serverless Framework implementation of the Mind Map Explorer application.

## Prerequisites

- Node.js (for Serverless Framework)
- Python 3.9
- AWS CLI configured with appropriate credentials
- Serverless Framework installed (`npm install -g serverless`)

## Structure

- `serverless.yml` - Main configuration file for the Serverless Framework
- `utils.py` - Utility functions for Lambda handlers
- `package.json` - Node.js package file with scripts for deployment
- `requirements.txt` - Python dependencies

## Commands

- Deploy: `npm run deploy`
- Remove: `npm run remove`
- View logs: `npm run logs --function [functionName]`
- Get info: `npm run info`

## Resources Created

- DynamoDB Tables
  - Spaces Table - For storing mind map spaces
  - Nodes Table - For storing mind map nodes
- S3 Bucket - For storing node content
- Lambda Functions - For API operations
- API Gateway - For exposing the API

## API Endpoints

### Spaces

- POST /spaces - Create a new space
- GET /spaces - List spaces
- GET /spaces/{spaceId} - Get space tree
- PUT /spaces/{spaceId} - Update space
- DELETE /spaces/{spaceId} - Delete space

### Nodes

- POST /spaces/{spaceId}/nodes - Add a node
- GET /spaces/{spaceId}/nodes/{nodeId} - Get node
- PUT /spaces/{spaceId}/nodes/{nodeId} - Update node
- DELETE /spaces/{spaceId}/nodes/{nodeId} - Delete node
- POST /spaces/{spaceId}/nodes/reorder - Reorder nodes
