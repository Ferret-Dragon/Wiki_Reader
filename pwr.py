from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime
import os
from playwright_stealth import stealth  # Correct import
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async


seed_page = "https://www.indeed.com/"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edge/87.0.664.60",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def random_sleep(a, b):
    """Sleep for a random time to mimic human behavior"""
    time.sleep(random.uniform(a, b))

async def main():
    with sync_playwright() as p:
        # Rotate user agent
        random_user_agent = random.choice(user_agents)

        # Launch browser with stealth mode
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-extensions", "--no-proxy-server", "--use-gl=desktop"]
        )

        # Create a new context (incognito) 
        context = await browser.new_context(
            user_agent=random_user_agent,
            ignore_https_errors=True
        )
        page = await context.new_page()

        # Apply stealth mode to the context using the correct method
        await stealth_async(page)  # Correct way to apply stealth to the context

        visitPage = context.new_page()

        try:
            visitPage.goto(seed_page, timeout=60000)  # 60-second timeout to wait for page loading

            # Random delay between actions to simulate human-like behavior
            random_sleep(1, 2)
            visitPage.wait_for_selector("#text-input-what", timeout=30000)  # Wait for the selector to appear
            visitPage.fill("#text-input-what", "Software Engineer")

            random_sleep(1, 2)
            visitPage.click('button >> text="Search"')

            random_sleep(17, 20)

            # Ensure the 'results_folder' exists before writing the file
            if not os.path.exists("results_folder"):
                os.makedirs("results_folder")

            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            content = visitPage.content()
            with open(f"results_folder/indeed_{now}.txt", "w+") as file:
                file.write(content)

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            time.sleep(5)
            browser.close()

# Run the main function
main()
