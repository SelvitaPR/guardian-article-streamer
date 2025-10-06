from datetime import datetime, date
import json


def get_user_search_criteria():
    """
    Collects required search_term and date_from data from user for local CLI interaction.
    Return:
    dictionary containing user input
    """
    search_term = input('Search tearm:')
    while True:
        date_from_str = input('Enter date YYYY-MM-DD from when to look articles from (Optional, press Enter for today): ')
        
        try:
            if date_from_str.strip() == '':
                date_from = date.today()
                break
            
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            break
            
        except ValueError:
            print("\n🚨 Invalid date format or date. Please use the YYYY-MM-DD format (e.g., 2024-01-01).")
            
    print('\nSearch criteria successfully generated.')
    
    return {'search_term': search_term.strip(), 'date_from': date_from}

def build_search_params(criteria: dict):
    """
    Transforms user input for search_term and date_from to a dictionary of 
    parameters suitable for the Guardian API fetching.
    """
    date_from_object = criteria['date_from'] 
    date_str = date_from_object.strftime('%Y-%m-%d')
    return {
        'q': criteria['search_term'], 
        'from-date': date_str,
        'order-by': 'newest'
    }

def process_and_print_results(data):
    """Prints the date, title, and URL for each article in the API response."""
    
    if not data or 'response' not in data or 'results' not in data['response']:
        print("No articles found to display.")
        return

    results = data['response']['results']
    
    print("\n--- Extracted Article Data ---")
    
    for i, article in enumerate(results):
        date = article.get('webPublicationDate', 'N/A')
        title = article.get('webTitle', 'N/A')
        url = article.get('webUrl', 'N/A')
        
        print(f"\nArticle {i + 1}:")
        print(f"  webPublicationDate:  {date}")
        print(f"  webTitle: {title}")
        print(f"  webURL:   {url}")

    print("------------------------------")



