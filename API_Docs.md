# Mind Map Explorer API Documentation

## Overview
This document provides comprehensive documentation for all RESTful API endpoints in the Mind Map Explorer project, including their purpose, request/response formats, and end-to-end behavior. It also details the automated tests, their order, and what each test covers.

---

## API Endpoints

### User Endpoints

#### Create User
- **POST** `/users`
- **Handler:** `createuser.py`
- **Description:** Create a new user.
- **Request Body:**
  ```json
  { "name": "string", "email": "string" }
  ```
- **Response (201):**
  ```json
  { "Id": "string", "name": "string", "email": "string", "createdAt": "ISO-timestamp" }
  ```

#### Get User
- **GET** `/users/{userId}`
- **Handler:** `getuser.py`
- **Description:** Retrieve a user by their ID.
- **Response (200):**
  ```json
  { "Id": "string", "name": "string", "email": "string", "createdAt": "ISO-timestamp" }
  ```

#### Update User
- **PUT** `/users/{userId}`
- **Handler:** `updateuser.py`
- **Description:** Update user details.
- **Request Body:**
  ```json
  { "name": "string", "email": "string" }
  ```
- **Response (200):** Updated user object.

#### Delete User
- **DELETE** `/users/{userId}`
- **Handler:** `deleteuser.py`
- **Description:** Delete a user by ID.
- **Response (204):** No content.

#### List Users
- **GET** `/users`
- **Handler:** `listusers.py`
- **Description:** List all users.
- **Response (200):** Array of user objects.

---

### Space Endpoints

#### Create Space
- **POST** `/spaces`
- **Handler:** `spaces_create_handler.py`
- **Description:** Create a new mind map space.
- **Request Body:**
  ```json
  { "name": "string", "description": "string", "ownerId": "string" }
  ```
- **Response (201):**
  ```json
  { "spaceId": "string", "name": "string", "description": "string", "createdAt": "ISO-timestamp" }
  ```

#### List Spaces
- **GET** `/spaces`
- **Handler:** `spaces_list_handler.py`
- **Description:** List all spaces for the user.
- **Response (200):** Array of space objects.

#### Get Space (Tree)
- **GET** `/spaces/{spaceId}`
- **Handler:** `spaces_tree_handler.py`
- **Description:** Get a space and its full node tree.
- **Response (200):**
  ```json
  { "spaceId": "string", "nodes": [ { "nodeId": "string", "title": "string", "children": [ ... ] } ] }
  ```

#### Update Space
- **PUT** `/spaces/{spaceId}`
- **Handler:** `spaces_update_handler.py`
- **Description:** Update a space's name or description.
- **Request Body:**
  ```json
  { "name": "string", "description": "string" }
  ```
- **Response (200):** Updated space object.

#### Delete Space
- **DELETE** `/spaces/{spaceId}`
- **Handler:** `spaces_delete_handler.py`
- **Description:** Delete a space and all its nodes/content.
- **Response (204):** No content.

---

### Node Endpoints

#### Add Node
- **POST** `/spaces/{spaceId}/nodes`
- **Handler:** `nodes_add_handler.py`
- **Description:** Add a new node to a space. Optionally includes HTML content (stored in S3).
- **Request Body:**
  ```json
  { "title": "string", "contentHTML": "string", "parentNodeId": "string|null", "orderIndex": 0 }
  ```
- **Response (201):**
  ```json
  { "nodeId": "string", "title": "string", "parentNodeId": "string|null", "orderIndex": 0, "s3Key": "string" }
  ```

#### Get Node
- **GET** `/spaces/{spaceId}/nodes/{nodeId}`
- **Handler:** `nodes_get_handler.py`
- **Description:** Get a node's metadata and content.
- **Response (200):**
  ```json
  { "nodeId": "string", "title": "string", "contentHTML": "string", "parentNodeId": "string|null", "orderIndex": 0 }
  ```

#### Update Node
- **PUT** `/spaces/{spaceId}/nodes/{nodeId}`
- **Handler:** `nodes_update_handler.py`
- **Description:** Update a node's title or content.
- **Request Body:**
  ```json
  { "title": "string", "contentHTML": "string" }
  ```
- **Response (200):** Updated node object.

#### Delete Node
- **DELETE** `/spaces/{spaceId}/nodes/{nodeId}`
- **Handler:** `nodes_delete_handler.py`
- **Description:** Delete a node and its content from S3.
- **Response (204):** No content.

#### Reorder Nodes
- **POST** `/spaces/{spaceId}/nodes/reorder`
- **Handler:** `nodes_reorder_handler.py`
- **Description:** Reorder nodes within a space.
- **Request Body:**
  ```json
  { "nodeOrder": ["nodeId1", "nodeId2", ...] }
  ```
- **Response (200):** Confirmation or updated order.

---

## End-to-End API Working
1. **User creates a space** (`POST /spaces`).
2. **User adds nodes** to the space (`POST /spaces/{spaceId}/nodes`).
3. **User can get the full tree** (`GET /spaces/{spaceId}`) or individual nodes (`GET /spaces/{spaceId}/nodes/{nodeId}`).
4. **User updates nodes or spaces** as needed (`PUT` endpoints).
5. **User deletes nodes or spaces** (`DELETE` endpoints), which also cleans up S3 content.
6. **Node order can be changed** with the reorder endpoint.

---

## Automated Tests

### Test Files
- `tests/test_spaces_api.py`: Tests for space endpoints.
- `tests/test_nodes_api.py`: Tests for node endpoints.

### Test Order and Coverage

#### 1. Space Tests (`test_spaces_api.py`)
- **test_create_space**: Creates a new space and asserts a 201 response with a valid spaceId.
- **test_list_spaces**: Lists all spaces and checks for a 200 response and correct format.
- **test_space_lifecycle**: Full lifecycle:
  - Create a space
  - Get the space
  - Update the space
  - Delete the space
  - Confirm deletion

#### 2. Node Tests (`test_nodes_api.py`)
- **test_add_get_update_delete_node**: End-to-end node lifecycle:
  - Add a node to a test space
  - Get the node
  - Update the node
  - Delete the node
  - Confirm deletion
- **test_recursive_node_deletion**: Tests that deleting a parent node recursively deletes all child nodes.

#### Test Execution Order
- Space tests run first to ensure a valid space exists for node tests.
- Node tests use a fixture to create a test space, add nodes, and clean up after.

### What Each Test Does (End-to-End)
- **Space tests** verify creation, retrieval, update, deletion, and listing of spaces.
- **Node tests** verify node creation, retrieval, update, deletion, and recursive deletion logic, including S3 integration for content.

---

## Notes
- All endpoints use correct RESTful status codes (201 for create, 200 for get/update, 204 for delete).
- Error responses are structured and informative.
- S3 and DynamoDB integration is robust and tested.
- IAM permissions are set for development; restrict in production.

---

For further details, see `API_STATUS_AND_ROADMAP.md` and `product_specs.md` in the project root.
