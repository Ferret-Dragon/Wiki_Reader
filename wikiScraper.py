import sqlite3
import requests
from bs4 import BeautifulSoup

def get_url_info(url):
    """
    Returns headers, text, soup, title
    """
    response = requests.get(url)
    headers = response.headers['content-type']
    text = response.text
    soup = BeautifulSoup(text, features="html.parser")
    title = soup.find("h1", id="firstHeading").text.strip()
    return headers, text, soup, title

def id_categories(soup):
    cat_div = soup.find("div", id="mw-normal-catlinks")
    categories = []
    if cat_div:
        for li in cat_div.find("ul").find_all("li"):
            categories.append(li.text.strip())
    return categories

# Get following urls
def get_first_article_links(url, count=4):
    base_url = "https://en.wikipedia.org"
    _,_,soup,_ = get_url_info(url)
    content_div = soup.find("div", id="mw-content-text")
    
    urls = []
    if content_div:
        for link in content_div.find_all("a", href=True):
            href = link["href"]
            if href.startswith("/wiki/") and not ":" in href:  # Skip special pages like "Category:", "Help:", etc.
                full_url = base_url + href
                if full_url not in urls:
                    urls.append(full_url)
                if len(urls) >= count:
                    break
    return urls



# Name == main
if __name__ == "__main__":
    # Create database
    conn = sqlite3.connect("wikipedia_articles.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            categories TEXT
        )
    """)
    conn.commit()


    first_test_url = "https://en.wikipedia.org/wiki/Web_scraping"
    urls = [first_test_url]
    urls.extend(get_first_article_links(first_test_url))  # <- FIXED

    # Add to database
    for url in urls:
        #  headers, text, soup, title <-- Add to Function Signature 
        _, _, souper, title = get_url_info(url)
        categories = id_categories(souper)
        category_string = ", ".join(categories)
        cur.execute("INSERT INTO articles (title, categories) VALUES (?, ?)", (title, category_string))

    conn.commit()
    conn.close()
