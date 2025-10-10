import os
import unittest
from unittest.mock import Mock, call, patch

from dotenv import load_dotenv

from src.api_client import fetch_guardian_content

load_dotenv()
API_KEY=os.getenv("GUARDIAN_API_KEY")
API_URL=os.getenv("GUARDIAN_URL")


class TestFetchGuardianContent(unittest.TestCase):


    @patch('requests.get')
    def test_succesful_api_call(self, mock_get):
        """
        Tests if function returns status_code 200 for a successful response, 
        and returns the parsed JSON data"""
        mock_response = Mock()
        mock_response.status_code = 200
        expected_data = {
            "response": {
                "status": "ok",
                "userTier": "developer",
                "total": 10
            }
        }
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response
        test_params = {'q': 'test_search', 'order-by': 'newest'}
        result = fetch_guardian_content(API_URL, test_params)
        self.assertEqual(result, expected_data, "Function did not return the expected JSON data.")
        
        mock_get.assert_called_once()
        
        expected_call_params = {
            'q': 'test_search', 
            'order-by': 'newest', 
            'api-key': API_KEY 
        }
        mock_get.assert_called_with(API_URL, params=expected_call_params)

    @patch('builtins.print')
    @patch('requests.get')
    def test_unauthorized_error_401(self, mock_get, mock_print):
        """
        Tests that the function handles a 401 Unauthorized response by 
        returning None and printing the error message.
        """
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        test_params = {'q': 'error_test'}
        result = fetch_guardian_content(API_URL, test_params)

        self.assertIsNone(result, "Function returns None on 401 error.")
        
        mock_print.assert_any_call("Error: Unauthorized. Check your API key.")

    @patch('builtins.print')
    @patch('requests.get')
    def test_generic_error_500(self, mock_get, mock_print):
        """
        Tests that the function handles a generic non-200/non-401 error
        by returning None and printing the status code and response text.
        """
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error HTML"
        mock_get.return_value = mock_response
        test_params = {'q': 'server_test'}
        result = fetch_guardian_content(API_URL, test_params)
        expected_calls = [
            call("Error: Received status code 500"),
            call("Response:", "Internal Server Error HTML")
        ]

        self.assertIsNone(result, "Function should return None on a non-401 failure.")
        mock_print.assert_has_calls(expected_calls, any_order=False)

    @patch('requests.get')
    def test_parameter_merging_includes_api_key(self, mock_get):
        """
        Tests that the function correctly merges user parameters
        with the mandatory API_KEY and calls requests.get.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {} 
        mock_get.return_value = mock_response
        expected_call_params = {
            'q': 'economy', 
            'from-date': '2020-01-01', 
            'api-key': API_KEY 
        }
        
        test_params = {'q': 'economy', 'from-date': '2020-01-01'}
        fetch_guardian_content(API_URL, test_params)
        
        mock_get.assert_called_with(API_URL, params=expected_call_params)


if __name__ == '__main__':
    unittest.main()