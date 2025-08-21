# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

from contact_component import show_contact_section
from universal_scraper import scrape_universal_contact, save_scraped_data
from dashboard_component import show_dashboard, add_to_history

# Page configuration
st.set_page_config(page_title="Caprae - Web Contact Scraper", layout="wide", page_icon="🔍")

# MINIMAL CSS - Only essential
st.markdown("""
<style>
[data-testid="column"] {
    align-items: stretch;
    gap: 1rem;
}
.stButton > button {
    width: 100%;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Navigation sidebar
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Navigate to", ["Dashboard", "Universal Contact Scraper", "Competitive Analysis", "Contact Us"])

# Function to scrape pricing data from SaaSquatchLeads
def scrape_pricing_data(url):
    """
    Scrapes pricing data from the SaaSquatchLeads website.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the pricing table
        pricing_table = soup.find('table', {'class': 'jsx-c15ddf1490db7a4f'})
        
        if not pricing_table:
            return {
                'pricing_data': pd.DataFrame(),
                'error': 'Pricing table not found on the page'
            }
        
        # Extract table headers (plan names)
        headers = []
        header_cells = pricing_table.find('thead').find_all('th')
        for cell in header_cells:
            header_text = cell.get_text(strip=True)
            if header_text and header_text != 'Features':
                headers.append(header_text)
        
        # Extract table rows (features)
        features_data = []
        rows = pricing_table.find('tbody').find_all('tr')
        
        for row in rows:
            feature_cells = row.find_all('td')
            if len(feature_cells) > 1:
                feature_name = feature_cells[0].get_text(strip=True)
                feature_values = [cell.get_text(strip=True) for cell in feature_cells[1:]]
                
                # Convert checkmarks to standardized format
                standardized_values = []
                for value in feature_values:
                    if '✔️' in value or '✔' in value:
                        standardized_values.append('✅')
                    elif '—' in value or value == '':
                        standardized_values.append('❌')
                    else:
                        standardized_values.append(value)
                
                features_data.append({
                    'Feature': feature_name,
                    **dict(zip(headers, standardized_values))
                })
        
        # Extract prices from the footer
        footer = pricing_table.find('tfoot')
        if footer:
            price_row = footer.find_all('tr')[0]
            price_cells = price_row.find_all('td')[1:]  # Skip the first cell ("Price")
            
            prices = {}
            for i, cell in enumerate(price_cells):
                if i < len(headers):
                    prices[headers[i]] = cell.get_text(strip=True)
            
            # Add pricing row
            features_data.append({
                'Feature': 'Price',
                **prices
            })
        
        return {
            'pricing_data': pd.DataFrame(features_data),
            'error': None
        }
        
    except Exception as e:
        return {
            'pricing_data': pd.DataFrame(),
            'error': f'Error scraping pricing data: {str(e)}'
        }

# Main content area
if page == "Dashboard":
    show_dashboard()

elif page == "Universal Contact Scraper":
    st.title("🌐 Universal Web Contact Scraper")
    st.write("Enter any website URL to extract contact information.")
    
    # Input horizontal
    input_col, button_col = st.columns([3, 1])
    
    with input_col:
        url_input = st.text_input("Enter Website URL", placeholder="https://example.com")
    
    with button_col:
        scrape_clicked = st.button("🚀 Scrape Now", type="primary", use_container_width=True)
    
    if scrape_clicked and url_input:
        with st.spinner('Extracting contact information...'):
            result = scrape_universal_contact(url_input)
            
        if result.get('error'):
            st.error(f"Error: {result['error']}")
        else:
            st.success(f"✅ Successfully extracted from {result['website']}")
            
            # Save to history
            history_id = add_to_history(result)
            st.info(f"Scraping saved to history with ID: {history_id}")
            
            # Results horizontal layout
            st.subheader("📋 Scraping Results")
            
            # Email & Phone side by side
            email_col, phone_col = st.columns(2)
            
            with email_col:
                st.write("**📧 Email Addresses**")
                if result['emails']:
                    for email in result['emails']:
                        st.code(email)
                else:
                    st.info("No emails found")
            
            with phone_col:
                st.write("**📞 Phone Numbers**")
                if result['phones']:
                    for phone in result['phones']:
                        st.code(phone)
                else:
                    st.info("No phones found")
            
            # Social media horizontal
            st.write("**📱 Social Media Links**")
            if result['social_links']:
                social_cols = st.columns(min(3, len(result['social_links'])))
                for i, (platform, link) in enumerate(result['social_links'].items()):
                    with social_cols[i % 3]:
                        st.write(f"**{platform.upper()}**")
                        st.markdown(f"[Visit {platform}]({link})")
            else:
                st.info("No social links found")
                
    elif scrape_clicked and not url_input:
        st.warning("Please enter a website URL first")

elif page == "Competitive Analysis":
    st.title("🔍 Competitive Intelligence")
    st.write("Analyze pricing structure and features from target websites.")

    # Contact Information - 3 columns horizontal
    st.subheader("📞 Contact Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **LinkedIn**  
        [linkedin.com/company/saasquatchleads](https://www.linkedin.com/company/saasquatchleads/)
        """)
    
    with col2:
        st.info("""
        **Email**  
        support@saasquatchleads.com
        """)
    
    with col3:
        st.info("""
        **Office Location**  
        Caprae Capital Partners  
        Glendale, California
        """)
    
    st.divider()
    
    # Analysis Tools - Horizontal layout
    st.subheader("🚀 Analysis Tools")
    
    url_col, button_col = st.columns([3, 1])
    
    with url_col:
        target_url = st.text_input("Target URL for analysis", value="https://www.saasquatchleads.com/")
    
    with button_col:
        analyze_clicked = st.button("Analyze Pricing", type="primary", use_container_width=True)
    
    if analyze_clicked:
        with st.spinner('Analyzing website and extracting pricing data...'):
            hasil = scrape_pricing_data(target_url)
        
        if hasil and 'pricing_data' in hasil and not hasil['pricing_data'].empty:
            st.success('✅ Analysis completed!')
            
            # Convert to dictionary format for history
            pricing_data_list = []
            for _, row in hasil['pricing_data'].iterrows():
                pricing_data_list.append(row.to_dict())
            
            # Save to history
            history_entry = {
                'website': target_url,
                'pricing_data': pricing_data_list,
                'emails': [],
                'phones': [],
                'social_links': {},
                'scraper_type': 'competitive_analysis'
            }
            history_id = add_to_history(history_entry)
            st.info(f"Analysis saved to history with ID: {history_id}")
            
            # Results horizontal
            st.subheader("📊 Pricing Analysis - SaaSquatchLeads")
            
            # Display the scraped pricing table
            st.dataframe(hasil['pricing_data'], use_container_width=True, hide_index=True)
            
            # Additional insights
            st.subheader("💡 Key Insights")
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                st.metric("Total Plans", len(hasil['pricing_data'].columns) - 1)
                st.metric("Features Tracked", len(hasil['pricing_data']) - 1)  # Subtract 1 for the price row
            
            with insight_col2:
                # Find the price row
                price_row = hasil['pricing_data'][hasil['pricing_data']['Feature'] == 'Price']
                if not price_row.empty:
                    prices = price_row.iloc[0].to_dict()
                    del prices['Feature']
                    st.write("**Plan Prices:**")
                    for plan, price in prices.items():
                        st.write(f"- {plan}: {price}")
            
            # Filter & Export horizontal
            st.divider()
            filter_col, export_col = st.columns([3, 1])
            
            with filter_col:
                search_query = st.text_input("Search features", placeholder="AI, Export, Support")
                if search_query:
                    filtered_df = hasil['pricing_data'][
                        hasil['pricing_data']['Feature'].str.contains(search_query, case=False, na=False)
                    ]
                    if not filtered_df.empty:
                        st.write("**Filtered Results:**")
                        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            with export_col:
                csv_data = hasil['pricing_data'].to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="saasquatch_pricing_analysis.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            error_msg = hasil.get('error', 'Unknown error occurred') if isinstance(hasil, dict) else 'No pricing data found'
            st.warning(f"No pricing data found or error occurred: {error_msg}")
            st.info("Note: This scraper is specifically designed for the SaaSquatchLeads pricing page.")

elif page == "Contact Us":
    show_contact_section()
