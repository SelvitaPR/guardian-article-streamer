import json
import os
from datetime import date, datetime

import boto3
from botocore.exceptions import ClientError

from src.api_client import fetch_guardian_content
from src.publisher import KinesisPublisher
from src.utils import build_search_params

# --- CONFIGURATION (Read from Environment Variables) ---
# These variables will be set in the Lambda console
SECRET_NAME = os.environ.get("SECRET_NAME") 
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
    
    # --- Caching Check ---
    if CACHED_SECRETS is not None:
        return CACHED_SECRETS
        
    # --- Client Setup ---
    if SECRETS_CLIENT is None:
        session = boto3.session.Session()
        SECRETS_CLIENT = session.client(
            service_name='secretsmanager',
            region_name=KINESIS_REGION
        )

    # --- Retrieval ---
    try:
        get_secret_value_response = SECRETS_CLIENT.get_secret_value(
            SecretId=SECRET_NAME
        )
    except ClientError as e:
        print(f"ERROR: Failed to retrieve secret '{SECRET_NAME}': {e}")
        raise e

    # --- Parsing and Caching ---
    secret_json_string = get_secret_value_response['SecretString']
    
    CACHED_SECRETS = json.loads(secret_json_string) 

    return CACHED_SECRETS


def lambda_handler(event: dict, context: object):
    """
    AWS Lambda entry point. Orchestrates secret retrieval, data fetch, and Kinesis publish.
    """
    print("--- Lambda Invocation Started ---")
    
    # --- LOAD ALL SECRETS, SECURELY ---
    try:
        secrets = get_secret()
        API_KEY = secrets.get('GUARDIAN_API_KEY')
        API_URL = secrets.get('GUARDIAN_URL')
    except Exception as e:
        print(f"FATAL: Could not initialize secrets: {e}")
        return {'statusCode': 500, 'body': 'Failed to load credentials for execution.'}

    # --- EXTRACT ARGUMENTS FROM EVENT ---
    search_term = event.get('search')
    date_from_str = event.get('date_from')

    if not search_term:
        print("ERROR: 'search' term is missing from the event payload.")
        return {'statusCode': 400, 'body': 'Missing required search parameter'}

    # --- PREPARE DATE CRITERIA (optional date) ---
    if date_from_str:
        try:
            date_obj = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"WARNING: Invalid date format: {date_from_str}. Using today's date.")
            date_obj = date.today()
    else:
        date_obj = date.today()

    # --- BUILD API PARAMETERS ---
    user_criteria = {
        'search_term': search_term,
        'date_from': date_obj
    }
    api_params = build_search_params(user_criteria)

    # --- FETCH CONTENT ---
    print(f"Fetching data for '{search_term}' from {date_obj}...")
    data = fetch_guardian_content(API_URL, api_params, API_KEY) 

    if not data or 'response' not in data or 'results' not in data['response']:
        print("Fetch failed or no data found in response.")
        return {'statusCode': 200, 'body': 'No articles found or API structure was missing.'}

    records_to_publish = data['response']['results']

    # --- INITIALIZE & PUBLISH ---
    print(f"Found {len(records_to_publish)} records. Publishing to Kinesis...")
    
    publisher = KinesisPublisher(
        stream_name=KINESIS_STREAM_NAME, 
        region_name=KINESIS_REGION
    )
    
    publish_response = publisher.publish(records_to_publish)

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
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed or partial failure during Kinesis publish. Check CloudWatch logs for details.'})
        }