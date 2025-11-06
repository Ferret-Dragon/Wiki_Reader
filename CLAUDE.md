# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a job scraping tool that collects software engineering internship listings from job boards, primarily focusing on Indeed.com. The project uses web scraping with Playwright, stores data in SQLite databases, and exports results to CSV/JSON formats.

## Environment Setup

**Python Version:** Python 3.9 (based on venv path)

**Virtual Environment:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Playwright browser installation (required)
playwright install
```

## Running the Scraper

**Main internship scraper (Indeed):**
```bash
python richmond_internships_final.py
```
- Scrapes Indeed.com for "software engineering internship" positions in Richmond, VA
- Uses non-headless browser mode by default to bypass detection
- Results saved to: `results_folder/richmond_internships_<timestamp>.csv` and `.json`
- Data also stored in: `richmond_internships.db`

## Architecture

### Core Components

**Playwright-based scraper** (`richmond_internships_final.py`):
- Launch browser with anti-detection settings (custom user agents, realistic viewport sizes)
- Navigate to job boards using human-like interactions (random delays, form filling)
- Extract job data using multiple fallback CSS selectors (job boards frequently change HTML structure)
- Handle timeouts and scroll behaviors

### Data Storage

**SQLite database:**
- `richmond_internships.db`: Schema includes title, company, location, salary, snippet, job_url, source, scraped_at

**Results output:**
- `results_folder/`: Timestamped CSV and JSON files with scraping results
- Files follow naming: `richmond_internships_<YYYY-MM-DD_HH-MM-SS>.<ext>`

### Key Functions

**richmond_internships_final.py:**
- `scrape_indeed_internships()`: Main orchestration function
- `extract_job_info(job_element)`: Parses job card HTML with multiple fallback selectors
- `is_relevant_internship(job_data)`: Filters results using keyword matching (internship + tech keywords)
- `random_sleep(min, max)`: Human-like delays to avoid detection
- `setup_database()`: Create SQLite schema
- `save_results()`: Export to CSV/JSON

## Anti-Detection Strategies

The scraper implements several techniques to avoid blocking:
- Non-headless browser mode (visible browser window)
- Randomized delays between actions (1-5 seconds)
- Realistic user agents (Chrome on macOS)
- Human-like form interactions (clicking, typing with delays)
- Starting from homepage before search (Indeed)
- Custom headers (Accept-Language, Accept-Encoding)
- `--no-blink-features=AutomationControlled` flag

## Known Issues & Workarounds

**Site blocking status:**
- Indeed.com: Previously blocked by Cloudflare, current scraper uses GUI mode workaround
- LinkedIn, Monster, Handshake, Glassdoor: Behind account walls
- Stack Overflow: Accessible in GUI mode

**Selector fragility:**
- Job board HTML changes frequently
- All extraction functions use arrays of fallback selectors
- When scraper fails, check `indeed_debug.html` for current structure
- Common selector patterns: `[data-testid="*"]`, `.jobTitle`, `h2 a span`

## Development Guidelines

**IMPORTANT: Always prefer editing existing files over creating new ones**
- Before adding new functionality, check if similar code exists in the codebase
- Extend existing files rather than creating duplicate implementations
- When modifying scrapers, update `richmond_internships_final.py` directly
- Do not create new scraper files unless implementing support for a completely new job board

**Adding new job sources:**
1. Study the site's HTML structure and selectors
2. Create extraction functions with multiple fallback selectors (see `extract_job_info()` pattern)
3. Implement random delays and realistic browsing behavior
4. Test in non-headless mode first

**Database schema updates:**
- Modify CREATE TABLE statements in `richmond_internships_final.py`
- SQLite uses `INSERT OR REPLACE` for de-duplication (requires UNIQUE constraint on job_url)
