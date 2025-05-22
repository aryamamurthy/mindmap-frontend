# Mind-Map Creator: Simplified Implementation Plan

This plan outlines the simplified tasks to implement the Mind-Map Creator application. Each node will directly contain its content, merging the concept of "Pages" into "Nodes". Authentication and other complex features will be added in later iterations. The focus here is on a barebones, deployable API.

## Phase 1: Project Setup & Local Development Environment

*   **Task 1.1: Understand Product Specifications**
    *   Review the updated `product_specs.md` for core features (Spaces, Nodes with integrated content) and basic API structure.

*   **Task 1.2: Initial Project Setup**
    *   Initialize a Git repository.
    *   Create a simple project structure:
        *   `app/main.py` (for FastAPI app)
        *   `app/handlers/` (for Lambda handler logic - or combine into routers for extreme simplicity initially)
        *   `tests/`

*   **Task 1.3: Local Development with LocalStack**
    *   Set up LocalStack to emulate DynamoDB and S3.
    *   Ensure the FastAPI application can run locally and interact with LocalStack services.

## Phase 2: Core Backend - API Gateway (Simplified)

*   **Task 2.1: Basic FastAPI Application**
    *   Set up the main FastAPI application in `app/main.py`.
    *   Define Pydantic models for basic request/response structures (Spaces, Nodes).

*   **Task 2.2: API Gateway Setup with Mangum**
    *   Integrate Mangum to wrap the FastAPI application for AWS Lambda deployment.
    *   Define initial API Gateway routes for Spaces and Nodes (no authentication).

## Phase 3: Backend CRUD Operations - Spaces, Nodes (Simplified)

*This phase focuses on direct CRUD operations for Spaces and Nodes (which now include content).*

*   **Task 3.1: Implement "Spaces" CRUD APIs**
    *   Define DynamoDB schema for the `Spaces` table (PK: `SPACE#<spaceId>`, SK: `META`) and create in LocalStack.
    *   Develop simple Lambda Handlers (or direct FastAPI functions):
        *   `SpacesCreateHandler`
        *   `SpacesListHandler`
        *   `SpacesTreeHandler` (`GET /api/spaces/{spaceId}/tree`) - This will now fetch Node titles for the tree.
        *   `SpacesUpdateHandler`
        *   `SpacesDeleteHandler` (basic delete, will need to consider deleting associated Node content from S3).
    *   Develop corresponding FastAPI routes in `app/main.py` (or a dedicated spaces router).

*   **Task 3.2: Implement "Nodes" CRUD APIs (with Content)**
    *   Define DynamoDB schema for the `Nodes` table (PK: `SPACE#<spaceId>`, SK: `NODE#<nodeId>`) including attributes like `title`, `s3Key`, `version`. Create in LocalStack.
    *   Set up an S3 bucket in LocalStack for node content (`contentHTML`).
    *   Develop Lambda Handlers/FastAPI functions:
        *   `NodesAddHandler` (handles `title`, optional `contentHTML` with S3 upload, creates `s3Key`)
        *   `NodesGetHandler` (retrieves Node metadata from DynamoDB and `contentHTML` from S3 via `s3Key`)
        *   `NodesUpdateHandler` (handles updates to `title` and/or `contentHTML` with S3 update)
        *   `NodesDeleteHandler` (basic delete from DynamoDB, and S3 object deletion).
        *   `NodesReorderHandler`
    *   Develop corresponding FastAPI routes.

## Phase 4: Infrastructure as Code (IaC) & Deployment Strategy

*   **Task 4.1: Choose and Implement IaC Strategy**
    *   Select an IaC tool (e.g., AWS SAM or Serverless Framework).

*   **Task 4.2: Define Basic AWS Resources in IaC**
    *   Create IaC templates for:
        *   API Gateway (basic routes)
        *   Lambda functions (for FastAPI app via Mangum)
        *   DynamoDB tables (Spaces, Nodes)
        *   S3 bucket for node content
    *   Develop simple deployment scripts.

## Phase 5: Advanced Backend - Event-Driven Architecture (Simplified for Node Content)

*   **Task 5.1: Implement Basic Event-Driven Logic for Deletes**
    *   Design and implement basic event-driven mechanisms for cascading deletes (e.g., Space deletion triggers Node data and S3 object cleanup for each node). This can start with synchronous cleanup within the delete handlers.

*   **Task 5.2: Consider SQS for Decoupling (Optional)**
    *   If delete operations (especially S3 cleanup) become slow, consider SQS.

## Phase 6: Testing & Quality Assurance

*   **Task 6.1: Basic Test Coverage**
    *   Write unit tests for core logic.
    *   Write basic integration tests for API endpoints interacting with LocalStack (DynamoDB and S3 for nodes).

*   **Task 6.2: API Documentation**
    *   Leverage FastAPI's automatic OpenAPI documentation generation.

## Phase 7: UI Development

*   **Task 7.1: Build UI Application**
    *   Select a frontend framework.
    *   Implement UI for core features:
        *   Spaces (Create, List, View)
        *   Nodes (Hierarchical view, Add, Rename/Edit Content, Delete)
    *   Integrate UI with the backend APIs.

*   **Task 7.2: Enable Server-Side Rendering (SSR) - If Required (Future)**
    *   Evaluate and implement SSR later if needed.

---
This simplified plan prioritizes a functional, deployable barebones version where nodes directly manage their content. Authentication and advanced features are deferred.
