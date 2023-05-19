import os
from dotenv import load_dotenv

from load_page import *

load_dotenv()

def filter_links(href):
    prefix = "https://www.linkedin.com/in/"
    return href and href.startswith(prefix)

def get_connections_urls(driver):
    connections_urls = []
    num_of_pages = int(os.getenv('linkedin_connection_page_count'))
    for page_num in range(1, num_of_pages+1):
        connections_url = f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&page={page_num}&sid=GAs"
        soup = load_page(driver, connections_url)
        connection_list = soup.find('main').find('ul').find_all('li')
        for connection in connection_list:
            try:
                href = connection.find('a', href=filter_links).get('href')
                connections_urls.append(href)
            except:
                continue

    return connections_urls