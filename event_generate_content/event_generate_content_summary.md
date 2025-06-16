# Mind Map Explorer: Event-Driven Content Generation (event_generate_content)

## Summary
This document describes the work completed for the `event_generate_content` component of the Mind Map Explorer project, focusing on the event-driven AI content generation system using AWS Lambda, EventBridge, DynamoDB, S3, and Bedrock.

---

## Key Accomplishments

### 1. Serverless Configuration
- **Handler Path:**
  - Ensured the Lambda handler is set to `nodes_generate_content_handler.lambda_handler` and the file is at the root of the deployment package.
  - Removed all references to `lambda_handlers` or subfolders for this Lambda.
- **Resource Names:**
  - Used correct DynamoDB table and S3 bucket names via variables in `serverless.yml`.
  - Set up environment variables for table, bucket, Bedrock model, and EventBridge bus.
- **Minimal Packaging:**
  - Configured the `package.patterns` to include only essential files: handler, Bedrock client, S3/DynamoDB utils, and requirements.
  - Excluded all unnecessary files/scripts from deployment.

### 2. Lambda Logic & Bedrock Integration
- **EventBridge Trigger:**
  - Lambda is triggered by EventBridge events for node creation/updates.
- **Bedrock Content Generation:**
  - Integrated Bedrock (nova model) for AI content generation.
  - Fixed extraction logic for nova model responses to correctly parse and clean the generated HTML content (removing code block markers, etc.).
- **S3 Storage:**
  - Ensured generated content is uploaded to S3 and referenced in DynamoDB.
- **DynamoDB Update & Event Publishing:**
  - Node record is updated with the S3 key and content version.
  - Event is published after content generation.

### 3. Permissions & Resources
- **IAM Permissions:**
  - Lambda has least-privilege access to DynamoDB, S3, Bedrock, EventBridge, CloudWatch Logs, and SQS (DLQ).
- **DLQ:**
  - Configured a Dead Letter Queue for failed events.

### 4. Testing & Validation
- **End-to-End Tests:**
  - Ran and validated `test_end_to_end.py` and `test_node_content_s3.py` to ensure the workflow is functional.
  - Confirmed that node creation triggers content generation, S3 storage, and DynamoDB updates.
- **Debug Logging:**
  - Added/verified debug logs for Bedrock responses and Lambda execution.

### 5. Cleanup
- **File Cleanup:**
  - Removed all non-essential files/scripts from `event_generate_content`, keeping only what is required for deployment and operation.

---

## Jira Ticket Update (Sample)

**Ticket:** MME-1234 — Implement Event-Driven AI Content Generation (event_generate_content)

**Status:** Done

**Details:**
- Serverless config updated for correct handler, resource names, and minimal packaging.
- Lambda now correctly extracts and stores Bedrock-generated content for nova model.
- End-to-end and API tests pass, confirming content is generated, stored in S3, and referenced in DynamoDB.
- All unnecessary files removed from deployment package.
- IAM permissions, DLQ, and event triggers validated.

**Testing:**
- Created nodes via API and confirmed content generation in S3 and DynamoDB.
- Validated with `test_end_to_end.py` and `test_node_content_s3.py`.

**Next Steps:**
- Monitor in production and optimize as needed.
- Ready for review/merge.

---

**Prepared by:** GitHub Copilot
**Date:** 2025-05-23
