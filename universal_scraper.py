import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse, urljoin
from datetime import datetime

def scrape_universal_contact(url):
    """
    Scrape contact information from any website
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, response.text)
        emails = list(set(emails))  # Remove duplicates
        
        # Extract phone numbers (international format)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        phones = re.findall(phone_pattern, response.text)
        phones = [phone[0] if isinstance(phone, tuple) else phone for phone in phones]
        phones = list(set(phones))  # Remove duplicates
        
        # Extract social media links
        social_links = {}
        social_patterns = {
            'facebook': r'https?://(www\.)?facebook\.com/[A-Za-z0-9_.-]+',
            'twitter': r'https?://(www\.)?twitter\.com/[A-Za-z0-9_]+',
            'linkedin': r'https?://(www\.)?linkedin\.com/(company|in)/[A-Za-z0-9_.-]+',
            'instagram': r'https?://(www\.)?instagram\.com/[A-Za-z0-9_.-]+',
            'youtube': r'https?://(www\.)?youtube\.com/(channel/|user/|@)[A-Za-z0-9_.-]+'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                # Handle both string and tuple matches
                cleaned_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        # Take the first non-empty group
                        match = next((m for m in match if m), '')
                    if match and match not in cleaned_matches:
                        cleaned_matches.append(match)
                
                if cleaned_matches:
                    social_links[platform] = cleaned_matches[0]  # Take the first match
        
        # Get website name from URL
        parsed_url = urlparse(url)
        website_name = parsed_url.netloc
        
        # Prepare result
        result = {
            'website': website_name,
            'url': url,
            'emails': emails,
            'phones': phones,
            'social_links': social_links,
            'timestamp': datetime.now().isoformat(),
            'scraper_type': 'universal'
        }
        
        # Save to history
        save_to_scraping_history(result)
        
        return result
        
    except Exception as e:
        return {'error': f'Failed to scrape website: {str(e)}'}

def save_to_scraping_history(scraping_data):
    """
    Save scraping data to scraping_history.json permanently
    """
    history_file = "scraping_history.json"
    
    # Read existing history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    else:
        history = []
    
    # Add ID to the new data
    scraping_data['id'] = len(history) + 1
    
    # Add to history
    history.append(scraping_data)
    
    # Save back to file
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    return scraping_data['id']
