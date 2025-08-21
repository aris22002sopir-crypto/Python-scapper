# universal_scraper.py (enhanced version with fallback)
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import time
from bs4 import Comment
from datetime import datetime
from typing import List, Dict, Any, Set
import concurrent.futures

# Try to import phonenumbers, but provide fallback if not available
try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    print("Warning: phonenumbers module not installed. Using regex fallback for phone number extraction.")

class UniversalContactScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.visited_urls = set()
        self.max_depth = 2
        self.max_pages = 10
        
    def extract_emails(self, text):
        """Extract emails from text with improved pattern matching"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        return list(set([email.lower() for email in emails]))
    
    def extract_phones(self, text, default_region="ID"):
        """Extract phone numbers using regex patterns optimized for various formats"""
        phone_patterns = [
            r'\+?[\d\s\-\(\)]{10,}',  # General international pattern
            r'\+?\d{1,4}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}',  # International
            r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',  # US/Canada format
            r'\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # Various local formats
            r'\+62[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # Indonesia specific
            r'0\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # Local Indonesian numbers
        ]
        
        all_phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean the phone number
                clean_phone = re.sub(r'[^\d+]', '', match)
                if len(clean_phone) >= 8:  # Minimum reasonable phone number length
                    all_phones.append(clean_phone)
        
        return list(set(all_phones))
    
    def extract_addresses(self, text):
        """Extract potential addresses from text"""
        # Common address indicators
        address_indicators = [
            r'jalan\s+[\w\s]+', r'jl\.?\s+[\w\s]+', r'street\s+[\w\s]+', 
            r'avenue\s+[\w\s]+', r'blvd\.?\s+[\w\s]+', r'rt\.?\s*\d+[/\s]*rw\.?\s*\d+',
            r'kel\.\s+[\w\s]+', r'kec\.\s+[\w\s]+', r'kota\s+[\w\s]+', r'city\s+[\w\s]+',
            r'provinsi\s+[\w\s]+', r'kode pos\s+\d+', r'zip code\s+\d+'
        ]
        
        addresses = []
        for pattern in address_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            addresses.extend(matches)
        
        return list(set(addresses))
    
    def extract_social_links(self, soup, base_url):
        """Extract social media links with comprehensive platform coverage"""
        social_platforms = {
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'instagram': ['instagram.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'tiktok': ['tiktok.com'],
            'whatsapp': ['whatsapp.com', 'wa.me'],
        }
        
        social_links = {}
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href'].lower()
            for platform, domains in social_platforms.items():
                for domain in domains:
                    if domain in href:
                        absolute_url = urljoin(base_url, href)
                        social_links[platform] = absolute_url
                        break
        
        return social_links
    
    def extract_contact_elements(self, soup, base_url):
        """Extract contact information from various HTML elements"""
        contact_data = {
            'phones': set(),
            'emails': set(),
            'addresses': set(),
            'contact_links': set()
        }
        
        # Check common contact elements
        contact_selectors = [
            'a[href*="tel:"]', 'a[href*="mailto:"]', 
            'a[href*="contact"]', 'a[href*="about"]',
            '.contact', '.phone', '.email', '.address',
            '[class*="contact"]', '[class*="phone"]',
            '[class*="email"]', '[class*="address"]',
            '#contact', '#phone', '#email', '#address'
        ]
        
        for selector in contact_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                href = element.get('href', '')
                
                # Extract phones
                if 'tel:' in href:
                    phone = href.replace('tel:', '').strip()
                    contact_data['phones'].add(phone)
                
                # Extract emails
                if 'mailto:' in href:
                    email = href.replace('mailto:', '').strip()
                    contact_data['emails'].add(email)
                
                # Extract contact page links
                if any(keyword in href.lower() for keyword in ['contact', 'about', 'help']):
                    contact_data['contact_links'].add(urljoin(base_url, href))
                
                # Extract from text content
                contact_data['phones'].update(self.extract_phones(text))
                contact_data['emails'].update(self.extract_emails(text))
                contact_data['addresses'].update(self.extract_addresses(text))
        
        # Convert sets to lists
        for key in contact_data:
            contact_data[key] = list(contact_data[key])
            
        return contact_data
    
    def extract_from_metadata(self, soup):
        """Extract contact information from meta tags"""
        meta_contacts = {'emails': set(), 'phones': set()}
        
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            content = tag.get('content', '')
            name = tag.get('name', '').lower()
            property_attr = tag.get('property', '').lower()
            
            # Check for contact-related meta tags
            if any(term in name for term in ['contact', 'email', 'phone', 'tel']) or \
               any(term in property_attr for term in ['contact', 'email', 'phone', 'tel']):
                meta_contacts['emails'].update(self.extract_emails(content))
                meta_contacts['phones'].update(self.extract_phones(content))
        
        # Convert sets to lists
        for key in meta_contacts:
            meta_contacts[key] = list(meta_contacts[key])
            
        return meta_contacts
    
    def extract_from_json_ld(self, soup):
        """Extract contact information from JSON-LD structured data"""
        contact_info = {}
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    data = [data]  # Convert to list for consistent processing
                
                for item in data:
                    if '@type' in item and item['@type'] in ['Organization', 'LocalBusiness', 'Person']:
                        if 'contactPoint' in item:
                            if isinstance(item['contactPoint'], list):
                                for contact in item['contactPoint']:
                                    if 'telephone' in contact:
                                        if 'phones' not in contact_info:
                                            contact_info['phones'] = set()
                                        contact_info['phones'].add(contact['telephone'])
                                    if 'email' in contact:
                                        if 'emails' not in contact_info:
                                            contact_info['emails'] = set()
                                        contact_info['emails'].add(contact['email'])
                            
                        # Direct contact info
                        for field in ['telephone', 'phone', 'email', 'contactPoint']:
                            if field in item:
                                value = item[field]
                                if isinstance(value, str):
                                    if field in ['telephone', 'phone']:
                                        if 'phones' not in contact_info:
                                            contact_info['phones'] = set()
                                        contact_info['phones'].add(value)
                                    elif field == 'email':
                                        if 'emails' not in contact_info:
                                            contact_info['emails'] = set()
                                        contact_info['emails'].add(value)
            except:
                continue
        
        # Convert sets to lists
        for key in contact_info:
            contact_info[key] = list(contact_info[key])
            
        return contact_info
    
    def crawl_page(self, url, depth=0):
        """Crawl a single page and extract contact information"""
        if depth > self.max_depth or len(self.visited_urls) >= self.max_pages or url in self.visited_urls:
            return {}
        
        self.visited_urls.add(url)
        print(f"Crawling: {url} (depth: {depth})")
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            text_content = ' '.join(text_content.split())
            
            # Extract various types of contact information
            contact_data = {
                'url': url,
                'emails': self.extract_emails(text_content),
                'phones': self.extract_phones(text_content),
                'addresses': self.extract_addresses(text_content),
                'social_links': self.extract_social_links(soup, url),
                'page_title': soup.title.string if soup.title else '',
                'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                  if soup.find('meta', attrs={'name': 'description'}) else ''
            }
            
            # Extract from HTML elements
            element_data = self.extract_contact_elements(soup, url)
            contact_data['emails'].extend(element_data['emails'])
            contact_data['phones'].extend(element_data['phones'])
            contact_data['addresses'].extend(element_data['addresses'])
            
            # Extract from meta tags
            meta_data = self.extract_from_metadata(soup)
            contact_data['emails'].extend(meta_data['emails'])
            contact_data['phones'].extend(meta_data['phones'])
            
            # Extract from JSON-LD
            json_ld_data = self.extract_from_json_ld(soup)
            if 'emails' in json_ld_data:
                contact_data['emails'].extend(json_ld_data['emails'])
            if 'phones' in json_ld_data:
                contact_data['phones'].extend(json_ld_data['phones'])
            
            # Remove duplicates
            for key in ['emails', 'phones', 'addresses']:
                contact_data[key] = list(set(contact_data[key]))
            
            # Find additional pages to crawl
            if depth < self.max_depth:
                internal_links = self.find_internal_links(soup, url)
                for link in internal_links:
                    if len(self.visited_urls) < self.max_pages:
                        time.sleep(0.5)  # Be polite
                        page_data = self.crawl_page(link, depth + 1)
                        # Merge results
                        for key in ['emails', 'phones', 'addresses']:
                            contact_data[key].extend(page_data.get(key, []))
            
            return contact_data
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return {}
    
    def find_internal_links(self, soup, base_url):
        """Find internal links that might contain contact information"""
        internal_links = set()
        domain = urlparse(base_url).netloc
        
        contact_keywords = ['contact', 'about', 'help', 'support', 'location', 'address']
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Check if it's an internal link and not already visited
            if (parsed_url.netloc == domain and 
                full_url not in self.visited_urls and
                not any(ext in href for ext in ['.pdf', '.doc', '.docx', '.jpg', '.png'])):
                
                # Prioritize contact-related pages
                link_text = link.get_text().lower()
                if any(keyword in href.lower() or keyword in link_text for keyword in contact_keywords):
                    internal_links.add(full_url)
                
                # Also include other internal pages but limit quantity
                elif len(internal_links) < 5:  # Limit non-contact pages
                    internal_links.add(full_url)
        
        return list(internal_links)
    
    def scrape_from_main_page(self, main_url):
        """Main method to scrape contact information starting from the main page"""
        self.visited_urls = set()
        
        # Start with the main page
        main_data = self.crawl_page(main_url)
        
        # Consolidate results
        consolidated = {
            'website': main_url,
            'emails': list(set(main_data.get('emails', []))),
            'phones': list(set(main_data.get('phones', []))),
            'addresses': list(set(main_data.get('addresses', []))),
            'social_links': main_data.get('social_links', {}),
            'pages_crawled': list(self.visited_urls),
            'crawl_timestamp': datetime.now().isoformat()
        }
        
        return consolidated

# Function alias for backward compatibility
def scrape_universal_contact(url, max_depth=2, max_pages=10):
    """
    Universal contact scraper function - compatible with the original import
    """
    scraper = UniversalContactScraper()
    scraper.max_depth = max_depth
    scraper.max_pages = max_pages
    return scraper.scrape_from_main_page(url)

# Alias for backward compatibility
scrape_universal_data = scrape_universal_contact

def save_scraped_data(scraped_data, filename="scraped_data.json"):
    """Save scraped data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_scraped_data(filename="scraped_data.json"):
    """Load scraped data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Test the function
    result = scrape_universal_contact("https://www.coca-cola.com/id/")
    print(json.dumps(result, indent=2))
    
    # Save results
    save_scraped_data(result, "contact_results.json")
    print("Scraping completed. Results saved to contact_results.json")