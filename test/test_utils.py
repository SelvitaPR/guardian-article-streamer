import unittest

from unittest.mock import patch, call
from datetime import datetime, date
from src.utils import get_user_search_criteria, build_search_params, process_and_print_results

class TestGetUserSearchCriteria(unittest.TestCase):


    @patch('builtins.input', side_effect=['bitcoin', '2024-01-01'])
    def test_correct_search_term_input(self, mock_input):
        """
        Tests that the function returns correct search_term input.
        """
        result = get_user_search_criteria()
        mock_input.assert_called() #this confirms interaction with decorator input()
        self.assertEqual(result['search_term'], 'bitcoin')
        assert result['search_term'] == 'bitcoin'

    @patch('builtins.input', side_effect=['bitcoin', '2024-01-01'])
    def test_correct_date_from_input(self, mock_input):
        """
        Tests that the function returns correct date_from input.
        """
        result = get_user_search_criteria()
        mock_input.assert_called() 
        expected_date = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        self.assertEqual(result['date_from'], expected_date)
        assert result['date_from'] == expected_date

    @patch('builtins.input', side_effect=['bitcoin', "January 1st", '2024-01-01'])
    def test_invalid_date_format_retries(self, mock_input):
        """
        Tests that the function handles an invalid date format by re-prompting 
        the user and returns a second, valid date.
        """
        result = get_user_search_criteria()
        self.assertEqual(mock_input.call_count, 3, "Input function was not called the expected number of times (3).")
        expected_date = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        self.assertEqual(result['date_from'], expected_date, "Did not return the final, valid date object.")
        self.assertEqual(result['search_term'], 'bitcoin')

    @patch('builtins.input', side_effect=['bitcoin', '2024-02-30', '2024-01-01'])
    def test_logically_invalid_date(self, mock_input):
        """
        Tests that the function handles a logically impossible date (e.g., Feb 30th) 
        by catching the ValueError and successfully re-prompting the user.
        """
        result = get_user_search_criteria()
        self.assertEqual(mock_input.call_count, 3, "Input function was not called the expected number of times (3).")
        expected_date = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        self.assertEqual(result['date_from'], expected_date, "Did not return the final, valid date object.")
        self.assertEqual(result['search_term'], 'bitcoin')

    @patch('builtins.input', side_effect=['bitcoin', ''])
    def test_returns_dictionary_with_current_date(self,mock_input):
        """
        Tests if function returns today's date when user inputs empty string
        and if function returns a dictionary"""
        result = get_user_search_criteria()
        mock_input.assert_called()
        expected_date = date.today()
        assert isinstance(result, dict)
        assert isinstance(result['date_from'], date)
        self.assertEqual(result['date_from'], expected_date)


class TestBuildSearchParams(unittest.TestCase):

    
    def test_returns_dictionary(self):
        """
        Tests if function returns a dictionary.
        """
        test_search_term = 'machine learning'
        test_date_from = datetime.strptime('2023-01-01', '%Y-%m-%d').date()
        test_dict = {
            'search_term': test_search_term,
            'date_from': test_date_from
        }
        result = build_search_params(test_dict)
        assert isinstance(result, dict)

    def test_transforms_date_to_str(self):
        """
        Tests if function converts datetime to string.
        """
        test_search_term = 'machine learning'
        test_date_from = datetime.strptime('2023-01-01', '%Y-%m-%d').date()
        test_dict = {
            'search_term': test_search_term,
            'date_from': test_date_from
        }
        result = build_search_params(test_dict)
        assert isinstance(result['from-date'], str)

    def test_dictionary_contains_expected_params(self):
        """
        Tests if function returns the correct parameters.
        """
        test_search_term = 'machine learning'
        test_date_from = datetime.strptime('2023-01-01', '%Y-%m-%d').date()
        expected_date = '2023-01-01'
        test_dict = {
            'search_term': test_search_term,
            'date_from': test_date_from
        }
        result = build_search_params(test_dict)
        assert result['q'] == test_search_term
        assert result['from-date'] == expected_date

    def test_conversion_with_different_date(self):
        """
        Tests that the function correctly converts a different, valid datetime.date 
        object into the expected Guardian API string format.
        """
        test_search_term = 'future of AI'
        test_date_from = datetime.strptime('2025-11-20', '%Y-%m-%d').date() 
        expected_date = '2025-11-20'
        
        test_dict = {
            'search_term': test_search_term,
            'date_from': test_date_from
        }
        
        result = build_search_params(test_dict)
        
        self.assertEqual(result['q'], test_search_term)
        self.assertEqual(result['from-date'], expected_date)

    def test_non_datetime_input_raises_attribute_error(self):
        """
        Tests that passing a non-datetime object for the date raises an 
        AttributeError(implicit python error) when the function tries to call .strftime().
        """
        test_dict = {
            'search_term': 'test',
            'date_from': 'a simple string'
        }
        with self.assertRaises(AttributeError):
            build_search_params(test_dict)


class TestProcessAnPrint(unittest.TestCase):


    TEST_EMPTY_RESPONSE = {
        'response': {
            'status': 'ok',
            'total': 0,
            'results': []
        }
    }
    TEST_VALID_RESPONSE = {
        'response': {
            'status': 'ok',
            'results': [
                {
                    "webPublicationDate": "2025-10-01T10:00:00Z",
                    "webTitle": "First Test Article Title",
                    "webUrl": "http://example.com/article1"
                },
                {
                    "webPublicationDate": "2025-10-02T11:00:00Z",
                    "webTitle": "Second Test Article Title",
                    "webUrl": "http://example.com/article2"
                }
            ]
        }
    }

    @patch('builtins.print')
    def test_prints_no_articles_found(self, mock_print):
        """
        Tests that the function prints 'No articles found to display.' when the 'results' list is empty.
        """
        process_and_print_results(self.TEST_EMPTY_RESPONSE)
        mock_print.assert_called_with("No articles found to display.")

        process_and_print_results({'some': 'data'})
        mock_print.assert_called_with("No articles found to display.")

    @patch('builtins.print')
    def test_prints_right_fields(self, mock_print):
        """
        Tests that the function prints the correct fields in the expected format for multiple articles.
        """
        process_and_print_results(self.TEST_VALID_RESPONSE)
        expected_calls = [
            call('\n--- Extracted Article Data ---'),
            
            # First article
            call('\nArticle 1:'),
            call('  webPublicationDate:  2025-10-01T10:00:00Z'),
            call('  webTitle: First Test Article Title'),
            call('  webURL:   http://example.com/article1'),
            
            # Second article
            call('\nArticle 2:'),
            call('  webPublicationDate:  2025-10-02T11:00:00Z'),
            call('  webTitle: Second Test Article Title'),
            call('  webURL:   http://example.com/article2'),
            
            call('------------------------------')
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)


if __name__ == '__main__':
    unittest.main()