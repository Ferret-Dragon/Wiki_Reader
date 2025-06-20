from playwright.sync_api import sync_playwright
import sqlite3

        
def visit_seed_web_page(page_to_visit, browser):
    playwrightPage = None
    playwrightPage = browser.new_page()
    playwrightPage.goto(page_to_visit, wait_until="networkidle")  # Wait until page is fully loaded
    return playwrightPage

def get_all_link_elements_from_page(playwrightPage):
       
    matchingSearchResultsOnPage = playwrightPage.query_selector_all("div.cl-search-result.cl-search-view-mode-thumb")
    print("number of links found on page", len(matchingSearchResultsOnPage))

    return matchingSearchResultsOnPage

        # firstResult = matchingSearchResultsOnPage[0]

        # link_el = firstResult.query_selector("a")
        # if link_el:
        #     print("Link in result : ", link_el.get_attribute("href"))
        #     print("inner text of link : ", link_el.inner_text())
    
def get_job_title_from_CL_html(playwrightElementHandle):
    ### Type --> playwright.sync_api._generated.ElementHandle
    jobTitle = playwrightElementHandle.get_attribute("title")
    
    return jobTitle

def get_web_address_for_link_element(playwrightElementHandle):
    link_el = playwrightElementHandle.query_selector("a")
    if link_el:
        return link_el.get_attribute("href")

    return "none listed"
    
if __name__ == "__main__":

    link="https://richmond.craigslist.org/search/richmond-va/sof?lat=37.551&lon=-77.459&search_distance=25#search=2~thumb~0"

    ### Open connection to the database
    conn = sqlite3.connect("craigslist_jobs.db")
    cur = conn.cursor()

    ### Create Database if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job TEXT,
            url TEXT
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
            
            cur.execute("INSERT INTO jobs (job, url) VALUES (?, ?)", (title, webAddress))

        conn.commit()
        conn.close()
        browser.close()

        # TODO - 
        # Visit each of these links
        # Determine what data is important / related to the job listing (i.e. parse data for critical information)
        # Send to an LLM to ask for a 1 sentence summary of the job.
        # Store that result in our database.
        


    ### For each link, grab the title + link

        ### Print them out


