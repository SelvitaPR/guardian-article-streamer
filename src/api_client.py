import os
import requests
import json
# import csv
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("GUARDIAN_API_KEY")
API_URL=os.getenv("GUARDIAN_URL")

def connect_to_guardian(url, auth=API_KEY):
    """
    Connects to the Guardian API and returns the JSON response.
    """
    response = requests.get(url, auth=(API_KEY, ""))
    if response.status_code == 200:
        print("Status code:", response.status_code)
        return response.json()
    elif response.status_code == 401:
        print("Error: Unauthorized. Check your API key.")
    else:
        print(f"Error: Received status code {response.status_code}")
        print("Response:", response.text)
    return None

if __name__ == '__main__':
    data = connect_to_guardian(API_URL, API_KEY)
    if data:
        with open("api_response.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("job done")
