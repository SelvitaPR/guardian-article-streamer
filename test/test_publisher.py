import json
import unittest
from unittest.mock import MagicMock, call

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.publisher import KinesisPublisher


@pytest.fixture(scope='session')
def stream_name():
    return 'guardian-test-stream'

@pytest.fixture(scope='session')
def sample_records():
    return [
        {'webPublicationDate': '2025-10-01T10:00:00Z', 'webTitle': 'AI Article', 'webUrl': 'https://url/1'},
        {'webPublicationDate': '2025-10-02T11:00:00Z', 'webTitle': 'Space News', 'webUrl': 'https://url/2'}
    ]

class TestKinesisPublisher:
    
    @pytest.mark.parametrize('records', [
        [],
    ])
    def test_handles_empty_records_list(self, mocker, stream_name, records):
        """
        Tests that publish method exits when given an empty list of records."""
       
       # Arrange
        # 1. Mock the client that KinesisPublisher.__init__ creates internally
        mock_client = MagicMock()
        mocker.patch('boto3.client', return_value=mock_client)
        
        # 2. Instantiate the class. Note: We only pass the stream name string here.
        model_instance = KinesisPublisher(stream_name=stream_name, region_name='eu-west-2')
        
        # 3. Patch print to capture output
        mock_print = mocker.patch('builtins.print')

        # Act
        result = model_instance.publish(records)
        
        # Assert
        assert result is None
        
        # Check print output
        mock_print.assert_called_once_with("No records provided to publish.")
        
        # Check client interaction (Crucial TDD check: put_records was NEVER called)
        mock_client.put_records.assert_not_called()
       
    def test_correct_data_transformation_and_call(self, mocker, stream_name, sample_records):
        """
        Tests that input records are correctly transformed (JSON/Bytes/PartitionKey) 
        and passed to the Kinesis client.
        """
        # Arrange
        mock_kinesis_client = MagicMock()
        
        # Set up the Kinesis client to return a successful response with 0 failures
        mock_kinesis_client.put_records.return_value = {
            'FailedRecordCount': 0,
            'Records': [{'SequenceNumber': '1', 'ShardId': '0'}, {'SequenceNumber': '2', 'ShardId': '0'}],
            'EncryptionType': 'NONE'
        }
        mocker.patch('boto3.client', return_value=mock_kinesis_client)
        
        model_instance = KinesisPublisher(stream_name=stream_name, region_name='eu-west-2')
        
        # Define the exact expected structure required by Kinesis
        expected_records_payload = [
            {
                'Data': json.dumps(sample_records[0]).encode('utf-8'),
                'PartitionKey': sample_records[0]['webUrl'] # webUrl as PartitionKey
            },
            {
                'Data': json.dumps(sample_records[1]).encode('utf-8'),
                'PartitionKey': sample_records[1]['webUrl']
            }
        ]

        # Act
        model_instance.publish(sample_records)

        # Assert
        # Verify put_records was called with the correctly formatted data
        mock_kinesis_client.put_records.assert_called_once_with(
            Records=expected_records_payload,
            StreamName=stream_name
        )

    # --- Feature 3: Successful Publish (Simplified check) ---
    
    def test_successful_publish_prints_success(self, mocker, stream_name, sample_records):
        """
        Tests that a successful publish (0 failed records) returns the response 
        and prints the success message.
        """
        # Arrange
        mock_kinesis_client = MagicMock()
        mock_kinesis_client.put_records.return_value = {
            'FailedRecordCount': 0,
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        mocker.patch('boto3.client', return_value=mock_kinesis_client)
        model_instance = KinesisPublisher(stream_name=stream_name)
        mock_print = mocker.patch('builtins.print')

        # Act
        result = model_instance.publish(sample_records)
        
        # Assert
        assert result['FailedRecordCount'] == 0
        mock_print.assert_any_call("Success: All records published.")

    def test_partial_failure_prints_warning(self, mocker, stream_name, sample_records):
        """
        Tests that the function handles a Kinesis response with FailedRecordCount > 0 
        by returning the response and printing a warning.
        """
        # Arrange
        FAILED_COUNT = 1
        mock_kinesis_client = MagicMock()
        mock_kinesis_client.put_records.return_value = {
            'FailedRecordCount': FAILED_COUNT,
            'ResponseMetadata': {'HTTPStatusCode': 200}
            # Kinesis response would also contain ErrorCode and ErrorMessage for failed records
        }
        mocker.patch('boto3.client', return_value=mock_kinesis_client)
        model_instance = KinesisPublisher(stream_name=stream_name, region_name='eu-west-2')
        mock_print = mocker.patch('builtins.print')

        # Act
        result = model_instance.publish(sample_records)
        
        # Assert
        assert result['FailedRecordCount'] == FAILED_COUNT
        # Assert the specific warning message was printed
        mock_print.assert_any_call(f"Warning: {FAILED_COUNT} records failed to publish.")

    # --- Feature 5: Handling Kinesis Client Exception ---
    
    def test_kinesis_client_exception_returns_none(self, mocker, stream_name, sample_records):
        """
        Tests that the function catches a low-level Kinesis error (e.g., connection 
        or permissions error) and returns None.
        """
        # Arrange
        mock_kinesis_client = MagicMock()
        # Configure put_records to raise a ClientError (or any Exception)
        mock_kinesis_client.put_records.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Stream not found'}},
            'PutRecords'
        )
        mocker.patch('boto3.client', return_value=mock_kinesis_client)
        model_instance = KinesisPublisher(stream_name=stream_name, region_name='eu-west-2')
        mock_print = mocker.patch('builtins.print')

        # Act
        result = model_instance.publish(sample_records)
        
        # Assert
        assert result is None
        
        # Check that the error message was printed
        mock_print.assert_any_call(
            f"Error publishing to Kinesis stream '{stream_name}': {mock_kinesis_client.put_records.side_effect}"
        )

if __name__ == '__main__':
    unittest.main()