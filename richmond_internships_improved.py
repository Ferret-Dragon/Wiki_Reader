#!/usr/bin/env python3
"""
Improved Richmond Software Engineering Internship Scraper
Enhanced anti-detection measures for Indeed.com scraping
"""

from playwright.sync_api import sync_playwright
import csv
import json
import sqlite3
import time
import random
from datetime import datetime

def random_sleep(min_seconds, max_seconds):
    """Sleep for a random duration to appear more human-like"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def setup_database():
    """Set up SQLite database for job storage"""
    conn = sqlite3.connect("richmond_internships.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            snippet TEXT,
            job_url TEXT UNIQUE,
            source TEXT,
            scraped_at TEXT
        )
    """)

    conn.commit()
    return conn, cur

def save_results(jobs_data):
    """Save job data in CSV and JSON formats"""
    if not jobs_data:
        print("No data to save")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Save to CSV
    csv_filename = f"results_folder/richmond_internships_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=jobs_data[0].keys())
        writer.writeheader()
        writer.writerows(jobs_data)
    print(f"CSV saved: {csv_filename}")

    # Save to JSON
    json_filename = f"results_folder/richmond_internships_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(jobs_data, jsonfile, indent=2, ensure_ascii=False)
    print(f"JSON saved: {json_filename}")

def scrape_indeed_internships():
    """Enhanced scraping function with better anti-detection"""

    conn, cur = setup_database()
    jobs_data = []

    with sync_playwright() as p:
        # Enhanced browser launch with stealth mode
        browser = p.chromium.launch(
            headless=False,
            slow_mo=50,  # Add delays between actions
            args=[
                '--no-blink-features=AutomationControlled',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--start-maximized'
            ]
        )

        # Create context with enhanced stealth
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Add stealth script to remove webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        page = context.new_page()

        try:
            print("Step 1: Loading Indeed homepage with enhanced stealth...")

            # Go to Indeed homepage first and simulate human behavior
            page.goto("https://www.indeed.com", timeout=60000)

            # Wait for page to fully load
            page.wait_for_load_state('networkidle', timeout=30000)
            random_sleep(3, 6)

            # Check if we're blocked or redirected
            current_url = page.url
            print(f"Current URL: {current_url}")

            if "blocked" in current_url.lower() or "captcha" in current_url.lower():
                print("❌ Detected blocking or CAPTCHA. Try again later or use a VPN.")
                return []

            # Simulate human mouse movements
            page.mouse.move(random.randint(100, 500), random.randint(100, 300))
            random_sleep(1, 2)

            print("Step 2: Filling search form...")

            # Wait for and interact with search form
            try:
                # Wait for the job search input
                what_input = page.wait_for_selector('input[name="q"], #text-input-what', timeout=15000)
                if what_input:
                    # Click and clear first
                    what_input.click()
                    random_sleep(0.5, 1)
                    what_input.press('Control+a')
                    random_sleep(0.2, 0.5)

                    # Type slowly like a human
                    search_term = "software engineering internship"
                    for char in search_term:
                        what_input.type(char)
                        random_sleep(0.05, 0.15)

                    random_sleep(1, 2)

                # Handle location field
                where_input = page.query_selector('input[name="l"], #text-input-where')
                if where_input:
                    where_input.click()
                    random_sleep(0.5, 1)
                    where_input.press('Control+a')
                    random_sleep(0.2, 0.5)

                    location_term = "Richmond, VA"
                    for char in location_term:
                        where_input.type(char)
                        random_sleep(0.05, 0.15)

                    random_sleep(1, 2)

                # Submit search
                search_button = page.query_selector('button[type="submit"], .yosegi-InlineWhatWhere-primaryButton')
                if search_button:
                    print("Step 3: Submitting search...")
                    search_button.click()

                    # Wait for results page to load
                    print("Step 4: Waiting for results...")
                    page.wait_for_load_state('networkidle', timeout=45000)
                    random_sleep(5, 8)

            except Exception as e:
                print(f"Error with search form: {e}")
                # Save debug page
                with open('debug_search_form.html', 'w') as f:
                    f.write(page.content())
                print("Debug page saved as debug_search_form.html")
                return []

            # Check final URL
            final_url = page.url
            print(f"Results URL: {final_url}")

            # Look for job results
            print("Step 5: Looking for job listings...")

            # Multiple selectors to try
            selectors = [
                '.job_seen_beacon',
                'div[data-jk]',
                '.jobsearch-SerpJobCard',
                '[data-testid="job-result"]',
                '.slider_container .slider_item'
            ]

            job_elements = []
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        job_elements = elements
                        print(f"✅ Found {len(job_elements)} jobs using: {selector}")
                        break
                except:
                    continue

            if not job_elements:
                print("❌ No job elements found. Saving debug page...")
                with open('debug_no_jobs.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("Debug page saved as debug_no_jobs.html")

                # Check if there's a "no results" message
                no_results = page.query_selector_all('text="No jobs found"')
                if no_results:
                    print("Indeed returned 'No jobs found' - try different search terms")

                return []

            print(f"Step 6: Processing {len(job_elements)} job listings...")

            # Process each job
            for i, job_elem in enumerate(job_elements[:10]):  # Limit to first 10 for testing
                try:
                    job_data = extract_job_info(job_elem)
                    if job_data and is_internship(job_data):
                        jobs_data.append(job_data)
                        print(f"✅ {len(jobs_data)}. {job_data['title']} at {job_data['company']}")

                        # Save to database
                        try:
                            cur.execute("""
                                INSERT OR REPLACE INTO internships
                                (title, company, location, salary, snippet, job_url, source, scraped_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                job_data['title'],
                                job_data['company'],
                                job_data['location'],
                                job_data['salary'],
                                job_data['snippet'],
                                job_data['job_url'],
                                'Indeed',
                                job_data['scraped_at']
                            ))
                        except Exception as e:
                            print(f"Database error: {e}")

                except Exception as e:
                    print(f"Error processing job {i+1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            # Save debug page
            try:
                with open('debug_error.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("Error debug page saved as debug_error.html")
            except:
                pass

        finally:
            print("Closing browser...")
            browser.close()

    # Save results
    conn.commit()
    conn.close()

    if jobs_data:
        save_results(jobs_data)
        print(f"\n🎉 Success! Found {len(jobs_data)} internship positions")
        companies = list(set([job['company'] for job in jobs_data]))
        print(f"Companies: {', '.join(companies)}")
    else:
        print("\n❌ No internship positions found")
        print("\nTroubleshooting tips:")
        print("1. Check debug_*.html files for what Indeed returned")
        print("2. Try running again in a few minutes")
        print("3. Use a VPN if you've been rate-limited")
        print("4. Search manually on Indeed first to verify listings exist")

    return jobs_data

def extract_job_info(job_element):
    """Extract job information with robust selectors"""
    try:
        # Title extraction
        title_selectors = ['h2 a span[title]', 'h2 a span', '.jobTitle a span', '.jobTitle span']
        title = "N/A"
        for sel in title_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                title = elem.get_attribute('title') or elem.inner_text().strip()
                if title and len(title) > 2:
                    break

        # Company extraction
        company_selectors = ['[data-testid="company-name"]', '.companyName']
        company = "N/A"
        for sel in company_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                company = elem.inner_text().strip()
                if company and len(company) > 1:
                    break

        # Location extraction
        location_selectors = ['[data-testid="job-location"]', '.companyLocation']
        location = "N/A"
        for sel in location_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                location = elem.inner_text().strip()
                if location and len(location) > 1:
                    break

        # Salary extraction
        salary_selectors = ['[data-testid="attribute_snippet_testid"]', '.salaryText']
        salary = "N/A"
        for sel in salary_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                salary = elem.inner_text().strip()
                if salary and len(salary) > 1:
                    break

        # Snippet extraction
        snippet_selectors = ['[data-testid="job-snippet"]', '.summary']
        snippet = "N/A"
        for sel in snippet_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                snippet = elem.inner_text().strip()
                if snippet and len(snippet) > 5:
                    break

        # URL extraction
        url_selectors = ['h2 a', '.jobTitle a']
        job_url = "N/A"
        for sel in url_selectors:
            elem = job_element.query_selector(sel)
            if elem:
                href = elem.get_attribute('href')
                if href:
                    job_url = f"https://www.indeed.com{href}" if href.startswith('/') else href
                    break

        return {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'snippet': snippet,
            'job_url': job_url,
            'scraped_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error extracting job info: {e}")
        return None

def is_internship(job_data):
    """Check if job is an internship"""
    if not job_data:
        return False

    text = f"{job_data['title']} {job_data['snippet']}".lower()

    # Internship keywords
    internship_words = ['intern', 'internship', 'co-op', 'coop']
    has_internship = any(word in text for word in internship_words)

    # Tech keywords
    tech_words = ['software', 'developer', 'engineer', 'programming', 'tech', 'it']
    has_tech = any(word in text for word in tech_words)

    return has_internship and has_tech

if __name__ == "__main__":
    print("🔍 Enhanced Richmond Software Engineering Internship Scraper")
    print("=" * 60)
    scrape_indeed_internships()