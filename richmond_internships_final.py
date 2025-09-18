#!/usr/bin/env python3
"""
Richmond Software Engineering Internship Scraper
Scrapes Indeed.com for software engineering internship positions in Richmond, VA
"""

from playwright.sync_api import sync_playwright
import csv
import json
import sqlite3
import time
import random
from datetime import datetime
import re

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

def save_results(jobs_data, format_type="all"):
    """Save job data in specified format(s)"""
    if not jobs_data:
        print("No data to save")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if format_type in ["csv", "all"]:
        csv_filename = f"results_folder/richmond_internships_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=jobs_data[0].keys())
            writer.writeheader()
            writer.writerows(jobs_data)
        print(f"CSV saved: {csv_filename}")

    if format_type in ["json", "all"]:
        json_filename = f"results_folder/richmond_internships_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(jobs_data, jsonfile, indent=2, ensure_ascii=False)
        print(f"JSON saved: {json_filename}")

def scrape_indeed_internships():
    """Main scraping function with improved error handling"""

    # Setup database
    conn, cur = setup_database()

    jobs_data = []

    with sync_playwright() as p:
        # Launch browser with more realistic settings
        browser = p.chromium.launch(
            headless=False,
            args=['--no-blink-features=AutomationControlled']
        )

        # Create context with realistic headers
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768},
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )

        page = context.new_page()

        try:
            # Start with Indeed homepage first
            print("Loading Indeed homepage...")
            page.goto("https://www.indeed.com", wait_until='networkidle')
            random_sleep(2, 4)

            # Fill search form manually to be more human-like
            print("Filling search form...")

            # Wait for and fill the job search box
            what_box = page.wait_for_selector('#text-input-what', timeout=10000)
            if what_box:
                what_box.click()
                random_sleep(0.5, 1)
                what_box.fill('software engineering internship')
                random_sleep(1, 2)

            # Fill location box
            where_box = page.query_selector('#text-input-where')
            if where_box:
                where_box.click()
                random_sleep(0.5, 1)
                # Clear existing text first
                where_box.press('Control+a')
                where_box.press('Delete')
                random_sleep(0.5, 1)
                where_box.fill('Richmond, VA')
                random_sleep(1, 2)

            # Click search button
            search_button = page.query_selector('button[type="submit"]')
            if search_button:
                search_button.click()
                print("Search submitted, waiting for results...")
                page.wait_for_load_state('networkidle', timeout=30000)
                random_sleep(3, 5)

            # Look for job results with multiple fallback selectors
            job_selectors = [
                'div[data-jk]',
                '.jobsearch-SerpJobCard',
                '.job_seen_beacon',
                '[data-testid="job-result"]',
                '.slider_container .slider_item',
                'table[role="table"] tr',
                '.jobsearch-ResultsList .result'
            ]

            job_elements = []
            for selector in job_selectors:
                job_elements = page.query_selector_all(selector)
                if job_elements:
                    print(f"Found {len(job_elements)} job listings using selector: {selector}")
                    break

            if not job_elements:
                print("No job elements found. Saving page for debugging...")
                with open('indeed_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("Page saved as indeed_debug.html")
                return []

            # Extract job data
            for i, job_elem in enumerate(job_elements):
                try:
                    job_data = extract_job_info(job_elem)
                    if job_data and is_relevant_internship(job_data):
                        jobs_data.append(job_data)
                        print(f"{len(jobs_data)}. {job_data['title']} at {job_data['company']}")

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
                                job_data['description'],
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
            print(f"Error during scraping: {e}")

        finally:
            browser.close()

    # Commit database changes
    conn.commit()
    conn.close()

    # Save results in multiple formats
    if jobs_data:
        save_results(jobs_data)
        print(f"\nScraping completed! Found {len(jobs_data)} relevant internship positions.")

        # Print summary
        companies = list(set([job['company'] for job in jobs_data if job['company'] != 'N/A']))
        print(f"Companies found: {', '.join(companies)}")
    else:
        print("No relevant internship positions found.")

    return jobs_data

def extract_job_info(job_element):
    """Extract job information from a job element"""
    try:
        # Extract title with multiple fallback selectors
        title_selectors = [
            'h2 a span[title]',
            'h2 a span',
            'h2 span',
            '.jobTitle a',
            '.jobTitle span',
            'a[data-jk] span'
        ]

        title = "N/A"
        for selector in title_selectors:
            elem = job_element.query_selector(selector)
            if elem:
                title = elem.get_attribute('title') or elem.inner_text().strip()
                if title and title != "N/A":
                    break

        # Extract company
        company_selectors = [
            '[data-testid="company-name"] a',
            '[data-testid="company-name"]',
            '.companyName a',
            '.companyName span',
            '.companyName'
        ]

        company = "N/A"
        for selector in company_selectors:
            elem = job_element.query_selector(selector)
            if elem:
                company = elem.inner_text().strip()
                if company and company != "N/A":
                    break

        # Extract location
        location_selectors = [
            '[data-testid="job-location"]',
            '.companyLocation',
            '.locationsContainer'
        ]

        location = "N/A"
        for selector in location_selectors:
            elem = job_element.query_selector(selector)
            if elem:
                location = elem.inner_text().strip()
                if location and location != "N/A":
                    break

        # Extract salary
        salary_selectors = [
            '[data-testid="attribute_snippet_testid"]',
            '.salaryText',
            '.salary-snippet'
        ]

        salary = "N/A"
        for selector in salary_selectors:
            elem = job_element.query_selector(selector)
            if elem:
                salary = elem.inner_text().strip()
                if salary and salary != "N/A":
                    break

        # Extract description/snippet
        desc_selectors = [
            '[data-testid="job-snippet"]',
            '.summary',
            '.jobSnippet'
        ]

        description = "N/A"
        for selector in desc_selectors:
            elem = job_element.query_selector(selector)
            if elem:
                description = elem.inner_text().strip()
                if description and description != "N/A":
                    break

        # Extract job URL
        url_selectors = [
            'h2 a',
            '.jobTitle a',
            'a[data-jk]'
        ]

        job_url = "N/A"
        for selector in url_selectors:
            elem = job_element.query_selector(selector)
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
            'description': description,
            'job_url': job_url,
            'scraped_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error extracting job info: {e}")
        return None

def is_relevant_internship(job_data):
    """Check if the job is a relevant software engineering internship"""
    if not job_data:
        return False

    title = job_data.get('title', '').lower()
    description = job_data.get('description', '').lower()
    combined_text = f"{title} {description}"

    # Check for internship keywords
    internship_keywords = ['intern', 'internship', 'co-op', 'coop', 'summer program', 'entry level']
    has_internship = any(keyword in combined_text for keyword in internship_keywords)

    # Check for software/tech keywords
    tech_keywords = ['software', 'developer', 'engineer', 'programming', 'coding', 'tech', 'computer', 'java', 'python', 'javascript', 'web']
    has_tech = any(keyword in combined_text for keyword in tech_keywords)

    return has_internship and has_tech

if __name__ == "__main__":
    print("Richmond Software Engineering Internship Scraper")
    print("=" * 50)
    scrape_indeed_internships()