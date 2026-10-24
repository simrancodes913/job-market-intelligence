from concurrent.futures import wait
from pathlib import Path
import yaml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options




from selenium.webdriver.support.ui import WebDriverWait  ##(wait function is used to wait for a certain condition to 
                                                           ##be met before proceeding with the next step in the code).
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import urlsplit, urlunsplit
import re

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Configuration file
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def generate_page_url(base_url, page_number):
    parts = urlsplit(base_url)

    path = re.sub(r"-\d+$", "", parts.path)

    if page_number > 1:
        path = f"{path}-{page_number}"

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        path,
        parts.query,
        parts.fragment
    ))



def test_browser():
    config = load_config()
    url = config["scraping"]["job_url"]

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    ## first we have done driver open the url and starts collecting the job cards; but selenuim is not able to find the job cards
    #  because the page is not fully loaded yet. Because the selenium works differently like:
    #  first the raw HTML page loads then javascript runs after that selenium loads pages and create job cards dynamically 
    # So we need to wait for the page to load completely
    #  before we can find the job cards. We can use time.sleep() to wait for a few seconds before finding the job cards.

    #time.sleep(5)  # Wait for 5 seconds for the page to load



    ##we could use the selenium wait function to wait for the job cards to load instead of using time.sleep() 
    # which is not a good practice. Because the selenium's wait function will wait the job cards to load and in pagination concept 
    ## this selenium wait function will be very useful because we can wait for the job cards to load in 
    # each page and then we can scrape the job cards.

    ###HERE'S THE SELENIUM WAIT FUNCTION TO WAIT FOR THE JOB CARDS TO LOAD
    wait = WebDriverWait(driver, 15)

    job_cards = wait.until(
        EC.presence_of_all_elements_located(
            ("css selector", ".srp-jobtuple-wrapper")
        )
    )

    print("Job cards found:", len(job_cards))


    print("Title:", driver.title)
    print("URL:", driver.current_url)

    # Save the complete HTML
    html = driver.page_source

    output_path = BASE_DIR / "data" / "raw" / "naukri_page.html"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)

    print("HTML saved to:", output_path)
    time.sleep(10)  # Wait for 10 seconds to observe the browser before closing
    driver.quit()

if __name__ == "__main__":
    config = load_config()

    base_url = config["scraping"]["job_url"]

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 15)

    for page in range(1, 4):

        page_url = generate_page_url(base_url, page)

        print(f"\nOpening page {page}")
        print(page_url)

        driver.get(page_url)

        job_cards = wait.until(
            EC.presence_of_all_elements_located(
                ("css selector", ".srp-jobtuple-wrapper")
            )
        )

        print("Job cards found:", len(job_cards))

    driver.quit()