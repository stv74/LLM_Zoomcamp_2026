'''This script loads FAQ data from the datatalks.club API and builds a MinSearch index.
'''
import requests
from minsearch import Index

def load_faq_data():
    '''
    Load FAQ data from the datatalks.club API and return a list of documents.
    Each document is a dictionary containing the course information.'''
    docs_url = "https://datatalks.club/faq/json/courses.json"
    response = requests.get(docs_url)
    courses_raw = response.json()

    documents = []
    url_prefix = "https://datatalks.club/faq"

    for course in courses_raw:
        course_url = f"""{url_prefix}{course["path"]}"""

        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_data = course_response.json()

        documents.extend(course_data)

    return documents

def build_index(documents):
    '''
    Build a MinSearch index from the list of documents.
    '''
    index = Index(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"]
    )
    index.fit(documents)
    return index
    