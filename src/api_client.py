import json
import os
import requests

from typing import Dict, Any


def fetch_guardian_content(api_url: str, params: dict, api_key: str) -> Dict[str, Any] or None:
    """
    Connects to the Guardian API using the given URL, search parameters, and API key.

    Args:
        api_url: The base URL for the Guardian API search endpoint.
        params: Dictionary of query parameters (q, from-date, order-by, etc.).
        api_key: The secure API key retrieved from Secrets Manager.

    Returns:
        The JSON response dictionary if status 200, otherwise None.
    """
    # Create a new dictionary for the request parameters, keep it pure.
    request_params = params.copy()
    request_params['api-key'] = api_key  # Add the required API key

    response = requests.get(api_url, params=request_params) # Use the 'params' argument in requests.get()

    if response.status_code == 200:
        print("Status code:", response.status_code)
        return response.json()
    elif response.status_code == 401:
        print("Error: Unauthorized. Check your API key retrieved from Secrets Manager.")
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
