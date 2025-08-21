# app.py
import streamlit as st

from contact_component import show_contact_section
from universal_scraper import scrape_universal_contact, save_scraped_data
from dashboard_component import show_dashboard, add_to_history  # Import dashboard component yang benar
import pandas as pd
import time

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

# Main content area
if page == "Dashboard":
    show_dashboard()  # Menggunakan dashboard component yang sudah diperbaiki

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
        with st.spinner('Analyzing website...'):
            hasil = scrape_saasquatch(target_url)
        
        if not hasil['pricing_data'].empty:
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
            st.subheader("📊 Pricing Analysis")
            st.dataframe(hasil['pricing_data'], use_container_width=True, hide_index=True)
            
            # Filter & Export horizontal
            filter_col, export_col = st.columns([3, 1])
            
            with filter_col:
                search_query = st.text_input("Search features", placeholder="AI, Export, Support")
            
            with export_col:
                csv_data = hasil['pricing_data'].to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="pricing_analysis.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("No pricing data found or error occurred during scraping")

elif page == "Contact Us":
    show_contact_section()
