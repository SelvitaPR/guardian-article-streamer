import argparse
import json
import os

from dotenv import load_dotenv

from src.api_client import fetch_guardian_content
from src.publisher import LocalPublisher
from src.utils import build_search_params, process_and_print_results

# --- LOCAL CREDENTIAL LOADING ---
load_dotenv()
API_KEY_LOCAL = os.getenv("GUARDIAN_API_KEY")
API_URL_LOCAL = os.getenv("GUARDIAN_URL")

# --- KINESIS CONFIGURATION (Uses local .env defaults) ---
KINESIS_STREAM_NAME = os.getenv("KINESIS_STREAM_NAME")
KINESIS_REGION = os.getenv("KINESIS_REGION")
# --------------------------------------------------------


parser = argparse.ArgumentParser(
    prog="GuardianArticleStreamer",
    description="Fetches articles from the Guardian API based on search terms and publishes up to 10 of the most recent results.",
)
parser.add_argument("--search", help="term you'd like to search for")
parser.add_argument(
    "--date_from",
    help="date you'd like to search articles from (YYYY-MM-DD). Defaults to today.",
    default=None,
)

if __name__ == "__main__":
    from datetime import date, datetime

    args = parser.parse_args()

    # Convert Arguments to Criteria (Handling Optional Date)
    if args.date_from is None or args.date_from.strip() == "":
        date_obj = date.today()
        date_used_str = "today"
    else:
        try:
            date_obj = datetime.strptime(args.date_from, "%Y-%m-%d").date()
            date_used_str = args.date_from
        except ValueError:  # user types wrong format
            print(
                f"\nError: Invalid date format '{args.date_from}'. Please use YYYY-MM-DD."
            )
            exit(1)

    # Final check for search term
    if args.search is None:
        print("\nError: The --search term is mandatory. Please provide a query.")
        exit(1)

    # Create the dictionary for build_search_params
    user_criteria = {"search_term": args.search, "date_from": date_obj}

    # Format Parameters for API
    api_params = build_search_params(user_criteria)

    # Fetch Content
    print(
        f"--- Searching Guardian for '{user_criteria['search_term']}' from {date_used_str} ---"
    )
    data = fetch_guardian_content(API_URL_LOCAL, api_params, API_KEY_LOCAL)

    # Process, Print, and Publish Results
    if data:
        records_to_publish = data["response"].get("results", [])

        publisher = LocalPublisher(
            stream_name=KINESIS_STREAM_NAME, region_name=KINESIS_REGION
        )

        publisher.publish(records_to_publish)

        # Print locally for confirmation
        process_and_print_results(data)
    else:
        print("Search failed or returned no data.")
