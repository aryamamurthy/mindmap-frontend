import requests
import pytest
from config import API_BASE_URL
import uuid

# Helper to print request/response verbosely
def verbose_print(label, value):
    print(f"\n{'='*20} {label} {'='*20}\n{value}\n{'='*50}")

def test_create_space():
    url = f"{API_BASE_URL}/spaces"
    payload = {
        "name": "Test Space",
        "description": "Created by pytest",
        "ownerId": "pytest_user"
    }
    verbose_print("POST /spaces Payload", payload)
    resp = requests.post(url, json=payload)
    verbose_print("POST /spaces Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 201
    data = resp.json()
    assert "spaceId" in data

def test_list_spaces():
    url = f"{API_BASE_URL}/spaces"
    resp = requests.get(url)
    verbose_print("GET /spaces Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_space_lifecycle():
    # Create
    url = f"{API_BASE_URL}/spaces"
    payload = {
        "name": "Lifecycle Space",
        "description": "Lifecycle test",
        "ownerId": "pytest_user"
    }
    resp = requests.post(url, json=payload)
    verbose_print("POST /spaces (lifecycle) Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 201
    space = resp.json()
    space_id = space["spaceId"]

    # Get
    get_url = f"{API_BASE_URL}/spaces/{space_id}"
    resp = requests.get(get_url)
    verbose_print("GET /spaces/{spaceId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    assert resp.json()["spaceId"] == space_id

    # Update
    update_url = f"{API_BASE_URL}/spaces/{space_id}"
    update_payload = {"name": "Updated Name", "description": "Updated desc"}
    resp = requests.put(update_url, json=update_payload)
    verbose_print("PUT /spaces/{spaceId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"

    # Delete
    del_url = f"{API_BASE_URL}/spaces/{space_id}"
    resp = requests.delete(del_url)
    verbose_print("DELETE /spaces/{spaceId} Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 204  # No Content response for successful deletion

    # Confirm deleted
    resp = requests.get(get_url)
    verbose_print("GET /spaces/{spaceId} after delete Response", f"Status: {resp.status_code}\nBody: {resp.text}")
    assert resp.status_code == 404
