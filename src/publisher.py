import json
from typing import Any, Dict, List

import boto3


class KinesisPublisher:
    """
    A class responsible for publishing records to an AWS Kinesis Data Stream.
    
    It uses the boto3 client and the put_records API call for batch publishing.
    """

    def __init__(self, stream_name: str, region_name: str = 'eu-west-2'):
        """
        Initializes the Kinesis client.
        
        Args:
            stream_name: The name of the Kinesis Stream to publish to.
            region_name: The AWS region where the Kinesis stream resides.
        """
        self.stream_name = stream_name
        # Initialize the client immediately for reuse across publish calls
        self.client = boto3.client('kinesis', region_name=region_name)

    def publish(self, records: List[Dict[str, Any]]):
        """
        Publishes a list of records (articles) to the configured Kinesis stream.
        
        The records argument should be the clean list of article dictionaries 
        extracted from the Guardian API response.
        
        args:
            records: A list of dictionaries, where each dictionary is an article.
        return:
            The response from the Kinesis service, or None on failure.
        """
        if not records:
            print("No records provided to publish.")
            return None

        # Kinesis put_records requires the data to be bytes and a PartitionKey.
        # We transform the list of dictionaries into the required Kinesis format.
        kinesis_records = []
        for i, record in enumerate(records):
            # Convert dictionary record to a JSON string, then encode to bytes.
            data_bytes = json.dumps(record).encode('utf-8')
            
            # The PartitionKey is crucial for shard distribution. We use the
            # article's URL or a unique index as a predictable, high-cardinality key.
            partition_key = record.get('webUrl', f'record-{i}')
            
            kinesis_records.append({
                'Data': data_bytes,
                'PartitionKey': partition_key
            })

        print(f"Attempting to publish {len(kinesis_records)} records to stream '{self.stream_name}'...")

        try:
            # The API call for batch publishing
            response = self.client.put_records(
                Records=kinesis_records,
                StreamName=self.stream_name
            )
            
            # Check for failed records (a common scenario in Kinesis)
            failed_count = response.get('FailedRecordCount', 0)
            if failed_count > 0:
                print(f"Warning: {failed_count} records failed to publish.")
            else:
                print("Success: All records published.")
            
            return response

        except Exception as e:
            print(f"Error publishing to Kinesis stream '{self.stream_name}': {e}")
            return None