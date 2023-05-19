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
read_txt_file = True

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

# Get my connections list
if not read_txt_file:
    connections_urls = get_connections_urls(driver)
    print(f'Connections collected {len(connections_urls)}')
    with open('shakeds_connections.txt', 'w') as file:
        for item in connections_urls:
            file.write(str(item) + '\n')
else:
    connections_urls = []
    with open('test.txt', 'r') as file:
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
df.to_csv('linkedin_data.csv', index=False)