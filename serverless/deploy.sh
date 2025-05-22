#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Mind Map Explorer Serverless Deployment ===${NC}"

# Set timestamp for unique S3 bucket name
export TIMESTAMP=$(date +%s)
echo -e "${YELLOW}Using timestamp: ${TIMESTAMP}${NC}"

# Get the deployment stage
STAGE=${1:-dev}
echo -e "${YELLOW}Deploying to stage: ${STAGE}${NC}"

# Deploy the application
echo -e "${GREEN}Deploying Serverless application...${NC}"
npx serverless deploy --stage $STAGE --verbose

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Use 'npm run info' to see the deployed endpoints and resources${NC}"
