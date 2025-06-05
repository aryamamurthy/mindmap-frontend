import os
import time
import uuid
import boto3
import requests
import pytest

def test_add_node_and_event_driven_content():
    # Create a space first
    space_url = "https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod/spaces/"
    space_payload = {
        "name": f"Test Space {uuid.uuid4().hex[:6]}",
        "description": "Test space for event-driven content generation",
        "ownerId": "test_user"
    }
    space_response = requests.post(space_url, json=space_payload)
    assert space_response.status_code == 201, f"Space creation failed: {space_response.text}"
    space_id = space_response.json()["spaceId"]

    # Now add a node to the created space WITHOUT contentHTML
    api_url = f"https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod/spaces/{space_id}/nodes"
    node_title = f"Test Node {uuid.uuid4().hex[:6]}"
    payload = {"title": node_title}
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    assert response.status_code == 201, f"Node creation failed: {response.text}"
    node_data = response.json()
    node_id = node_data["nodeId"]

    # For event-driven, wait for content to be generated (look for s3Key or contentPreview)
    dynamodb = boto3.resource("dynamodb")
    table_name = "MindMapNodes"  # Use your actual table name
    table = dynamodb.Table(table_name)
    max_attempts = 12
    wait_time = 5
    found_content = False
    for attempt in range(max_attempts):
        time.sleep(wait_time)
        item = table.get_item(Key={"nodeId": node_id, "spaceId": space_id}).get("Item")
        if item and ("s3Key" in item or "contentPreview" in item):
            found_content = True
            print(f"Event-driven content for node: {item.get('s3Key', item.get('contentPreview'))}")
            break
        print(f"Attempt {attempt+1}: Event-driven content not generated yet, waiting...")
    assert found_content, "Event-driven content generation Lambda did not update the node with content."
    print("Test passed: Node created and event-driven content generated.")

if __name__ == "__main__":
    test_add_node_and_event_driven_content()
