import os
import time
import uuid
import requests
import boto3

def test_node_content_s3():
    # --- 1. Create a node via API ---
    api_url = "https://b5gm8qyv5h.execute-api.us-east-1.amazonaws.com/dev/spaces/{spaceId}/nodes"
    space_id = str(uuid.uuid4())
    node_title = f"Test Node {uuid.uuid4().hex[:6]}"
    url = api_url.replace("{spaceId}", space_id)
    payload = {"title": node_title}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 201, f"Node creation failed: {response.text}"
    node = response.json()
    node_id = node.get("nodeId") or node.get("id")
    assert node_id, "Node ID not found in response"

    # --- 2. Wait for content generation (poll S3 for up to 90 seconds) ---
    bucket = "serverless-framework-deployments-us-east-1-bdfd491e-cce3"
    s3 = boto3.client("s3")
    key = f"nodes/{space_id}/{node_id}/content.html"
    content = None
    for _ in range(30):  # Try for up to 90 seconds
        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            content = obj["Body"].read().decode("utf-8")
            break
        except s3.exceptions.NoSuchKey:
            time.sleep(3)
    assert content is not None, f"Content not found in S3 at {key} after waiting."

    # --- 3. Print the content ---
    print("\n===== AI Generated Content from S3 =====\n")
    print(content)
    print("\n=======================================\n")

if __name__ == "__main__":
    test_node_content_s3()
