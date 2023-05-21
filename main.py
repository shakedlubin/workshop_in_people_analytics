from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
import pandas as pd

from extract_relevant_fields import *
from get_connections_urls import *
from load_page import *

load_dotenv()
read_urls_file = True
urls_output_file = "msc_search.txt"
urls_input_file = "test_msc.txt"
search_keyword = "ms.c"
csv_output_file = "msc_data.csv"

# Opening the login page and letting it load
driver = webdriver.Chrome(os.getenv('chromedriver_location'))
driver.get("https://linkedin.com/uas/login")
time.sleep(5)

# Login
username = driver.find_element(By.ID, "username")
username.send_keys(os.getenv('linkedin_username'))
pword = driver.find_element(By.ID, "password")
pword.send_keys(os.getenv('linkedin_password'))	
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Get list of Linkedin profiles urls
if not read_urls_file:
    connections_urls = get_connections_urls(driver, search_keyword)
    print(f'Connections collected {len(connections_urls)}')
    with open(urls_output_file, 'w') as file:
        for item in connections_urls:
            file.write(str(item) + '\n')
else:
    connections_urls = []
    with open(urls_input_file, 'r') as file:
        for line in file:
            connections_urls.append(line.strip())
    print(f'Connections in file {len(connections_urls)}')

# Iterate over all their pages and extract the relevant info
rows = []
for connection in connections_urls:
    soup = load_page(driver, connection)
    try:
        row = extract_relevant_fields(soup)
        rows.append(row)
    except:
        continue

# Create and save the data
df = pd.DataFrame(rows)
df.to_csv(csv_output_file, index=False)