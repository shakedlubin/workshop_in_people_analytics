import time
from bs4 import BeautifulSoup

def load_page(driver, url):
    driver.get(url)

    # Load the page
    start = time.time()
    initialScroll = 0
    finalScroll = 1000

    while True:
        driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
        initialScroll = finalScroll
        finalScroll += 1000
        time.sleep(3)
        end = time.time()
        if round(end - start) > 20:
            break
        
    # Extracting the data
    src = driver.page_source

    # Now using beautiful soup
    soup = BeautifulSoup(src, 'lxml')

    return soup