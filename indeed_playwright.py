from playwright.sync_api import sync_playwright
import sqlite3
import time
import random
from datetime import datetime

seed_page = "https://www.indeed.com/"

def random_sleep(a, b):
    time.sleep(random.uniform(a, b))
    
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context= browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        visitPage = context.new_page()
        visitPage.goto(seed_page)

        random_sleep(1, 2)
        visitPage.wait_for_selector("#text-input-what")
        visitPage.fill("#text-input-what", "Software Engineer")

        random_sleep(1, 2)
        visitPage.click('button >> text="Search"')
        random_sleep(17, 20)

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        content = visitPage.content()
        with open(f"results_folder/indeed_{now}.txt", "w+") as file:
            file.write(content)
        
        time.sleep(5)
        browser.close()

main()
