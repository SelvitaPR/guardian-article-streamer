import argparse

#I think the following creates a CLI program to do what we want the tool to do:

parser = argparse.ArgumentParser(
                    prog='GuardianArticleStreamer',
                    description='Retrieve 10 most recent articles',
                    epilog='Text at the bottom of help')
parser.add_argument('search_term')
parser.add_argument('date_from')
parser.add_argument('message_broker')

# •	Accept arguments:
# search_term STR
# date_from STR-DATETIME
# message_broker STR

