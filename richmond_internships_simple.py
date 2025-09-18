from playwright.sync_api import sync_playwright
import csv
import json
import time
import random
from datetime import datetime
from urllib.parse import urlencode

def random_sleep(min_seconds, max_seconds):
    """Sleep for a random duration between min_seconds and max_seconds"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def build_indeed_url():
    """Build Indeed search URL specifically for internships in Richmond, VA"""
    base_url = "https://www.indeed.com/jobs"
    params = {
        'q': 'software engineering internship',
        'l': 'Richmond, VA',
        'jt': 'internship',
        'sort': 'date'
    }
    return f"{base_url}?{urlencode(params)}"

def scrape_internships():
    """Simple scraper for Richmond software engineering internships"""

    jobs_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            url = build_indeed_url()
            print(f"Searching: {url}")
            page.goto(url)
            random_sleep(3, 5)

            # Close any popups
            try:
                close_button = page.query_selector('[aria-label="close"], [aria-label="Close"]')
                if close_button:
                    close_button.click()
                    random_sleep(1, 2)
            except:
                pass

            # Wait for results
            page.wait_for_load_state('networkidle')
            random_sleep(2, 4)

            # Try to find job cards using various selectors
            selectors_to_try = [
                'div[data-jk]',
                '.jobsearch-SerpJobCard',
                '.job_seen_beacon',
                '[data-testid="job-result"]',
                '.slider_container .slider_item'
            ]

            job_elements = []
            for selector in selectors_to_try:
                job_elements = page.query_selector_all(selector)
                if job_elements:
                    print(f"Found {len(job_elements)} job elements using selector: {selector}")
                    break

            if not job_elements:
                # Save page content for manual inspection
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("No job elements found. Page saved as debug_page.html")
                return []

            # Extract job information
            for i, job_element in enumerate(job_elements):
                try:
                    # Try multiple title selectors
                    title_selectors = ['h2 a span', 'h2 span', '.jobTitle a', '.jobTitle']
                    title = "N/A"
                    for sel in title_selectors:
                        title_elem = job_element.query_selector(sel)
                        if title_elem:
                            title = title_elem.inner_text().strip()
                            break

                    # Try multiple company selectors
                    company_selectors = ['[data-testid="company-name"]', '.companyName']
                    company = "N/A"
                    for sel in company_selectors:
                        company_elem = job_element.query_selector(sel)
                        if company_elem:
                            company = company_elem.inner_text().strip()
                            break

                    # Try multiple location selectors
                    location_selectors = ['[data-testid="job-location"]', '.companyLocation']
                    location = "N/A"
                    for sel in location_selectors:
                        location_elem = job_element.query_selector(sel)
                        if location_elem:
                            location = location_elem.inner_text().strip()
                            break

                    # Try to find job URL
                    url_selectors = ['h2 a', '.jobTitle a', 'a']
                    job_url = "N/A"
                    for sel in url_selectors:
                        link_elem = job_element.query_selector(sel)
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href:
                                job_url = f"https://www.indeed.com{href}" if href.startswith('/') else href
                                break

                    # Try to find job description/snippet
                    snippet_selectors = ['[data-testid="job-snippet"]', '.summary']
                    snippet = "N/A"
                    for sel in snippet_selectors:
                        snippet_elem = job_element.query_selector(sel)
                        if snippet_elem:
                            snippet = snippet_elem.inner_text().strip()
                            break

                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'snippet': snippet,
                        'job_url': job_url,
                        'scraped_at': datetime.now().isoformat()
                    }

                    jobs_data.append(job_data)
                    print(f"{i+1}. {title} at {company} - {location}")

                except Exception as e:
                    print(f"Error processing job {i+1}: {e}")

        except Exception as e:
            print(f"Error during scraping: {e}")

        finally:
            browser.close()

    # Save results
    if jobs_data:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Save to CSV
        csv_filename = f"results_folder/simple_richmond_internships_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if jobs_data:
                writer = csv.DictWriter(csvfile, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)

        # Save to JSON
        json_filename = f"results_folder/simple_richmond_internships_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(jobs_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"\nResults saved:")
        print(f"- CSV: {csv_filename}")
        print(f"- JSON: {json_filename}")
        print(f"- Total jobs found: {len(jobs_data)}")

        # Print summary
        companies = [job['company'] for job in jobs_data if job['company'] != 'N/A']
        unique_companies = list(set(companies))
        print(f"- Companies found: {', '.join(unique_companies[:10])}")

    return jobs_data

if __name__ == "__main__":
    scrape_internships()