import pytest
from unittest.mock import patch, MagicMock
import event_generate_content.dynamo_utils as dynamo_utils

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_get_table_success(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    table = dynamo_utils.get_table('test-table')
    assert table == mock_table
    mock_boto3_resource.assert_called_with('dynamodb')
    mock_boto3_resource.return_value.Table.assert_called_with('test-table')

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_get_table_exception(mock_boto3_resource):
    mock_boto3_resource.side_effect = Exception('fail')
    with pytest.raises(Exception):
        dynamo_utils.get_table('test-table')

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_put_item_success(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    result = dynamo_utils.put_item('test-table', {'id': '1'})
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    mock_table.put_item.assert_called_with(Item={'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_put_item_exception(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.put_item.side_effect = Exception('fail')
    with pytest.raises(Exception):
        dynamo_utils.put_item('test-table', {'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_get_item_success(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.get_item.return_value = {'Item': {'id': '1'}}
    result = dynamo_utils.get_item('test-table', {'id': '1'})
    assert result['Item']['id'] == '1'
    mock_table.get_item.assert_called_with(Key={'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_get_item_exception(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.get_item.side_effect = Exception('fail')
    with pytest.raises(Exception):
        dynamo_utils.get_item('test-table', {'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_update_item_success(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.return_value = {'Attributes': {'id': '1'}}
    result = dynamo_utils.update_item('test-table', {'id': '1'}, 'SET #n = :v', {'#n': 'name'}, {':v': 'value'})
    assert result['Attributes']['id'] == '1'
    mock_table.update_item.assert_called_with(
        Key={'id': '1'},
        UpdateExpression='SET #n = :v',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={':v': 'value'},
        ReturnValues='ALL_NEW'
    )

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_update_item_exception(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.side_effect = Exception('fail')
    with pytest.raises(Exception):
        dynamo_utils.update_item('test-table', {'id': '1'}, 'SET #n = :v', {'#n': 'name'}, {':v': 'value'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_delete_item_success(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    result = dynamo_utils.delete_item('test-table', {'id': '1'})
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    mock_table.delete_item.assert_called_with(Key={'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.resource')
def test_delete_item_exception(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.delete_item.side_effect = Exception('fail')
    with pytest.raises(Exception):
        dynamo_utils.delete_item('test-table', {'id': '1'})

@patch('event_generate_content.dynamo_utils.boto3.client')
@patch('event_generate_content.dynamo_utils.os.environ', {'NODES_TABLE_NAME': 'TestNodes', 'EVENT_BUS_NAME': 'TestBus'})
def test_update_node_with_content_success(mock_boto3):
    mock_dynamodb = MagicMock()
    mock_events = MagicMock()
    def client_side_effect(service):
        if service == 'dynamodb':
            return mock_dynamodb
        elif service == 'events':
            return mock_events
        raise Exception('Unknown service')
    mock_boto3.side_effect = client_side_effect
    mock_dynamodb.update_item.return_value = {}
    mock_events.put_events.return_value = {'FailedEntryCount': 0}
    dynamo_utils.update_node_with_content('n1', 's1', 's3key')
    mock_dynamodb.update_item.assert_called()
    mock_events.put_events.assert_called()

@patch('event_generate_content.dynamo_utils.boto3.client')
@patch('event_generate_content.dynamo_utils.os.environ', {'NODES_TABLE_NAME': 'TestNodes', 'EVENT_BUS_NAME': 'TestBus'})
def test_update_node_with_content_dynamodb_fail(mock_boto3):
    mock_dynamodb = MagicMock()
    mock_events = MagicMock()
    def client_side_effect(service):
        if service == 'dynamodb':
            return mock_dynamodb
        elif service == 'events':
            return mock_events
        raise Exception('Unknown service')
    mock_boto3.side_effect = client_side_effect
    mock_dynamodb.update_item.side_effect = Exception('ddb fail')
    with pytest.raises(Exception):
        dynamo_utils.update_node_with_content('n1', 's1', 's3key')

@patch('event_generate_content.dynamo_utils.boto3.client')
@patch('event_generate_content.dynamo_utils.os.environ', {'NODES_TABLE_NAME': 'TestNodes', 'EVENT_BUS_NAME': 'TestBus'})
def test_update_node_with_content_eventbridge_fail(mock_boto3):
    mock_dynamodb = MagicMock()
    mock_events = MagicMock()
    def client_side_effect(service):
        if service == 'dynamodb':
            return mock_dynamodb
        elif service == 'events':
            return mock_events
        raise Exception('Unknown service')
    mock_boto3.side_effect = client_side_effect
    mock_dynamodb.update_item.return_value = {}
    mock_events.put_events.side_effect = Exception('eventbridge fail')
    with pytest.raises(Exception):
        dynamo_utils.update_node_with_content('n1', 's1', 's3key')
