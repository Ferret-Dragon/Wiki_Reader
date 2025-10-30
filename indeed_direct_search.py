#!/usr/bin/env python3
"""
Direct Indeed URL approach for Richmond internships
Uses pre-constructed search URL to bypass form submission
"""

from playwright.sync_api import sync_playwright
import csv
import json
from datetime import datetime
import time
import random

def scrape_with_direct_url():
    """Scrape using direct Indeed search URL"""

    # Direct Indeed search URL for software internships in Richmond, VA
    search_url = "https://www.indeed.com/jobs?q=software+engineering+internship&l=Richmond%2C+VA&jt=internship"

    jobs_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        page = context.new_page()

        try:
            print(f"Loading: {search_url}")
            page.goto(search_url, timeout=60000)

            # Wait and check what we got
            try:
                page.wait_for_load_state('domcontentloaded', timeout=15000)
            except:
                print("Timeout waiting for page load, continuing anyway...")
            time.sleep(3)

            # Save the page for inspection
            with open('direct_search_result.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("Page saved as direct_search_result.html")

            # Try to find jobs
            job_selectors = ['.job_seen_beacon', 'div[data-jk]', '.jobsearch-SerpJobCard']

            for selector in job_selectors:
                jobs = page.query_selector_all(selector)
                if jobs:
                    print(f"Found {len(jobs)} jobs with selector: {selector}")

                    for i, job in enumerate(jobs[:5]):  # First 5 for testing
                        try:
                            # Extract basic info
                            title_elem = job.query_selector('h2 a span, .jobTitle')
                            title = title_elem.inner_text().strip() if title_elem else f"Job {i+1}"

                            company_elem = job.query_selector('[data-testid="company-name"], .companyName')
                            company = company_elem.inner_text().strip() if company_elem else "Unknown Company"

                            location_elem = job.query_selector('[data-testid="job-location"], .companyLocation')
                            location = location_elem.inner_text().strip() if location_elem else "Unknown Location"

                            jobs_data.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'scraped_at': datetime.now().isoformat()
                            })

                            print(f"{i+1}. {title} at {company}")

                        except Exception as e:
                            print(f"Error processing job {i+1}: {e}")

                    break

            if not jobs_data:
                print("No jobs found. Check direct_search_result.html to see what Indeed returned.")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            browser.close()

    # Save results if any found
    if jobs_data:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        csv_file = f"results_folder/direct_search_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
            writer.writeheader()
            writer.writerows(jobs_data)

        print(f"Results saved to {csv_file}")

    return jobs_data

if __name__ == "__main__":
    scrape_with_direct_url()