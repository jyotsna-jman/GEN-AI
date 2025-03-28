import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urlparse
import random

# Configure headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Enhanced cleaning function
def clean_text(soup):
    # Remove non-content elements
    for tag in ['script', 'style', 'nav', 'footer', 'iframe', 'button', 'form', 'header']:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Get text and clean
    text = soup.get_text(separator=' ', strip=True)
    return ' '.join(text.split())

# Site-specific scraping functions
def scrape_cisco(soup):
    content = soup.find('main') or soup.find('article') or soup
    return clean_text(content)

def scrape_bp(soup):
    content = soup.find('div', class_='main-content') or soup
    return clean_text(content)

def scrape_accenture(soup):
    content = soup.find('div', {'data-testid': 'richText'}) or soup
    return clean_text(content)

def scrape_visa(soup):
    content = soup.find('div', class_='content-wrapper') or soup
    return clean_text(content)

def scrape_gsk(soup):
    content = soup.find('main') or soup.find('div', class_='core-content') or soup
    return clean_text(content)

# Main scraping function
def scrape_website(url):
    try:
        print(f"\nScraping: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        domain = urlparse(url).netloc
        
        # Route to appropriate scraper
        if 'cisco.com' in domain:
            text = scrape_cisco(soup)
        elif 'bp.com' in domain:
            text = scrape_bp(soup)
        elif 'accenture.com' in domain:
            text = scrape_accenture(soup)
        elif 'visa.com' in domain:
            text = scrape_visa(soup)
        elif 'gsk.com' in domain:
            text = scrape_gsk(soup)
        else:
            text = clean_text(soup)
        
        return {
            'url': url,
            'domain': domain,
            'content': text[:50000],  # First 50k chars
            'status': 'success'
        }
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'url': url,
            'domain': domain,
            'content': None,
            'status': 'failed',
            'error': str(e)
        }

# Websites to scrape
websites = [
    "https://www.cisco.com",
    "https://www.bp.com",
    "https://www.accenture.com",
    "https://usa.visa.com",
    "https://www.gsk.com"
]

# Scraping with some delays
results = []
for url in websites:
    result = scrape_website(url)
    results.append(result)
    time.sleep(random.uniform(2, 5))  # Random delay between requests to prevent rate limiting

# Saving to CSV
output_file = "scraped_company_data.csv"
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['url', 'domain', 'content', 'status', 'error']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\nScraping complete! Results saved to {output_file}")
print(f"Successfully scraped: {sum(1 for r in results if r['status'] == 'success')}/{len(websites)}")
