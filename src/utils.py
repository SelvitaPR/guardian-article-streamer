import boto3
import os
import json

def get_secret(secret_name):
    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION"))
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
