import os
import requests
import json

from dotenv import load_dotenv
from src.utils import get_user_search_criteria, build_search_params, process_and_print_results


load_dotenv()
API_KEY=os.getenv("GUARDIAN_API_KEY")
API_URL=os.getenv("GUARDIAN_URL")

def fetch_guardian_content(api_url: str, params: dict):
    """
    Connects to the Guardian API using the given URL and search parameters.
    """
    # Create a new dictionary for the request parameters
    request_params = params.copy()
    request_params['api-key'] = API_KEY  # Add the required API key

    # Use the 'params' argument in requests.get()
    response = requests.get(api_url, params=request_params)

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
    
    print("--- Starting Guardian API Fetcher ---")
    
    user_criteria = get_user_search_criteria()
    
    if not user_criteria:
        print("Could not gather search criteria. Exiting.")
        exit()

    api_params = build_search_params(user_criteria)
    
    data = fetch_guardian_content(API_URL, api_params)

    if data:
        process_and_print_results(data)
        with open("api_response.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\nAPI data successfully fetched and saved to api_response.txt.")
        print("Job done.")
