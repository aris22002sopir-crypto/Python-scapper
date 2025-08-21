# contact_component.py
import streamlit as st
import requests
from bs4 import BeautifulSoup

def scrape_contact_form():
    """
    Scrape contact form dari website SaaSQuatchLeads
    """
    try:
        url = "https://www.saasquatchleads.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        contact_section = soup.find('section', {'id': 'contact-us-section'})
        
        if contact_section:
            form = contact_section.find('form')
            form_action = form.get('action') if form else 'https://formsubmit.co/support@saasquatchleads.com'
            
            return {'form_action': form_action, 'success': True}
        else:
            return {'success': False, 'error': 'Contact section not found'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def show_contact_section():
    """
    Generating section Contact Us on clean horizontal layout 
    """
    form_data = scrape_contact_form()
    
    # CSS Styling untuk container utama
    st.markdown("""
    <style>
    .main-contact-container {
        background: linear-gradient(135deg, rgba(24, 30, 42, 0.95) 0%, rgba(30, 40, 55, 0.95) 100%);
        border-radius: 16px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .contact-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .contact-column {
        padding: 1.5rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        height: fit-content;
    }
    
    .contact-link {
        color: #818CF8;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .contact-link:hover {
        color: #A5B4FC;
        text-decoration: underline;
    }
    
    @media (max-width: 768px) {
        .main-contact-container {
            padding: 1.5rem;
        }
        
        .contact-column {
            margin: 0.5rem 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container besar yang membungkus header dan kedua kolom
    st.markdown("""
    <div class="main-contact-container">
        <div class="contact-header">
            <h1 style="color: white; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">Contact Us</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
                Have questions? Fill out the form and we'll respond within 1 business day.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Two columns horizontal layout
    left_col, right_col = st.columns(2)
    
    # LEFT COLUMN - Contact Info (dalam form terpisah)
    with left_col:
        with st.form("contact_info_form"):
            st.markdown('<div class="contact-column">📞 Get in Touch', unsafe_allow_html=True)
            st.subheader("")
            st.write("Our team is ready to assist you with any inquiries.")
            
            # Contact info menggunakan Streamlit native untuk menghindari tag HTML yang terlihat
            st.markdown("**LinkedIn**")
            st.markdown('[linkedin.com/company/saasquatchleads](https://www.linkedin.com/company/saasquatchleads/)')
            
            st.markdown("**Email**")
            st.markdown('[support@saasquatchleads.com](mailto:support@saasquatchleads.com)')
            
            st.markdown("**Office**")
            st.markdown('Caprae Capital Partners  \nGlendale, California')
            
            # Tombol untuk bagian kiri (jika diperlukan)
            info_submitted = st.form_submit_button("View Contact Info", use_container_width=True, disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # RIGHT COLUMN - Contact Form
    with right_col:
        with st.form("contact_form", clear_on_submit=True):
            st.markdown('<div class="contact-column">💬 Send us a message', unsafe_allow_html=True)
            st.subheader("")
            
            if not form_data['success']:
                st.warning("Using default contact form")
            
            # Name & Email horizontal
            name_col, email_col = st.columns(2)
            with name_col:
                name = st.text_input("Full Name", placeholder="Your name")
            with email_col:
                email = st.text_input("Email Address", placeholder="you@company.com")
            
            subject = st.text_input("Subject", placeholder="How can we help?")
            message = st.text_area("Message", placeholder="Your message here...", height=100)
            
            submitted = st.form_submit_button("Send Message", use_container_width=True)
            
            if submitted:
                if not name:
                    st.error("Please enter your name")
                elif not email or "@" not in email:
                    st.error("Please enter valid email")
                elif not message:
                    st.error("Please enter your message")
                else:
                    try:
                        form_action = form_data.get('form_action', 'https://formsubmit.co/support@saasquatchleads.com')
                        form_data_dict = {
                            'name': name, 'email': email, 'subject': subject, 'message': message,
                            '_next': 'https://your-website.com/thank-you', '_captcha': 'false'
                        }
                        
                        response = requests.post(form_action, data=form_data_dict, timeout=10)
                        
                        if response.status_code == 200:
                            st.success("✅ Message sent successfully!")
                        else:
                            st.error("Error sending message. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tutup main container
    st.markdown('</div>', unsafe_allow_html=True)