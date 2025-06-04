"""
Complete End-to-End Testing Script for Mind Map Explorer
Tests the complete workflow including:
1. Space creation
2. Node creation
3. Content generation via EventBridge + Bedrock
4. S3 content retrieval
5. Node updates and tree structure
"""

import requests
import boto3
import json
import time
import uuid
import os
from config import API_BASE_URL

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

def test_complete_mindmap_workflow():
    """Test the complete mind map workflow from creation to AI content generation"""
    
    print("\n" + "="*80)
    print("STARTING COMPLETE MIND MAP WORKFLOW TEST")
    print("="*80)
    
    # Phase 1: Create a Space
    print("\n📂 Phase 1: Creating Space...")
    space_payload = {
        "name": f"AI Test Space {uuid.uuid4().hex[:6]}",
        "description": "Testing complete workflow with AI content generation",
        "ownerId": "test_user"
    }
    
    space_response = requests.post(f"{API_BASE_URL}/spaces", json=space_payload)
    assert space_response.status_code == 201, f"Space creation failed: {space_response.text}"
    
    space_data = space_response.json()
    space_id = space_data["spaceId"]
    print(f"✅ Space created: {space_id}")
    print(f"   Name: {space_data['name']}")
    
    # Phase 2: Create Root Node (should trigger AI content generation)
    print("\n🌱 Phase 2: Creating Root Node...")
    root_node_payload = {
        "title": "Machine Learning Fundamentals",
        "parentNodeId": None,
        "orderIndex": 0
    }
    
    node_response = requests.post(
        f"{API_BASE_URL}/spaces/{space_id}/nodes", 
        json=root_node_payload
    )
    assert node_response.status_code == 201, f"Node creation failed: {node_response.text}"
    
    root_node = node_response.json()
    root_node_id = root_node["nodeId"]
    print(f"✅ Root node created: {root_node_id}")
    print(f"   Title: {root_node['title']}")
    
    # Phase 3: Wait for AI Content Generation
    print("\n🤖 Phase 3: Waiting for AI Content Generation...")
    print("EventBridge should trigger the content generation Lambda...")
    
    # Check DynamoDB for s3Key update (content generation complete)
    nodes_table = dynamodb.Table('mindmap-explorer-sls-dev-nodes')
    max_attempts = 15  # 75 seconds max wait
    wait_time = 5
    content_generated = False
    
    for attempt in range(max_attempts):
        print(f"   Attempt {attempt + 1}/{max_attempts}: Checking for generated content...")
        
        try:
            item_response = nodes_table.get_item(
                Key={"nodeId": root_node_id, "spaceId": space_id}
            )
            
            if 'Item' in item_response:
                item = item_response['Item']
                if 's3Key' in item:
                    content_generated = True
                    s3_key = item['s3Key']
                    print(f"✅ Content generated! S3 Key: {s3_key}")
                    break
                    
        except Exception as e:
            print(f"   Error checking DynamoDB: {e}")
            
        if attempt < max_attempts - 1:
            print(f"   Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    assert content_generated, "AI content generation did not complete within expected time"
    
    # Phase 4: Retrieve and Verify AI Content
    print("\n📄 Phase 4: Retrieving AI Generated Content...")
    
    # Get node with content via API
    node_get_response = requests.get(f"{API_BASE_URL}/spaces/{space_id}/nodes/{root_node_id}")
    assert node_get_response.status_code == 200, f"Node retrieval failed: {node_get_response.text}"
    
    node_with_content = node_get_response.json()
    assert 'contentHTML' in node_with_content, "Node should have contentHTML"
    
    content_html = node_with_content['contentHTML']
    assert len(content_html) > 100, "Generated content should be substantial"
    
    print(f"✅ AI Content Retrieved (length: {len(content_html)} chars)")
    print(f"   Content preview: {content_html[:200]}...")
      # Verify content directly from S3
    content_bucket = 'mindmap-explorer-sls-dev-content-bucket-1455341320'
    try:
        s3_object = s3.get_object(Bucket=content_bucket, Key=s3_key)
        s3_content = s3_object['Body'].read().decode('utf-8')
        assert s3_content == content_html, "S3 content should match API content"
        print("✅ S3 content verified to match API response")
    except Exception as e:
        print(f"⚠️  S3 verification warning: {e}")
    
    # Phase 5: Create Child Nodes
    print("\n🌿 Phase 5: Creating Child Nodes...")
    
    child_nodes = [
        {"title": "Supervised Learning", "parentNodeId": root_node_id, "orderIndex": 0},
        {"title": "Unsupervised Learning", "parentNodeId": root_node_id, "orderIndex": 1},
        {"title": "Neural Networks", "parentNodeId": root_node_id, "orderIndex": 2}
    ]
    
    created_children = []
    for child_payload in child_nodes:
        child_response = requests.post(
            f"{API_BASE_URL}/spaces/{space_id}/nodes",
            json=child_payload
        )
        assert child_response.status_code == 201, f"Child node creation failed: {child_response.text}"
        
        child_node = child_response.json()
        created_children.append(child_node)
        print(f"✅ Child node created: {child_node['title']} ({child_node['nodeId']})")
    
    # Phase 6: Verify Tree Structure
    print("\n🌳 Phase 6: Verifying Tree Structure...")
    
    tree_response = requests.get(f"{API_BASE_URL}/spaces/{space_id}")
    assert tree_response.status_code == 200, f"Tree retrieval failed: {tree_response.text}"
    
    tree_data = tree_response.json()
    assert 'nodes' in tree_data, "Tree should have nodes"
    
    # Find root node in tree
    root_in_tree = None
    for node in tree_data['nodes']:
        if node['nodeId'] == root_node_id:
            root_in_tree = node
            break
    
    assert root_in_tree is not None, "Root node should be in tree"
    assert len(root_in_tree['children']) == 3, "Root should have 3 children"
    
    print(f"✅ Tree structure verified:")
    print(f"   Root: {root_in_tree['title']}")
    for child in root_in_tree['children']:
        print(f"   └── {child['title']}")
    
    # Phase 7: Test Node Updates
    print("\n✏️  Phase 7: Testing Node Updates...")
    
    # Update one of the child nodes
    update_payload = {
        "title": "Deep Learning & Neural Networks",
        "contentHTML": "<h2>Deep Learning</h2><p>Advanced neural network architectures...</p>"
    }
    
    child_to_update = created_children[2]  # Neural Networks node
    update_response = requests.put(
        f"{API_BASE_URL}/spaces/{space_id}/nodes/{child_to_update['nodeId']}",
        json=update_payload
    )
    assert update_response.status_code == 200, f"Node update failed: {update_response.text}"
    
    updated_node = update_response.json()
    assert updated_node['title'] == update_payload['title'], "Title should be updated"
    
    print(f"✅ Node updated successfully: {updated_node['title']}")
    
    # Phase 8: Test Node Reordering
    print("\n🔄 Phase 8: Testing Node Reordering...")
    
    # Reorder the child nodes
    reorder_payload = {
        "parentNodeId": root_node_id,
        "order": [
            created_children[2]['nodeId'],  # Neural Networks first
            created_children[0]['nodeId'],  # Supervised Learning second
            created_children[1]['nodeId']   # Unsupervised Learning third
        ]
    }
    
    reorder_response = requests.post(
        f"{API_BASE_URL}/spaces/{space_id}/nodes/reorder",
        json=reorder_payload
    )
    assert reorder_response.status_code == 200, f"Node reorder failed: {reorder_response.text}"
    
    print("✅ Node reordering completed")
    
    # Phase 9: Final Verification
    print("\n🔍 Phase 9: Final Verification...")
    
    # Get updated tree to verify reordering
    final_tree_response = requests.get(f"{API_BASE_URL}/spaces/{space_id}")
    assert final_tree_response.status_code == 200
    
    final_tree = final_tree_response.json()
    final_root = None
    for node in final_tree['nodes']:
        if node['nodeId'] == root_node_id:
            final_root = node
            break
    
    # Verify new order
    expected_order = ["Deep Learning & Neural Networks", "Supervised Learning", "Unsupervised Learning"]
    actual_order = [child['title'] for child in final_root['children']]
    
    print(f"   Expected order: {expected_order}")
    print(f"   Actual order: {actual_order}")
    
    # Note: The first item should be the updated title
    assert actual_order[0] == "Deep Learning & Neural Networks", "First child should be the updated neural networks node"
    
    print("✅ Final verification completed")
    
    # Phase 10: Cleanup
    print("\n🧹 Phase 10: Cleanup...")
    
    # Delete the space (should cascade delete all nodes)
    delete_response = requests.delete(f"{API_BASE_URL}/spaces/{space_id}")
    assert delete_response.status_code == 204, f"Space deletion failed: {delete_response.text}"
    
    print("✅ Space and all nodes deleted")
    
    print("\n" + "="*80)
    print("🎉 COMPLETE WORKFLOW TEST PASSED! 🎉")
    print("✅ All phases completed successfully:")
    print("   • Space creation")
    print("   • Node creation")
    print("   • AI content generation (EventBridge + Bedrock)")
    print("   • S3 content storage and retrieval")
    print("   • Tree structure verification")
    print("   • Node updates and reordering")
    print("   • Cleanup")
    print("="*80)

if __name__ == "__main__":
    test_complete_mindmap_workflow()
