from playwright.sync_api import sync_playwright
import sqlite3
import time

# seed_page = "https://www.linkedin.com/jobs/jobs-in-richmond-va?trk=public_profile_guest_nav_menu_jobs&position=1&pageNum=0"
# seed_page = "https://www.monster.com/"
# seed_page = "https://jobs.aerotek.com/us/en?icid=jb_aero_n_gen_xx_rtk.cmsrchjb_xx_na_usa_20201002_66610422"

seed_page = "https://stackoverflowjobs.com/"

if __name__ == "__main__":

    with sync_playwright() as p:
            #### Initialize our Browser
            browser = p.chromium.launch(headless=False)  # Launch headless browser

            ### Visit a seed web page
                ### Input -- A website to visit, a configured browser object
                ### Output -- Playwright Page Object
            visitPage = browser.new_page()
            visitPage.goto(seed_page, wait_until="networkidle")
            
            # print(visitPage)
            # print(type(visitPage))
            # print(dir(visitPage))
            #print(visitPage.content())
    
            with open("StackOverflowResults.txt", "w+") as file:
                file.write(visitPage.content())
            
            time.sleep(5)

            browser.close()

            # TODO - Figure out how to read the data without waiting for network idle
                # There is a point after the webpage finished loading, that we are waiting for
                # Can we check file Size to determine if content is ready?
            # TODO - Click on one of the job postings, and see if we can grab information from it.
            
