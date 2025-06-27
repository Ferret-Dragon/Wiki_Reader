# Imports
from playwright_practice import *
from claude_example import *
from playwright.sync_api import sync_playwright
import sqlite3
import tldextract


# Load environment variables from the .env file
load_dotenv()

claude_api_key = os.getenv("CLAUDE_API_KEY")

# initialize client 
client = anthropic.Anthropic(api_key=claude_api_key)

# Determine job search source
def get_link_source(url):
    extracted = tldextract.extract(url)
    # Use just the domain part and capitalize it for readability
    site_name = extracted.domain
    return site_name.capitalize()
    

# Generate job table
def create_job_table():
    print("Paste the link to the job source: \n")
    # https://richmond.craigslist.org/search/richmond-va/sof?lat=37.551&lon=-77.459&search_distance=25#search=2~thumb~0
    link = input()
    source = get_link_source(link)
    
    ### Open connection to the database
    conn = sqlite3.connect("craigslist_jobs.db")
    cur = conn.cursor()

    ### Create Database if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            job TEXT,
            description TEXT,
            url TEXT,
            compatability TEXT
        )
    """)
    conn.commit()


    with sync_playwright() as p:
        #### Initialize our Browser
        browser = p.chromium.launch(headless=True)  # Launch headless browser

        ### Visit a seed web page
            ### Input -- A website to visit, a configured browser object
            ### Output -- Playwright Page Object
        pageData = visit_seed_web_page(link, browser)

        ### Grab all elements that may contain search results from that page
        pageLinks = get_all_link_elements_from_page(pageData)

        ### Find the Title and Web Addresses from those results
        for data in pageLinks:
            title = get_job_title_from_CL_html(data)
            webAddress = get_web_address_for_link_element(data)
            print("title ", title)
            print("web address ", webAddress, "\n")
            
            cur.execute("INSERT INTO jobs (source, job, description, url, compatability) VALUES (?, ?, ?, ?, ?)", (source, title, "null", webAddress, "null"))

        conn.commit()
        conn.close()
        browser.close()


if __name__ == "__main__":
    create_job_table()