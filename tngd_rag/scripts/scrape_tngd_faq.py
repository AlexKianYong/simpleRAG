import cloudscraper
import os
from bs4 import BeautifulSoup
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor

def clean_text_strictly(text):
    """Aggressively removes unicode, smart quotes, and newlines."""
    if not text:
        return ""
    
    # 1. Replace newlines and tabs with spaces
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 2. Normalize to decompose combined characters
    text = unicodedata.normalize("NFKD", text)
    
    # 3. Manual map for stubborn characters (Non-breaking space, smart quotes)
    replacements = {
        '\xa0': ' ',     # Non-breaking space
        '\u2018': "'",   # Left single quote
        '\u2019': "'",   # Right single quote
        '\u201c': '"',   # Left double quote
        '\u201d': '"',   # Right double quote
        '\u2013': '-',   # En dash
        '\u2014': '-',   # Em dash
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # 4. Remove any remaining non-ASCII characters if you want purely clean text
    # This keeps standard punctuation but removes symbols/icons
    text = text.encode("ascii", "ignore").decode("utf-8")
    
    # 5. Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def scrape_article(article_info):
    url, scraper = article_info
    try:
        res = scraper.get(url, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            question = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Title"
            
            answer_div = soup.select_one('.article-body') or soup.select_one('.article-info')
            # Extract text first, then clean
            raw_answer = answer_div.get_text(separator=" ", strip=True) if answer_div else ""
            
            breadcrumbs = soup.select('.breadcrumbs li')
            category = breadcrumbs[2].get_text(strip=True) if len(breadcrumbs) >= 3 else "General"

            return {
                "category": clean_text_strictly(category),
                "question": clean_text_strictly(question),
                "answer": clean_text_strictly(raw_answer),
                "url": url
            }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return None

def main():
    base_url = "https://support.tngdigital.com.my"
    main_url = f"{base_url}/hc/en-my/categories/360002280493-Frequently-Asked-Questions-FAQ"
    targetKnowledgeBasePath = "../data/faq_data.json"
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    
    print("Fetching main list...")
    main_res = scraper.get(main_url)
    soup = BeautifulSoup(main_res.text, 'html.parser')
    links = [base_url + a.get('href') for a in soup.select('a.article-list-link')]
    
    print(f"Found {len(links)} articles. Scraping in parallel...")

    tasks = [(link, scraper) for link in links]

    # Using 5 workers to stay under the radar
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(scrape_article, tasks))

    final_data = [r for r in results if r is not None]

    directory = os.path.dirname(targetKnowledgeBasePath)
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it now...")
        os.makedirs(directory) # This creates the folder

    with open(targetKnowledgeBasePath, 'w', encoding='utf-8') as f:
        # ensure_ascii=True will force all non-ascii characters to be escaped, 
        # but since we cleaned them, False is fine and more readable.
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"Success! {len(final_data)} articles saved to faq_data.json.")

if __name__ == "__main__":
    main()