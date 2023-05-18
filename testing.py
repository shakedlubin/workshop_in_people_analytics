from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Creating a webdriver instance
driver = webdriver.Chrome("C:\\Users\\shake\\OneDrive\\Codes\\chromedriver_win32\\chromedriver")
# This instance will be used to log into LinkedIn

# Opening linkedIn's login page
driver.get("https://linkedin.com/uas/login")

# waiting for the page to load
time.sleep(5)

# Login
username = driver.find_element(By.ID, "username")
username.send_keys(os.getenv('linkedin_username'))
pword = driver.find_element(By.ID, "password")
pword.send_keys(os.getenv('linkedin_password'))	
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Go to my profile
profile_url = "https://www.linkedin.com/in/shaked-lubin-98728a163/"
driver.get(profile_url)

start = time.time()
initialScroll = 0
finalScroll = 1000

while True:
	driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
	# this command scrolls the window starting from
	# the pixel value stored in the initialScroll
	# variable to the pixel value stored at the
	# finalScroll variable
	initialScroll = finalScroll
	finalScroll += 1000

	# we will stop the script for 3 seconds so that
	# the data can load
	time.sleep(3)
	# You can change it as per your needs and internet speed

	end = time.time()

	# We will scroll for 20 seconds.
	# You can change it as per your needs and internet speed
	if round(end - start) > 20:
		break


# Extracting the data
src = driver.page_source

# Now using beautiful soup
soup = BeautifulSoup(src, 'lxml')

def filter_links(href):
    prefix = "/search/results/people/"
    return href and href.startswith(prefix)

print(soup.find_all('a', href=filter_links))

intro = soup.find('div', {'class': 'pv-text-details__left-panel'})

# Name
name_loc = intro.find("h1")
name = name_loc.get_text().strip()

# Current workplace
works_at_loc = intro.find("div", {'class': 'text-body-medium'})
works_at = works_at_loc.get_text().strip()

# Education
education = []
sections = soup.find_all('section')
for section in sections:
    if section.find('div', {'id': 'education'}) is not None:
        ul = section.find('ul')
        for item in ul.find_all('li'):
            info_list = []
            for info in item.find_all('span', {'aria-hidden': 'true'}):
                info_list.append(info.get_text().strip())
            education.append(info_list)

rows = []
row = {'Name': name, 'Workplace': works_at, 'Education': education}
rows.append(row)
df = pd.DataFrame(rows)
print(df)