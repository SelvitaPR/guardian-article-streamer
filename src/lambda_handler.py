#entry point for lambda
#Responsibility: Same orchestration as cli.py, but triggered by AWS.
#Keep it thin — it should just parse the Lambda event, call into your existing functions, and return a response.

import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, date
import json

# Import the core business logic components
from src.api_client import fetch_guardian_content
from src.utils import build_search_params
from src.publisher import KinesisPublisher 

# --- CONFIGURATION (Read from Environment Variables) ---
# These variables will be set in the Lambda console
SECRET_NAME = os.environ.get("SECRET_NAME", "guardian/article/streamer/api/credentials") 
KINESIS_STREAM_NAME = os.environ.get("KINESIS_STREAM_NAME") 
KINESIS_REGION = os.environ.get("KINESIS_REGION")
# ---------------------------------------------

# Global variables for caching (runs once per container lifecycle)
CACHED_SECRETS = None
SECRETS_CLIENT = None


def get_secret():
    """
    Retrieves and caches the secret value (a JSON string) from AWS Secrets Manager.
    
    The JSON string is parsed into a dictionary containing the API_KEY and API_URL.
    """
    global CACHED_SECRETS, SECRETS_CLIENT
    
    # --- 1. Caching Check (High performance for warm containers) ---
    if CACHED_SECRETS is not None:
        return CACHED_SECRETS
        
    # --- 2. Client Setup ---
    if SECRETS_CLIENT is None:
        session = boto3.session.Session()
        # Client setup uses the region configured in the Lambda environment
        SECRETS_CLIENT = session.client(
            service_name='secretsmanager',
            region_name=KINESIS_REGION
        )

    # --- 3. Retrieval ---
    try:
        get_secret_value_response = SECRETS_CLIENT.get_secret_value(
            SecretId=SECRET_NAME
        )
    except ClientError as e:
        # Crucial for IAM and troubleshooting: logs failure before halting
        print(f"ERROR: Failed to retrieve secret '{SECRET_NAME}': {e}")
        raise e

    # --- 4. Parsing and Caching ---
    secret_json_string = get_secret_value_response['SecretString']
    
    # Parse the secret JSON (e.g., '{"GUARDIAN_API_KEY": "...", "GUARDIAN_URL": "..."}')
    CACHED_SECRETS = json.loads(secret_json_string) 

    return CACHED_SECRETS


def lambda_handler(event: dict, context: object):
    """
    AWS Lambda entry point. Orchestrates secret retrieval, data fetch, and Kinesis publish.
    """
    print("--- Lambda Invocation Started ---")
    
    # --- 1. SECURELY LOAD ALL SECRETS ---
    try:
        secrets = get_secret()
        API_KEY = secrets.get('GUARDIAN_API_KEY')
        API_URL = secrets.get('GUARDIAN_URL')
    except Exception as e:
        print(f"FATAL: Could not initialize secrets: {e}")
        return {'statusCode': 500, 'body': 'Failed to load credentials for execution.'}

    # --- 2. EXTRACT ARGUMENTS FROM EVENT ---
    search_term = event.get('search')
    date_from_str = event.get('date_from')

    if not search_term:
        print("ERROR: 'search' term is missing from the event payload.")
        return {'statusCode': 400, 'body': 'Missing required search parameter'}

    # --- 3. PREPARE DATE CRITERIA (Handles optional date) ---
    if date_from_str:
        try:
            date_obj = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"WARNING: Invalid date format: {date_from_str}. Using today's date.")
            date_obj = date.today()
    else:
        date_obj = date.today()

    # --- 4. BUILD API PARAMETERS ---
    user_criteria = {
        'search_term': search_term,
        'date_from': date_obj
    }
    api_params = build_search_params(user_criteria)

    # --- 5. FETCH CONTENT (Pass dynamic URL and Key) ---
    print(f"Fetching data for '{search_term}' from {date_obj}...")
    data = fetch_guardian_content(API_URL, api_params, API_KEY) 

    if not data or 'response' not in data or 'results' not in data['response']:
        print("Fetch failed or no data found in response.")
        return {'statusCode': 200, 'body': 'No articles found or API structure was missing.'}

    records_to_publish = data['response']['results']

    # --- 6. INITIALIZE & PUBLISH ---
    print(f"Found {len(records_to_publish)} records. Publishing to Kinesis...")
    
    # KinesisPublisher automatically initializes the boto3 client using the region
    publisher = KinesisPublisher(
        stream_name=KINESIS_STREAM_NAME, 
        region_name=KINESIS_REGION
    )
    
    publish_response = publisher.publish(records_to_publish)

    # --- 7. RETURN STATUS ---
    if publish_response and publish_response.get('FailedRecordCount', 0) == 0:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Successfully published {len(records_to_publish)} records.",
                'kinesis_response_summary': {
                    'FailedRecordCount': publish_response.get('FailedRecordCount')
                }
            })
        }
    else:
        # Handles partial failure or complete Kinesis client error
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed or partial failure during Kinesis publish. Check CloudWatch logs for details.'})
        }