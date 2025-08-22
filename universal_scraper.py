import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse, urljoin
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ssl
import certifi

# Suppress only the single warning from urllib3 needed
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

def scrape_universal_contact(url):
    """
    Scrape contact information from any website
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Coba dengan certificate bundle yang benar terlebih dahulu
        try:
            response = requests.get(url, headers=headers, timeout=30, verify=certifi.where())
            response.raise_for_status()
        except requests.exceptions.SSLError:
            # Fallback ke verify=False jika certificate bundle tidak bekerja
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract emails - pattern sudah benar
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, response.text)
        emails = list(set(emails))  # Remove duplicates
        
        # Extract phone numbers - PERBAIKI PATTERN UNTUK KODE AREA
        phone_patterns = [
            # Format internasional: +xx xxxx xxxx, +xx xxxx xxxx, +xx (0) xxxx xxxx
            r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}',
            # Format dengan kode area: (021) 123-4567, 021-123-4567, 021.123.4567
            r'\(?(\d{2,4})\)?[\s\-.]?(\d{3,4})[\s\-.]?(\d{3,4})',
            # Format tanpa kode area (minimal 7 digit): 123-4567, 1234567
            r'\b\d{3}[\s\-.]?\d{4}\b',
            # Format dengan kata "tel", "phone", atau "call"
            r'(?:tel|phone|call|telepon)[\s::\-]+\(?([\+]?\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9})\)?',
        ]
        
        phones = []
        for pattern in phone_patterns:
            found_phones = re.finditer(pattern, response.text, re.IGNORECASE)
            for match in found_phones:
                # Ambil seluruh match atau group pertama jika ada grouping
                if match.groups():
                    phone = ''.join([g for g in match.groups() if g])
                else:
                    phone = match.group(0)
                phones.append(phone)
        
        # Bersihkan dan format nomor telepon
        cleaned_phones = []
        for phone in phones:
            # Hapus karakter non-digit kecuali tanda +
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            
            # Validasi panjang nomor (minimal 7 digit, maksimal 16 digit)
            if 7 <= len(cleaned_phone.replace('+', '')) <= 16:
                # Format yang lebih rapi
                if cleaned_phone.startswith('+'):
                    # Format internasional: +XX XXX XXX XXXX
                    digits = cleaned_phone.replace('+', '')
                    formatted_phone = f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
                else:
                    # Format lokal dengan kode area
                    if len(cleaned_phone) >= 10:
                        # Format: XXX-XXXX-XXXX atau XX-XXXX-XXXX
                        kode_area = cleaned_phone[:3] if len(cleaned_phone) >= 11 else cleaned_phone[:2]
                        nomor = cleaned_phone[len(kode_area):]
                        
                        if len(nomor) == 7:
                            formatted_phone = f"{kode_area}-{nomor[:3]}-{nomor[3:]}"
                        elif len(nomor) == 8:
                            formatted_phone = f"{kode_area}-{nomor[:4]}-{nomor[4:]}"
                        else:
                            formatted_phone = f"{kode_area}-{nomor}"
                    else:
                        # Format tanpa kode area: XXX-XXXX
                        formatted_phone = f"{cleaned_phone[:3]}-{cleaned_phone[3:]}"
                
                cleaned_phones.append(formatted_phone.strip())
        
        phones = list(set(cleaned_phones))  # Remove duplicates
        
        # Extract social media links
        social_links = {}
        social_patterns = {
            'facebook': r'https?://(www\.)?facebook\.com/[A-Za-z0-9_.-]+',
            'twitter': r'https?://(www\.)?twitter\.com/[A-Za-z0-9_]+',
            'linkedin': r'https?://(www\.)?linkedin\.com/(company|in)/[A-Za-z0-9_.-]+',
            'instagram': r'https?://(www\.)?instagram\.com/[A-Za-z0-9_.-]+',
            'youtube': r'https?://(www\.)?youtube\.com/(channel/|user/|@)[A-Za-z0-9_.-]+',
            'whatsapp': r'https?://(wa\.me|api\.whatsapp\.com)/[\d+]+'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.finditer(pattern, response.text, re.IGNORECASE)
            for match in matches:
                link = match.group(0)
                # Pastikan link tidak mengandung karakter yang tidak diinginkan
                if '"' in link or "'" in link or '>' in link or '<' in link:
                    link = re.split(r'["\'<>]', link)[0]
                
                if platform not in social_links:
                    social_links[platform] = link
                elif link not in social_links.values():
                    # Jika platform sudah ada, tambahkan dengan angka
                    count = 1
                    while f"{platform}_{count}" in social_links:
                        count += 1
                    social_links[f"{platform}_{count}"] = link
        
        # Cari juga di tag meta dan link
        for meta in soup.find_all('meta', content=True):
            content = meta.get('content', '')
            for platform, pattern in social_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        link = match.group(0)
                        if platform not in social_links:
                            social_links[platform] = link
        
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href, re.IGNORECASE):
                    if platform not in social_links:
                        social_links[platform] = href
        
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
        
        return result
        
    except Exception as e:
        return {'error': f'Failed to scrape website: {str(e)}'}

# Fungsi save_scraped_data untuk kompatibilitas dengan app.py yang lama
def save_scraped_data(data):
    """Save scraped data to history - for backward compatibility"""
    from dashboard_component import add_to_history
    return add_to_history(data)
