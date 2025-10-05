import boto3
import os
import json
import datetime

def filter_api_response(api_response: function, search_term: str, date_from: str):
    """
    Filters the Guardian API response by search term and date from publication.
    """
    date_list = date_from.split(',')
    date_from_final = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
    # Should this util just transform the parameter date??
    print("not finished")
