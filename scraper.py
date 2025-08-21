# scraper.py (essential functions only)
import pandas as pd
from playwright.sync_api import sync_playwright
import time
import re

def scrape_saasquatch(url):
    """
    Specialized scraping function for SaaSquatchLeads pricing table
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
            
            # Set longer timeout and wait for page to load
            page.goto(url, timeout=120000, wait_until='networkidle')
            
            # Wait for the pricing table to load
            page.wait_for_selector('table.jsx-c15ddf1490db7a4f', timeout=30000)
            
            # Extract the pricing table data
            pricing_data = page.evaluate('''() => {
                const table = document.querySelector('table.jsx-c15ddf1490db7a4f');
                if (!table) return null;
                
                // Extract headers (plan names)
                const headers = [];
                const headerCells = table.querySelectorAll('thead th');
                for (let i = 1; i < headerCells.length; i++) { // Skip the first header (Features)
                    headers.push(headerCells[i].innerText.trim());
                }
                
                // Extract features and values
                const features = [];
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length > 0) {
                        const featureName = cells[0].innerText.trim();
                        const featureValues = [];
                        
                        for (let i = 1; i < cells.length; i++) {
                            let value = cells[i].innerText.trim();
                            // Convert checkmarks and dashes to standardized format
                            if (value.includes('✔') || value.includes('✔️')) {
                                value = '✅';
                            } else if (value.includes('—') || value === '') {
                                value = '❌';
                            }
                            featureValues.push(value);
                        }
                        
                        features.push({
                            'Feature': featureName,
                            ...Object.fromEntries(headers.map((header, idx) => [header, featureValues[idx] || '❌']))
                        });
                    }
                });
                
                // Extract prices from footer
                const footerRows = table.querySelectorAll('tfoot tr');
                if (footerRows.length >= 2) {
                    const priceCells = footerRows[0].querySelectorAll('td');
                    const priceValues = [];
                    
                    for (let i = 1; i < priceCells.length; i++) {
                        priceValues.push(priceCells[i].innerText.trim());
                    }
                    
                    features.push({
                        'Feature': 'Price',
                        ...Object.fromEntries(headers.map((header, idx) => [header, priceValues[idx] || 'N/A']))
                    });
                }
                
                return features;
            }''')
            
            if pricing_data:
                result_data['pricing_data'] = pd.DataFrame(pricing_data)
                
                # Extract contact information if available
                contact_info = page.evaluate('''() => {
                    const contacts = {};
                    // Try to find email addresses
                    const emailElements = document.querySelectorAll('a[href^="mailto:"]');
                    if (emailElements.length > 0) {
                        contacts.emails = Array.from(emailElements).map(el => el.href.replace('mailto:', ''));
                    }
                    
                    // Try to find phone numbers
                    const phoneRegex = /(\+\d{1,2}\s?)?(\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}/g;
                    const bodyText = document.body.innerText;
                    const phoneMatches = bodyText.match(phoneRegex);
                    if (phoneMatches) {
                        contacts.phones = phoneMatches;
                    }
                    
                    return contacts;
                }''')
                
                result_data['contact_info'] = contact_info
            
            browser.close()
            
    except Exception as e:
        result_data['error'] = f"Error scraping SaaSquatchLeads: {str(e)}"
    
    return result_data


# Also update the app.py to use this specialized function for SaaSquatchLeads
# Add this function to your app.py file:

def scrape_pricing_data(url):
    """
    Scrapes pricing data from websites, with special handling for SaaSquatchLeads
    """
    # Special handling for SaaSquatchLeads
    if 'saasquatchleads.com' in url:
        return scrape_saasquatch(url)
    
    # Generic scraping for other websites
    try:
        # This is a placeholder - implement actual scraping logic for other sites
        # For demonstration, returning sample data
        sample_data = {
            'Feature': ['Monthly Leads', 'Lead Scraping', 'Export to CSV', 'Price'],
            'Free': ['5', '❌', '❌', '$0/mo'],
            'Bronze': ['50', '✅', '✅', '$19/mo'],
            'Silver': ['125', '✅', '✅', '$49/mo'],
            'Gold': ['292', '✅', '✅', '$99/mo'],
            'Platinum': ['Unlimited', '✅', '✅', '$199/mo'],
            'Custom': ['Custom', '✅', '✅', 'Custom']
        }
        
        return {
            'pricing_data': pd.DataFrame(sample_data),
            'error': None
        }
    except Exception as e:
        return {
            'pricing_data': pd.DataFrame(),
            'error': f'Error scraping pricing data: {str(e)}'
        }
