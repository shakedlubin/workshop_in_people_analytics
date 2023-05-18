from load_page import *

def filter_links(href):
    prefix = "https://www.linkedin.com/in/"
    return href and href.startswith(prefix)

def get_connections_urls(driver):
    connections_urls = []
    for page_num in range(1, 62):
        connections_url = f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&page={page_num}&sid=GAs"
        soup = load_page(driver, connections_url)
        connection_list = soup.find('main').find('ul').find_all('li')
        for connection in connection_list:
            href = print(connection.find('a', href=filter_links))
            connections_urls.append(href)

    return connections_urls