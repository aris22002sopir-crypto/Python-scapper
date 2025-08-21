# scraper.py (essential functions only)
import pandas as pd
from playwright.sync_api import sync_playwright
import time

def scrape_saasquatch(url):
    """
    Simplified scraping function
    """
    result_data = {
        'pricing_data': pd.DataFrame(),
        'contact_info': {},
        'error': None
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            
            # Simple pricing data extraction
            pricing_data = page.evaluate('''() => {
                const tables = document.querySelectorAll('table');
                if (tables.length === 0) return [];
                
                const rows = Array.from(tables[0].querySelectorAll('tr'));
                return rows.map(row => {
                    const cells = Array.from(row.querySelectorAll('th, td'));
                    return cells.map(cell => cell.innerText.trim());
                });
            }''')
            
            if pricing_data:
                result_data['pricing_data'] = pd.DataFrame(pricing_data[1:], columns=pricing_data[0])
            
            browser.close()
            
    except Exception as e:
        result_data['error'] = f"Error: {str(e)}"
    
    return result_data