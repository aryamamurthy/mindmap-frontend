# Mind Map Explorer API: Current State & Future Roadmap

## 1. Current Implementation Overview

### 1.1. User Management (users/)
- **CRUD Lambda Handlers:**
  - `createuser.py` — Create user (`POST /users`)
  - `getuser.py` — Get user by Id (`GET /users/{userId}`)
  - `updateuser.py` — Update user (`PUT /users/{userId}`)
  - `deleteuser.py` — Delete user (`DELETE /users/{userId}`)
  - `listusers.py` — List all users (`GET /users`)
- **DynamoDB Table:**
  - Table name: `users` (env: `USERS_TABLE_NAME`)
  - Primary key: `Id` (string, UUID)
  - Attributes: `Id`, `name`, `email`, `createdAt`, `updatedAt`
- **RESTful Compliance:**
  - All endpoints use correct HTTP methods, status codes, and JSON responses.
  - `Id` is used as the primary key in all handlers.

### 1.2. Spaces & Nodes (lambda_handlers/)
- **Spaces:**
  - CRUD handlers for spaces (create, list, get, update, delete)
  - DynamoDB table: `MindMapSpaces` (PK: `PK`, SK: `SK`)
- **Nodes:**
  - CRUD handlers for nodes (add, get, update, delete, reorder)
  - DynamoDB table: `MindMapNodes` (PK: `nodeId`, SK: `spaceId`)
- **S3 Integration:**
  - Node content stored in S3 bucket (env: `CONTENT_BUCKET_NAME`)
- **API Gateway:**
  - Endpoints mapped to Lambda handlers via AWS SAM template

### 1.3. Testing
- **Automated Tests:**
  - `tests/` directory with `pytest` and `requests`-based end-to-end tests for spaces and nodes
  - Verbose output for all test cases

## 2. RESTful API Endpoints (Current)

| Resource | Method | Path | Lambda Handler |
|----------|--------|------|----------------|
| User     | POST   | /users | createuser.py |
| User     | GET    | /users | listusers.py |
| User     | GET    | /users/{userId} | getuser.py |
| User     | PUT    | /users/{userId} | updateuser.py |
| User     | DELETE | /users/{userId} | deleteuser.py |
| Space    | POST   | /spaces | spaces_create_handler.py |
| Space    | GET    | /spaces | spaces_list_handler.py |
| Space    | GET    | /spaces/{spaceId} | spaces_tree_handler.py |
| Space    | PUT    | /spaces/{spaceId} | spaces_update_handler.py |
| Space    | DELETE | /spaces/{spaceId} | spaces_delete_handler.py |
| Node     | POST   | /spaces/{spaceId}/nodes | nodes_add_handler.py |
| Node     | GET    | /spaces/{spaceId}/nodes/{nodeId} | nodes_get_handler.py |
| Node     | PUT    | /spaces/{spaceId}/nodes/{nodeId} | nodes_update_handler.py |
| Node     | DELETE | /spaces/{spaceId}/nodes/{nodeId} | nodes_delete_handler.py |
| Node     | POST   | /spaces/{spaceId}/nodes/reorder | nodes_reorder_handler.py |

## 3. Known Gaps & RESTful Improvements
- No authentication/authorization yet (planned: Cognito integration)
- No pagination/filtering for list endpoints
- No `/users/{userId}/spaces` endpoint (list all spaces for a user)
- Error responses could be further structured (error codes, details)
- No OpenAPI/Swagger documentation yet

## 4. Future Roadmap

### 4.1. User & Space Relationship
- Implement `/users/{userId}/spaces` endpoint to list all spaces owned by a user
- Optionally, cascade delete spaces when a user is deleted

### 4.2. Authentication & Authorization
- Integrate Amazon Cognito for user signup, login, and JWT-based auth
- Secure all endpoints (except signup/login) with Cognito authorizer in API Gateway

### 4.3. Validation & Error Handling
- Add JSON Schema validation for all request bodies
- Return detailed, structured error responses

### 4.4. Pagination, Filtering, and Sorting
- Add pagination to all list endpoints (`/users`, `/spaces`, `/nodes`)
- Support filtering and sorting via query parameters

### 4.5. Documentation & Developer Experience
- Generate OpenAPI/Swagger docs for all endpoints
- Add usage examples and error code documentation

### 4.6. Testing & CI/CD
- Expand automated test coverage (users, auth, edge cases)
- Integrate tests into CI/CD pipeline

---

**This document summarizes the current backend API state and the next steps for a robust, production-ready Mind Map Explorer platform.**
