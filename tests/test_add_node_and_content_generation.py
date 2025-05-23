import os
import time
import uuid
import boto3
import requests
import pytest

def test_add_node_and_content_generation():
    # Setup
    api_url = "https://b5gm8qyv5h.execute-api.us-east-1.amazonaws.com/dev/spaces/{spaceId}/nodes"
    space_id = str(uuid.uuid4())
    node_title = f"Test Node {uuid.uuid4().hex[:6]}"
    
    # Prepare request
    url = api_url.replace("{spaceId}", space_id)
    payload = {
        "title": node_title
    }
    headers = {"Content-Type": "application/json"}

    # Call the API to add a node
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 201, f"Node creation failed: {response.text}"
    node_data = response.json()
    node_id = node_data["nodeId"]

    # Wait for content generation Lambda to process (poll DynamoDB for s3Key)
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("NODES_TABLE_NAME", "mindmap-explorer-sls-dev-nodes")
    table = dynamodb.Table(table_name)
    max_attempts = 12
    wait_time = 5
    found_content = False
    for attempt in range(max_attempts):
        time.sleep(wait_time)
        item = table.get_item(Key={"nodeId": node_id, "spaceId": space_id}).get("Item")
        if item and ("s3Key" in item or "contentPreview" in item):
            found_content = True
            print(f"Content generated for node: {item.get('s3Key', item.get('contentPreview'))}")
            break
        print(f"Attempt {attempt+1}: Content not generated yet, waiting...")
    assert found_content, "Content generation Lambda did not update the node with content."
    print("Test passed: Node created and content generated.")

if __name__ == "__main__":
    test_add_node_and_content_generation()
