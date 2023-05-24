import os
from dotenv import load_dotenv

from load_page import *

load_dotenv()

def filter_links(href):
    prefix = "https://www.linkedin.com/in/"
    bad_prefix = "https://www.linkedin.com/in/ACo"
    return href and href.startswith(prefix) and not href.startswith(bad_prefix)

def get_connections_urls(driver, keywords):
    connections_urls = set()
    num_of_pages = int(os.getenv('linkedin_connection_page_count'))
    for page_num in range(1, num_of_pages+1):
        if keywords is not None:
            connections_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=CLUSTER_EXPANSION&page={page_num}&sid=XlV"
        else:
            connections_url = f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&page={page_num}&sid=GAs"
        soup = load_page(driver, connections_url)
        
        try:
            lists = soup.find('main').find_all('ul')
            connection_list = []
            for ul in lists:
                connection_list += ul.find_all('li')
        except:
            continue
        
        for connection in connection_list:
            try:
                a_tags = connection.find_all('a', href=filter_links)
                for a_tag in a_tags:
                    connections_urls.add(a_tag.get('href'))
            except:
                continue

        print(f'Collected {len(connections_urls)} from {page_num} pages')

    return connections_urls