from playwright.sync_api import sync_playwright
import sqlite3
import time
import random
import json
import csv
from datetime import datetime
from urllib.parse import urlencode
import re

def random_sleep(min_seconds, max_seconds):
    """Sleep for a random duration between min_seconds and max_seconds"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def build_indeed_search_url(job_title, location, job_type="internship"):
    """Build Indeed search URL with specific parameters for internships"""
    base_url = "https://www.indeed.com/jobs"
    params = {
        'q': f'{job_title} {job_type}',
        'l': location,
        'jt': 'internship',  # Job type filter for internships
        'sort': 'date'  # Sort by most recent
    }
    return f"{base_url}?{urlencode(params)}"

def extract_job_data(job_element):
    """Extract job information from a job posting element"""
    try:
        # Extract job title - try multiple selectors
        title_element = (job_element.query_selector('h2 a span[title]') or
                        job_element.query_selector('h2 a span') or
                        job_element.query_selector('a[data-jk] span[title]') or
                        job_element.query_selector('.jobTitle a span'))
        title = title_element.get_attribute('title') or title_element.inner_text().strip() if title_element else "N/A"

        # Extract company name - try multiple selectors
        company_element = (job_element.query_selector('[data-testid="company-name"] a') or
                          job_element.query_selector('[data-testid="company-name"]') or
                          job_element.query_selector('.companyName a') or
                          job_element.query_selector('.companyName'))
        company = company_element.inner_text().strip() if company_element else "N/A"

        # Extract location - try multiple selectors
        location_element = (job_element.query_selector('[data-testid="job-location"]') or
                           job_element.query_selector('.companyLocation'))
        location = location_element.inner_text().strip() if location_element else "N/A"

        # Extract job URL - try multiple selectors
        link_element = (job_element.query_selector('h2 a') or
                       job_element.query_selector('.jobTitle a') or
                       job_element.query_selector('a[data-jk]'))

        if link_element:
            href = link_element.get_attribute('href')
            job_url = f"https://www.indeed.com{href}" if href and href.startswith('/') else href
        else:
            job_url = "N/A"

        # Extract salary if available
        salary_element = (job_element.query_selector('[data-testid="attribute_snippet_testid"]') or
                         job_element.query_selector('.salary-snippet') or
                         job_element.query_selector('.salaryText'))
        salary = salary_element.inner_text().strip() if salary_element else "N/A"

        # Extract snippet/description preview
        snippet_element = (job_element.query_selector('[data-testid="job-snippet"]') or
                          job_element.query_selector('.summary'))
        snippet = snippet_element.inner_text().strip() if snippet_element else "N/A"

        # Extract posting date
        date_element = (job_element.query_selector('[data-testid="myJobsStateDate"]') or
                       job_element.query_selector('.date'))
        posting_date = date_element.inner_text().strip() if date_element else "N/A"

        return {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'snippet': snippet,
            'posting_date': posting_date,
            'job_url': job_url,
            'scraped_at': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error extracting job data: {e}")
        return None

def setup_database():
    """Set up SQLite database for storing job listings"""
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
            posting_date TEXT,
            job_url TEXT UNIQUE,
            scraped_at TEXT
        )
    """)

    conn.commit()
    return conn, cur

def save_to_csv(jobs_data, filename):
    """Save job data to CSV file"""
    if not jobs_data:
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = jobs_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs_data)

def save_to_json(jobs_data, filename):
    """Save job data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(jobs_data, jsonfile, indent=2, ensure_ascii=False)

def scrape_richmond_internships(max_pages=5, debug=False):
    """Main scraping function for Richmond software engineering internships"""

    # Set up database
    conn, cur = setup_database()

    jobs_data = []
    search_url = build_indeed_search_url("Software Engineer", "Richmond, VA")

    with sync_playwright() as p:
        # Launch browser with realistic settings
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            print(f"Starting search for software engineering internships in Richmond, VA...")
            page.goto(search_url)
            random_sleep(2, 4)

            # Handle potential pop-ups or cookie banners
            try:
                popup_close = page.query_selector('[aria-label="close"]')
                if popup_close:
                    popup_close.click()
                    random_sleep(1, 2)
            except:
                pass

            page_num = 1

            while page_num <= max_pages:
                print(f"Scraping page {page_num}...")

                # Wait for job listings to load - try multiple selectors
                try:
                    page.wait_for_selector('[data-jk], .jobsearch-SerpJobCard, .job_seen_beacon', timeout=15000)
                except:
                    print("Waiting for page to load completely...")
                    random_sleep(5, 8)

                random_sleep(2, 4)

                # Get all job listing elements - try multiple selectors
                job_elements = (page.query_selector_all('[data-jk]') or
                               page.query_selector_all('.jobsearch-SerpJobCard') or
                               page.query_selector_all('.job_seen_beacon') or
                               page.query_selector_all('[data-testid="job-result"]'))

                print(f"Found {len(job_elements)} job listings on page {page_num}")

                # Save page content for debugging if no jobs found
                if debug and len(job_elements) == 0:
                    debug_filename = f"debug_page_{page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    with open(debug_filename, 'w', encoding='utf-8') as f:
                        f.write(page.content())
                    print(f"Debug: Saved page content to {debug_filename}")

                # Extract data from each job listing
                for job_element in job_elements:
                    job_data = extract_job_data(job_element)
                    if job_data and job_data['title'] != "N/A":
                        # Check for internship keywords in multiple fields
                        title_lower = job_data['title'].lower()
                        snippet_lower = job_data['snippet'].lower()

                        # Look for internship-related keywords
                        internship_keywords = ['intern', 'internship', 'co-op', 'coop', 'summer program', 'student']
                        software_keywords = ['software', 'developer', 'engineer', 'programming', 'coding', 'tech']

                        is_internship = any(keyword in title_lower or keyword in snippet_lower for keyword in internship_keywords)
                        is_software_related = any(keyword in title_lower or keyword in snippet_lower for keyword in software_keywords)

                        if is_internship and is_software_related:
                            jobs_data.append(job_data)
                            print(f"Found internship: {job_data['title']} at {job_data['company']}")
                        elif debug:
                            print(f"Skipped: {job_data['title']} at {job_data['company']} (not matching criteria)")

                        # Save to database (avoid duplicates)
                        try:
                            cur.execute("""
                                INSERT OR IGNORE INTO internships
                                (title, company, location, salary, snippet, posting_date, job_url, scraped_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                job_data['title'],
                                job_data['company'],
                                job_data['location'],
                                job_data['salary'],
                                job_data['snippet'],
                                job_data['posting_date'],
                                job_data['job_url'],
                                job_data['scraped_at']
                            ))
                        except Exception as e:
                            print(f"Database error: {e}")

                # Try to go to next page
                try:
                    next_button = page.query_selector('a[aria-label="Next Page"]')
                    if next_button and next_button.is_enabled():
                        next_button.click()
                        random_sleep(3, 5)
                        page_num += 1
                    else:
                        print("No more pages available")
                        break
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    break

        except Exception as e:
            print(f"Error during scraping: {e}")

        finally:
            browser.close()

    # Commit database changes
    conn.commit()
    conn.close()

    # Generate output files with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if jobs_data:
        # Save to CSV
        csv_filename = f"results_folder/richmond_internships_{timestamp}.csv"
        save_to_csv(jobs_data, csv_filename)

        # Save to JSON
        json_filename = f"results_folder/richmond_internships_{timestamp}.json"
        save_to_json(jobs_data, json_filename)

        print(f"\nScraping completed!")
        print(f"Found {len(jobs_data)} software engineering internship positions")
        print(f"Results saved to:")
        print(f"  - CSV: {csv_filename}")
        print(f"  - JSON: {json_filename}")
        print(f"  - Database: richmond_internships.db")

        # Print summary
        companies = set([job['company'] for job in jobs_data])
        print(f"\nSummary:")
        print(f"  - Total positions: {len(jobs_data)}")
        print(f"  - Unique companies: {len(companies)}")
        print(f"  - Top companies: {', '.join(list(companies)[:5])}")

    else:
        print("No internship positions found matching the criteria")

    return jobs_data

if __name__ == "__main__":
    scrape_richmond_internships(max_pages=3, debug=True)