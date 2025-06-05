
import requests
from bs4 import BeautifulSoup

first_test_url = "https://en.wikipedia.org/wiki/Web_scraping"

def extract_paragraph(url):
    response = requests.get(url)


    ### Docs for Requst library
    # https://pypi.org/project/requests/

    ### Beautiful Soup Docs
    # https://beautiful-soup-4.readthedocs.io/en/latest/


    # Status Code
    print("Status Code", response)

    # Headers
    headers = response.headers['content-type']
    #print("Headers", headers)

    # Text of the web response
    raw_text = response.text
    #print("Raw Text", raw_text)

    # any Json
    #print("JSON", first_request.json())

    # just html text
    html_soup = BeautifulSoup(raw_text, features="html.parser")
    print(html_soup)

    # Extract text
    first_paragraph = html_soup.find('p')
    print(first_paragraph.text.strip())

extract_paragraph(first_test_url)