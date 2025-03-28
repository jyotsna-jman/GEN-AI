import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urlparse

# Configure headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# List of Cisco pages to scrape
cisco_pages = [
    "https://www.cisco.com",
    "https://www.cisco.com/site/us/en/about/contact-cisco/index.html",
    "https://www.cisco.com/c/en/us/about.html",
    "https://newsroom.cisco.com/c/r/newsroom/en/us/executives.html",
    "https://www.cisco.com/c/en/us/about/careers/we-are-cisco.html"
]

def clean_text(text):
    """Clean and normalize text"""
    return ' '.join(text.strip().split())

def scrape_contact_page(url):
    """Specialized scraper for contact page"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        contact_info = {
            'phone': None,
            'email': None,
            'address': None,
            'support_links': []
        }
        
        # Extract phone numbers
        phone_elements = soup.select('a[href^="tel:"]')
        if phone_elements:
            contact_info['phone'] = clean_text(phone_elements[0].get_text())
        
        # Extract email
        email_elements = soup.select('a[href^="mailto:"]')
        if email_elements:
            contact_info['email'] = clean_text(email_elements[0].get_text())
        
        # Extract address (looking for common patterns)
        address_div = soup.find('div', class_=lambda x: x and 'address' in x.lower())
        if address_div:
            contact_info['address'] = clean_text(address_div.get_text())
        
        # Extract support links
        support_links = soup.select('a[href*="support"], a[href*="contact"]')
        contact_info['support_links'] = [urljoin(url, link['href']) for link in support_links]
        
        return contact_info
        
    except Exception as e:
        print(f"Error scraping contact page: {e}")
        return None

def scrape_executives_page(url):
    """Specialized scraper for executives page"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        executives = []
        
        # Look for executive cards - this selector may need adjustment
        exec_cards = soup.select('.executive-card, .leader-profile, .bio-card')
        
        for card in exec_cards:
            name = card.select_one('h2, h3, .name')
            title = card.select_one('.title, .position')
            bio = card.select_one('.bio, .description')
            
            if name:
                exec_data = {
                    'name': clean_text(name.get_text()),
                    'title': clean_text(title.get_text()) if title else None,
                    'bio': clean_text(bio.get_text()) if bio else None
                }
                executives.append(exec_data)
        
        return executives
        
    except Exception as e:
        print(f"Error scraping executives page: {e}")
        return None

def scrape_generic_page(url):
    """Generic scraper for other pages"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            element.decompose()
        
        # Get main content (try to find the most relevant section)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup
        
        # Clean and return text
        return clean_text(main_content.get_text(separator=' ', strip=True))[:10000]  # Limit to 10k chars
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Main scraping function
def scrape_cisco_pages(pages):
    results = []
    
    for url in pages:
        print(f"\nScraping: {url}")
        page_data = {
            'url': url,
            'type': None,
            'data': None
        }
        
        try:
            # Route to appropriate scraper
            if 'contact-cisco' in url:
                page_data['type'] = 'contact'
                page_data['data'] = scrape_contact_page(url)
            elif 'executives' in url:
                page_data['type'] = 'executives'
                page_data['data'] = scrape_executives_page(url)
            else:
                page_data['type'] = 'generic'
                page_data['data'] = scrape_generic_page(url)
            
            results.append(page_data)
            time.sleep(2)  # Be polite
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            page_data['error'] = str(e)
            results.append(page_data)
    
    return results

# Run the scraper
if __name__ == "__main__":
    scraped_data = scrape_cisco_pages(cisco_pages)
    
    # Save to CSV
    csv_file = "cisco_scraped_data.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Page Type', 'Data'])
        
        for page in scraped_data:
            writer.writerow([
                page['url'],
                page['type'],
                str(page['data'])  # Convert dict/list to string
            ])
    
    print(f"\nScraping complete! Results saved to {csv_file}")