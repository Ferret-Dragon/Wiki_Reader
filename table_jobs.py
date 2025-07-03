# Imports
from playwright_practice import *
from claude_example import *
from playwright.sync_api import sync_playwright
import sqlite3
import tldextract


###  SET DEFAULT RESUME FOR TESTING
with open("resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()
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
    
def get_compatability_score(resume, job_description):
    score = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1000,
        temperature=1,
        system="You are a world-class Job Analyst. You can see the jobs and people behind the resumes, and can understand whether or not a given job and person would be a good match.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                    "text": f"""
                        You are an AI assistant tasked with creating a "Match Score" between a user's description of their resume and a job posting. Your goal is to analyze both inputs and determine how well the candidate's qualifications align with the job requirements.

                        First, carefully read the following resume description:

                        <resume_description>
                        {resume}
                        </resume_description>

                        Now, read the job posting:

                        <job_posting>
                        {job_description}
                        </job_posting>

                        To create an accurate Match Score, follow these steps:

                        1. Analyze the job posting to identify key requirements, skills, and qualifications.
                        2. Compare these requirements to the information provided in the resume description.
                        3. Consider both hard skills (technical abilities, certifications, etc.) and soft skills (communication, teamwork, etc.) mentioned in both the resume and job posting.
                        4. Evaluate the level of experience required in the job posting and compare it to the candidate's experience level.
                        5. Look for any specific achievements or accomplishments in the resume that directly relate to the job requirements.

                        Before providing your final Match Score, use the <scratchpad> tags to think through your analysis and comparison. Consider the strengths and weaknesses of the match, and any areas where the candidate exceeds or falls short of the job requirements.

                        Finally, provide a numerical Match Score as a percentage, where 100% represents a perfect match and 0% represents no match at all. Consider all aspects of your analysis when determining this score. Present your Match Score within <match_score> tags.

                        <match_score>
                        [Your Match Score here]
                        </match_score>

                        Remember to be objective and thorough in your analysis, considering all aspects of both the resume description and job posting when determining the Match Score.
                    """
                    }
                ]
            }
        ]
    )
    return score.content[0].text

# Generate job table
## Open database
## Listing source
## Job title
## Description *
## Url
## Compatability *

def create_job_table():
    print("Paste the link to the job source: \n")
    # https://richmond.craigslist.org/search/richmond-va/sof?lat=37.551&lon=-77.459&search_distance=25#search=2~thumb~0
    link = "https://richmond.craigslist.org/search/richmond-va/sof?lat=37.551&lon=-77.459&search_distance=25#search=2~thumb~0"#input()
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
        context = browser.new_context()
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
            #print("title ", title)
            #print("web address ", webAddress, "\n")
            
            # Open the individual job listing
            job_page = context.new_page()
            try:
                job_page.goto(webAddress, timeout=10000)
                job_page.wait_for_selector("#postingbody", timeout=5000)
                desc_el = job_page.query_selector("#postingbody")
                description = desc_el.inner_text().strip() if desc_el else "No description found"
                print(get_compatability_score(resume, description))
            except:
                pass
            finally:
                job_page.close()
            
            cur.execute("INSERT INTO jobs (source, job, description, url, compatability) VALUES (?, ?, ?, ?, ?)", (source, title, description, webAddress, "compatability_score"))

        conn.commit()
        conn.close()
        browser.close()


if __name__ == "__main__":
    create_job_table()