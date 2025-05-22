import requests
import pytest
from tests.config import API_BASE_URL

# Helper to print request/response verbosely
def verbose_print(label, value):
    print(f"\n{'='*20} {label} {'='*20}\n{value}\n{'='*50}")

@pytest.fixture(scope="module")
def test_space():
    # Create a space for node tests
    url = f"{API_BASE_URL}/spaces"
    payload = {
        "name": "Node Test Space",
        "description": "For node API tests",
        "ownerId": "pytest_user"
    }
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    space_id = resp.json()["spaceId"]
    yield space_id
    # Cleanup
    requests.delete(f"{API_BASE_URL}/spaces/{space_id}")

def test_add_get_update_delete_node(test_space):
    space_id = test_space
    # Add node
    url = f"{API_BASE_URL}/spaces/{space_id}/nodes"
    payload = {
        "title": "Root Node",
        "content": "Main idea",
        "s3Key": None,
        "parentNodeId": None,
        "orderIndex": 0
    }
    verbose_print("POST /spaces/{spaceId}/nodes Payload", payload)
    resp = requests.post(url, json=payload)
    verbose_print("POST /spaces/{spaceId}/nodes Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    node = resp.json()
    node_id = node["nodeId"]

    # Get node
    get_url = f"{API_BASE_URL}/spaces/{space_id}/nodes/{node_id}"
    resp = requests.get(get_url)
    verbose_print("GET /spaces/{spaceId}/nodes/{nodeId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    assert resp.json()["nodeId"] == node_id

    # Update node
    update_url = f"{API_BASE_URL}/spaces/{space_id}/nodes/{node_id}"
    update_payload = {"title": "Updated Node", "content": "Updated content"}
    resp = requests.put(update_url, json=update_payload)
    verbose_print("PUT /spaces/{spaceId}/nodes/{nodeId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Node"

    # Delete node
    del_url = f"{API_BASE_URL}/spaces/{space_id}/nodes/{node_id}"
    resp = requests.delete(del_url)
    verbose_print("DELETE /spaces/{spaceId}/nodes/{nodeId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200

    # Confirm deleted
    resp = requests.get(get_url)
    verbose_print("GET /spaces/{spaceId}/nodes/{nodeId} after delete Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 404

def test_recursive_node_deletion(test_space):
    space_id = test_space
    # Add root node
    url = f"{API_BASE_URL}/spaces/{space_id}/nodes"
    root_payload = {
        "title": "Root",
        "content": "Root node",
        "s3Key": None,
        "parentNodeId": None,
        "orderIndex": 0
    }
    resp = requests.post(url, json=root_payload)
    assert resp.status_code == 200
    root_id = resp.json()["nodeId"]
    # Add child node
    child_payload = {
        "title": "Child",
        "content": "Child node",
        "s3Key": None,
        "parentNodeId": root_id,
        "orderIndex": 0
    }
    resp = requests.post(url, json=child_payload)
    assert resp.status_code == 200
    child_id = resp.json()["nodeId"]
    # Delete root node (should delete child too)
    del_url = f"{API_BASE_URL}/spaces/{space_id}/nodes/{root_id}"
    resp = requests.delete(del_url)
    verbose_print("DELETE /spaces/{spaceId}/nodes/{root_id} (recursive) Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    # Confirm both deleted
    resp = requests.get(f"{API_BASE_URL}/spaces/{space_id}/nodes/{root_id}")
    assert resp.status_code == 404
    resp = requests.get(f"{API_BASE_URL}/spaces/{space_id}/nodes/{child_id}")
    assert resp.status_code == 404
