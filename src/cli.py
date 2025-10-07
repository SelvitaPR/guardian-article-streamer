#GLUE CODE/ORCHESTRATION
#IN THIS FILE, I'M GOING TO CONNECT THE api_client.py(fetcher) WITH THE publisher.py(this publishes JSON messages to any broker)
#ADDTOREADME: Run `python -m src.cli --search "machine learning" --date_from "2023-01-01"` to print 10 most recent articles locally.

import argparse
from src.utils import build_search_params, process_and_print_results
from src.api_client import API_URL, fetch_guardian_content


parser = argparse.ArgumentParser(
                    prog='GuardianArticleStreamer',
                    description='Fetches articles from the Guardian API based on search terms and publishes up to 10 of the most recent results.'
                    )
parser.add_argument('--search', help="term you'd like to search for")
parser.add_argument('--date_from', help="date you'd like to search articles from (YYYY-MM-DD). Defaults to today.",
                    default=None)

if __name__ == '__main__':
    # Ensure date is imported here or globally
    from datetime import datetime, date 
    
    # 1. Parse Arguments
    args = parser.parse_args()
    
    # 2. Convert Arguments to Criteria (Handling Optional Date)
    
    # Check if the user supplied a date
    if args.date_from is None or args.date_from == "":
        # If no date is supplied, set the date object to today's date
        date_obj = date.today() 
        date_used_str = "today" 
    else:
        # If a date IS supplied, attempt conversion (with error handling)
        try:
            date_obj = datetime.strptime(args.date_from, '%Y-%m-%d').date()
            date_used_str = args.date_from
        except ValueError:
            # Handle invalid format for supplied date
            print(f"\nError: Invalid date format '{args.date_from}'. Please use YYYY-MM-DD.")
            exit(1)
            
    # Final check for search term (Good practice for mandatory fields)
    if args.search is None:
        print("\nError: The --search term is mandatory. Please provide a query.")
        exit(1)

    # 3. Create the Python-friendly dictionary expected by build_search_params
    user_criteria = {
        'search_term': args.search,
        'date_from': date_obj # Pass the datetime.date object
    }
    
    # 4. Format Parameters for API (uses your existing utility)
    api_params = build_search_params(user_criteria)

    # 5. Fetch Content (using your existing function)
    print(f"--- Searching Guardian for '{user_criteria['search_term']}' from {date_used_str} ---")
    data = fetch_guardian_content(API_URL, api_params)

    # 6. Process and Print Results
    if data:
        process_and_print_results(data)
    else:
        print("Search failed or returned no data.")

