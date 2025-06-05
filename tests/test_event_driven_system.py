#!/usr/bin/env python3
"""
Comprehensive test for the event-driven content generation system.
Tests the integration between the main CRUD API and the content generator Lambda.
"""

import os
import time
import uuid
import json
import boto3
import requests
from datetime import datetime
from config import API_BASE_URL

class EventDrivenSystemTester:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.events_client = boto3.client('events', region_name='us-east-1')
        self.cloudwatch_logs = boto3.client('logs', region_name='us-east-1')
        
        # Table and resource names from the deployed system
        self.nodes_table_name = "mindmap-explorer-sls-dev-nodes"
        self.spaces_table_name = "mindmap-explorer-sls-dev-spaces"
        self.event_bus_name = "mindmap-events-bus-dev"
        
        # Lambda function name for content generator
        self.content_generator_function = "mindmap-content-generator-dev-generateNodeContent"
        
        print(f"🚀 Testing Event-Driven System")
        print(f"📍 API Base URL: {self.api_base_url}")
        print(f"📊 Nodes Table: {self.nodes_table_name}")
        print(f"📨 Event Bus: {self.event_bus_name}")
        print(f"⚡ Content Generator: {self.content_generator_function}")
        print("-" * 60)

    def create_test_space(self):
        """Create a test space for our nodes."""
        print("📁 Creating test space...")
        
        space_payload = {
            "name": f"Event Test Space {datetime.now().strftime('%H:%M:%S')}",
            "description": "Test space for event-driven content generation"
        }
        
        response = requests.post(
            f"{self.api_base_url}/spaces",
            json=space_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            space_data = response.json()
            space_id = space_data['spaceId']
            print(f"✅ Space created: {space_id}")
            return space_id
        else:
            raise Exception(f"Failed to create space: {response.status_code} - {response.text}")

    def create_test_node(self, space_id, include_content=False):
        """Create a test node that should trigger content generation."""
        print(f"📄 Creating test node in space {space_id}...")
        
        node_payload = {
            "title": f"Event Test Node {datetime.now().strftime('%H:%M:%S')}",
            "orderIndex": 1
        }
        
        # Only add content if specified (when content is provided, AI generation is skipped)
        if include_content:
            node_payload["contentHTML"] = "<p>This node has pre-existing content</p>"
        
        response = requests.post(
            f"{self.api_base_url}/spaces/{space_id}/nodes",
            json=node_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            node_data = response.json()
            node_id = node_data['nodeId']
            has_content = 'contentHTML' in node_payload
            print(f"✅ Node created: {node_id} (content provided: {has_content})")
            return node_id, node_data
        else:
            raise Exception(f"Failed to create node: {response.status_code} - {response.text}")

    def check_event_bus_rules(self):
        """Check if EventBridge rules are properly configured."""
        print("🔍 Checking EventBridge configuration...")
        
        try:
            # List rules for our event bus
            response = self.events_client.list_rules(EventBusName=self.event_bus_name)
            rules = response.get('Rules', [])
            
            print(f"📋 Found {len(rules)} rules on event bus '{self.event_bus_name}':")
            for rule in rules:
                print(f"   - {rule['Name']} (State: {rule['State']})")
                
                # Get targets for this rule
                targets_response = self.events_client.list_targets_by_rule(
                    Rule=rule['Name'],
                    EventBusName=self.event_bus_name
                )
                targets = targets_response.get('Targets', [])
                for target in targets:
                    if 'lambda' in target.get('Arn', '').lower():
                        print(f"     → Lambda: {target['Arn'].split(':')[-1]}")
                        
            return len(rules) > 0
            
        except Exception as e:
            print(f"❌ Error checking event bus: {e}")
            return False

    def wait_for_content_generation(self, space_id, node_id, max_wait_time=60):
        """Wait for the content generation Lambda to process the event."""
        print(f"⏳ Waiting for content generation for node {node_id}...")
        
        table = self.dynamodb.Table(self.nodes_table_name)
        start_time = time.time()
        check_interval = 5
        
        while time.time() - start_time < max_wait_time:
            try:
                # Get the node from DynamoDB
                response = table.get_item(
                    Key={
                        'nodeId': node_id,
                        'spaceId': space_id
                    }
                )
                
                if 'Item' in response:
                    item = response['Item']
                    
                    # Check for content generation indicators
                    content_indicators = [
                        'contentS3Key',
                        'generatedContent', 
                        'aiGeneratedContent',
                        'contentPreview'
                    ]
                    
                    generated_content = False
                    for indicator in content_indicators:
                        if indicator in item and item[indicator]:
                            print(f"✅ Content generated! Found: {indicator} = {item[indicator]}")
                            generated_content = True
                            break
                    
                    if generated_content:
                        return True, item
                    
                    # Show current state
                    available_fields = [k for k in item.keys() if k not in ['nodeId', 'spaceId', 'title']]
                    print(f"⏱️  Still waiting... Current fields: {available_fields}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error checking node: {e}")
                time.sleep(check_interval)
        
        print(f"⏰ Timeout after {max_wait_time} seconds")
        return False, None

    def check_lambda_logs(self, function_name, start_time):
        """Check CloudWatch logs for the Lambda function."""
        print(f"📜 Checking logs for {function_name}...")
        
        try:
            log_group_name = f"/aws/lambda/{function_name}"
            
            # Get log streams
            streams_response = self.cloudwatch_logs.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )
            
            for stream in streams_response.get('logStreams', []):
                if stream['lastEventTime'] >= start_time * 1000:  # Convert to milliseconds
                    print(f"📖 Recent log stream: {stream['logStreamName']}")
                    
                    # Get log events
                    events_response = self.cloudwatch_logs.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        startTime=int(start_time * 1000)
                    )
                    
                    for event in events_response.get('events', [])[-10:]:  # Last 10 events
                        timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                        message = event['message'].strip()
                        print(f"   {timestamp}: {message}")
                    
                    break
            else:
                print("📭 No recent log streams found")
                
        except Exception as e:
            print(f"❌ Error checking logs: {e}")

    def test_event_system_end_to_end(self):
        """Run the complete end-to-end test."""
        test_start_time = time.time()
        
        try:
            # Step 1: Check EventBridge configuration
            if not self.check_event_bus_rules():
                print("⚠️  Warning: No EventBridge rules found, but continuing test...")
            
            # Step 2: Create test space
            space_id = self.create_test_space()
            
            # Step 3: Create node WITHOUT content (should trigger AI generation)
            node_id, node_data = self.create_test_node(space_id, include_content=False)
            
            # Step 4: Wait for content generation
            content_generated, updated_node = self.wait_for_content_generation(space_id, node_id)
            
            # Step 5: Check Lambda logs
            self.check_lambda_logs(self.content_generator_function, test_start_time)
            
            # Step 6: Report results
            if content_generated:
                print("\n" + "=" * 60)
                print("🎉 SUCCESS: Event-driven content generation is working!")
                print(f"✅ Node {node_id} received generated content")
                print(f"📊 Final node data: {json.dumps(updated_node, indent=2, default=str)}")
                print("=" * 60)
                return True
            else:
                print("\n" + "=" * 60)
                print("❌ FAILURE: Content generation did not complete")
                print("🔍 Possible issues:")
                print("   - EventBridge rule not triggering")
                print("   - Content generator Lambda failing")
                print("   - DynamoDB update not happening")
                print("   - Bedrock API issues")
                print("=" * 60)
                return False
                
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            return False

    def test_with_existing_content(self):
        """Test that nodes with existing content don't trigger generation."""
        print("\n🔬 Testing node with existing content (should NOT trigger AI generation)...")
        
        try:
            space_id = self.create_test_space()
            node_id, node_data = self.create_test_node(space_id, include_content=True)
            
            # Wait a short time and verify content wasn't changed
            time.sleep(10)
            
            table = self.dynamodb.Table(self.nodes_table_name)
            response = table.get_item(Key={'nodeId': node_id, 'spaceId': space_id})
            
            if 'Item' in response:
                item = response['Item']
                # Should still have the original content, not AI-generated
                has_ai_content = any(key in item for key in ['contentS3Key', 'generatedContent', 'aiGeneratedContent'])
                
                if not has_ai_content:
                    print("✅ Correct: Node with existing content did not trigger AI generation")
                    return True
                else:
                    print("⚠️  Warning: Node with existing content triggered AI generation (unexpected)")
                    return False
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False


def main():
    """Run all tests."""
    tester = EventDrivenSystemTester()
    
    print("🧪 Starting Event-Driven System Tests")
    print("=" * 60)
    
    # Test 1: End-to-end event system
    success1 = tester.test_event_system_end_to_end()
    
    # Test 2: Existing content behavior
    success2 = tester.test_with_existing_content()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"🎯 End-to-end test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"🔒 Existing content test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED - Event system is working correctly!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Check the output above for details")
        return 1


if __name__ == "__main__":
    exit(main())
