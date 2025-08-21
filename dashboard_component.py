# dashboard_component.py (updated version with fixed autocomplete)
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from universal_scraper import scrape_universal_data, save_scraped_data

HISTORY_FILE = "scraping_history.json"

def init_history():
    """Initialize the scraping history file if it doesn't exist"""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

def save_to_history(scraping_data):
    """Save scraping data to history file"""
    init_history()
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    scraping_data['timestamp'] = datetime.now().isoformat()
    scraping_data['id'] = len(history) + 1
    history.append(scraping_data)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    return scraping_data['id']

def get_history():
    """Retrieve scraping history"""
    init_history()
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def clear_history():
    """Clear all scraping history"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    st.success("History cleared successfully!")
    st.rerun()

def show_dashboard():
    """Show dashboard with scraped website data"""
    st.title("📊 Analytics Dashboard")
    
    # Menghapus bagian input URL karena sudah ada di halaman universal scraper
    
    st.divider()
    
    history = get_history()
    
    # Metrics Row - Horizontal
    st.subheader("📈 Performance Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Scrapes", str(len(history)))
    with col2:
        total_emails = sum(len(item.get('emails', [])) for item in history)
        st.metric("Total Emails", str(total_emails))
    with col3:
        total_phones = sum(len(item.get('phones', [])) for item in history)
        st.metric("Total Phones", str(total_phones))
    with col4:
        total_social = sum(len(item.get('social_links', {})) for item in history)
        st.metric("Social Links", str(total_social))
    #with col5:
     #   if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
      #      clear_history()
    
    st.divider()
    
    # Scraped Website Data Table with Filters
    st.subheader("🌐 Scraped Website Data")
    
    if history:
        # Create a list to store all scraped data
        all_scraped_data = []
        
        for item in history:
            website = item.get('website', 'Unknown')
            timestamp = item.get('timestamp', '')
            date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else 'Unknown'
            scraper_type = item.get('scraper_type', 'universal')
            
            # Add emails
            for email in item.get('emails', []):
                all_scraped_data.append({
                    'Website': website,
                    'Date': date,
                    'Type': 'Email',
                    'Value': email,
                    'URL': website,
                    'Source': scraper_type,
                    'Scrape ID': item.get('id', 'N/A')
                })
            
            # Add phones
            for phone in item.get('phones', []):
                all_scraped_data.append({
                    'Website': website,
                    'Date': date,
                    'Type': 'Phone',
                    'Value': phone,
                    'URL': website,
                    'Source': scraper_type,
                    'Scrape ID': item.get('id', 'N/A')
                })
            
            # Add social links
            for platform, link in item.get('social_links', {}).items():
                all_scraped_data.append({
                    'Website': website,
                    'Date': date,
                    'Type': f'Social ({platform})',
                    'Value': link,
                    'URL': website,
                    'Source': scraper_type,
                    'Scrape ID': item.get('id', 'N/A')
                })
            
            # Add pricing data (from competitive analysis)
            for pricing_item in item.get('pricing_data', []):
                if isinstance(pricing_item, dict):
                    # Convert dict to readable string
                    pricing_str = ", ".join([f"{k}: {v}" for k, v in pricing_item.items()])
                    all_scraped_data.append({
                        'Website': website,
                        'Date': date,
                        'Type': 'Pricing Plan',
                        'Value': pricing_str,
                        'URL': website,
                        'Source': scraper_type,
                        'Scrape ID': item.get('id', 'N/A')
                    })
                elif isinstance(pricing_item, list):
                    # Handle list format pricing data
                    pricing_str = ", ".join([str(x) for x in pricing_item])
                    all_scraped_data.append({
                        'Website': website,
                        'Date': date,
                        'Type': 'Pricing Plan',
                        'Value': pricing_str,
                        'URL': website,
                        'Source': scraper_type,
                        'Scrape ID': item.get('id', 'N/A')
                    })
        
        if all_scraped_data:
            # Create DataFrame
            scraped_df = pd.DataFrame(all_scraped_data)
            
            # Filter Section - Horizontal Layout
            st.subheader("🔍 Filter Data")
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                # Website filter dropdown
                websites = sorted(scraped_df['Website'].unique())
                selected_websites = st.multiselect(
                    "Filter by Website",
                    options=websites,
                    default=websites,
                    help="Select websites to display"
                )
            
            with filter_col2:
                # Data type filter dropdown
                data_types = sorted(scraped_df['Type'].unique())
                selected_types = st.multiselect(
                    "Filter by Data Type",
                    options=data_types,
                    default=data_types,
                    help="Select data types to display"
                )
            
            with filter_col3:
                # Source filter dropdown
                sources = sorted(scraped_df['Source'].unique())
                selected_sources = st.multiselect(
                    "Filter by Source",
                    options=sources,
                    default=sources,
                    help="Select scraper types to display"
                )
            
            with filter_col4:
                # Search filter dengan autocomplete yang benar
                search_term = st.text_input(
                    "Search in Values",
                    placeholder="Enter search term...",
                    help="Search within the extracted values",
                    autocomplete="on"  # Menambahkan atribut autocomplete yang valid
                )
            
            # Apply filters
            filtered_df = scraped_df[
                (scraped_df['Website'].isin(selected_websites)) &
                (scraped_df['Type'].isin(selected_types)) &
                (scraped_df['Source'].isin(selected_sources))
            ]
            
            # Apply search filter if provided
            if search_term:
                filtered_df = filtered_df[filtered_df['Value'].str.contains(search_term, case=False, na=False)]
            
            # Display stats
            st.info(f"📊 Showing {len(filtered_df)} of {len(scraped_df)} total records")
            
            # Display the table
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "URL": st.column_config.LinkColumn("Website"),
                    "Value": st.column_config.TextColumn("Extracted Value", width="large"),
                    "Scrape ID": st.column_config.NumberColumn("Scrape Session ID", format="%d")
                }
            )
            
            # Download buttons - Horizontal
            dl_col1, dl_col2 = st.columns(2)
            
            with dl_col1:
                # Download filtered data
                csv_filtered = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data as CSV",
                    data=csv_filtered,
                    file_name="filtered_scraped_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with dl_col2:
                # Download all data
                csv_all = scraped_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Data as CSV",
                    data=csv_all,
                    file_name="all_scraped_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("No detailed scraped data available yet")
    else:
        st.info("No scraping history yet. Use the Universal Scraper page to scrape websites!")
    
    st.divider()
    
    # Recent Activity with detailed view
    st.subheader("📋 Scraping Sessions")
    if history:
        # Session selection dropdown
        session_options = {item['id']: f"ID {item['id']} - {item.get('website', 'Unknown')} - {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M') if 'timestamp' in item else 'Unknown'}" 
                          for item in history}
        
        selected_session_id = st.selectbox(
            "Select a scraping session to view details:",
            options=list(session_options.keys()),
            format_func=lambda x: session_options[x]
        )
        
        # Display selected session details
        selected_session = next((item for item in history if item['id'] == selected_session_id), None)
        
        if selected_session:
            session_col1, session_col2 = st.columns([1, 2])
            
            with session_col1:
                st.write("**Session Overview**")
                st.write(f"**Website:** {selected_session.get('website', 'Unknown')}")
                st.write(f"**Date:** {datetime.fromisoformat(selected_session['timestamp']).strftime('%Y-%m-%d %H:%M') if 'timestamp' in selected_session else 'Unknown'}")
                st.write(f"**Scraper Type:** {selected_session.get('scraper_type', 'universal').replace('_', ' ').title()}")
                st.write(f"**Session ID:** {selected_session.get('id', 'N/A')}")
            
            with session_col2:
                st.write("**Extracted Data Summary**")
                
                summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                
                with summary_col1:
                    st.metric("Emails", len(selected_session.get('emails', [])))
                
                with summary_col2:
                    st.metric("Phones", len(selected_session.get('phones', [])))
                
                with summary_col3:
                    st.metric("Social Links", len(selected_session.get('social_links', {})))
                
                with summary_col4:
                    st.metric("Pricing Plans", len(selected_session.get('pricing_data', [])))
            
            # Detailed data from selected session
            st.write("**Detailed Data**")
            
            # Emails
            if selected_session.get('emails'):
                with st.expander(f"📧 Emails ({len(selected_session['emails'])})"):
                    for email in selected_session['emails']:
                        st.code(email)
            
            # Phone numbers
            if selected_session.get('phones'):
                with st.expander(f"📞 Phone Numbers ({len(selected_session['phones'])})"):
                    for phone in selected_session['phones']:
                        st.code(phone)
            
            # Social links
            if selected_session.get('social_links'):
                with st.expander(f"📱 Social Links ({len(selected_session['social_links'])})"):
                    for platform, link in selected_session['social_links'].items():
                        st.write(f"**{platform.upper()}**: {link}")
            
            # Pricing data
            if selected_session.get('pricing_data'):
                with st.expander(f"💰 Pricing Data ({len(selected_session['pricing_data'])})"):
                    if all(isinstance(item, dict) for item in selected_session['pricing_data']):
                        pricing_df = pd.DataFrame(selected_session['pricing_data'])
                        st.dataframe(pricing_df, use_container_width=True, hide_index=True)
                    else:
                        for i, item in enumerate(selected_session['pricing_data']):
                            st.write(f"**Item {i+1}:** {str(item)}")
    else:
        st.info("No scraping history yet")

def add_to_history(scraping_data):
    """Add new scraping data to history (alias for save_to_history)"""
    return save_to_history(scraping_data)
