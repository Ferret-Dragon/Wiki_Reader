from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Launch headless browser
        page = browser.new_page()

        #page.goto("https://richmond.craigslist.org/search/acc#search=2~thumb~0")
        #page.goto("https://richmond.craigslist.org/search/richmond,-va-va/acc?lat=37.5383&lon=-77.4615&search_distance=60#search=2~thumb~0", wait_until="networkidle")
        page.goto("https://richmond.craigslist.org/search/richmond-va/sof?lat=37.551&lon=-77.459&search_distance=25#search=2~thumb~0", wait_until="networkidle")  # Wait until page is fully loaded



        html = page.content()  # Get rendered HTML
        with open("seed_page_content.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        matchingSearchResultsOnPage = page.query_selector_all("div.cl-search-result.cl-search-view-mode-thumb")
        print(len(matchingSearchResultsOnPage))

        # with open("links_page.html", "w", encoding="utf-8") as f:
        #     for link in items:
        #         f.write(str(link))
        firstResult = matchingSearchResultsOnPage[0]
        print(type(firstResult))
        print(dir(type(firstResult)))
        print("-----------")
        print("inner html of element : ",firstResult.inner_html())
        print("Title of element : ", firstResult.get_attribute("title"))


        link_el = firstResult.query_selector("a")
        if link_el:
            print("Link in result : ", link_el.get_attribute("href"))
            print("inner text of link : ", link_el.inner_text())
            # for data in firstResult:
        #     print(data)
        
        browser.close()

        
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
        
        browser.close()

        
        


    ### For each link, grab the title + link

        ### Print them out


