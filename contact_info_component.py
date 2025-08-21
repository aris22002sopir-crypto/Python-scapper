# contact_info_component.py
import streamlit as st

def show_contact_info(contact_data):
    """
    Menampilkan Contact Information dengan desain yang sama persis
    """
    st.markdown("""
    <style>
    .contact-info-section {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 1rem;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(30, 42, 64, 0.4);
    }
    
    .contact-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    
    .contact-info-card {
        background: rgba(18, 26, 42, 0.8);
        border: 1px solid rgba(30, 42, 64, 0.4);
        border-radius: 0.75rem;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .contact-info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0ea5e9, #3b82f6);
    }
    
    .contact-info-icon {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.75rem;
        border-radius: 50%;
        margin-bottom: 1rem;
        display: inline-flex;
    }
    
    .contact-info-icon svg {
        width: 1.5rem;
        height: 1.5rem;
        color: #0ea5e9;
    }
    
    .contact-info-title {
        color: white;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .contact-info-detail {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .contact-info-detail a {
        color: #0ea5e9;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .contact-info-detail a:hover {
        color: #3b82f6;
    }
    
    .verified-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 0.75rem;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="contact-info-section">', unsafe_allow_html=True)
    st.markdown('<div class="contact-info-grid">', unsafe_allow_html=True)
    
    # LinkedIn Card
    st.markdown(f'''
    <div class="contact-info-card">
        <div class="contact-info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8c-4.41 0-8 3.59-8 8s3.59 8 8 8 8-3.59 8-8-3.59-8-8-8zm0 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z M3 20l1.5-3.5c1.8-4.1 5.3-7 9.5-7 3.9 0 7.3 2.6 8.5 6.3L21 20H3z"/>
            </svg>
        </div>
        <div class="contact-info-title">
            LinkedIn <span class="verified-badge">Verified</span>
        </div>
        <div class="contact-info-detail">
            <a href="{contact_data.get('linkedin', '#')}" target="_blank">
                {contact_data.get('linkedin', 'N/A')}
            </a>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Email Card
    st.markdown(f'''
    <div class="contact-info-card">
        <div class="contact-info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
        </div>
        <div class="contact-info-title">
            Email <span class="verified-badge">Verified</span>
        </div>
        <div class="contact-info-detail">
            <a href="mailto:{contact_data.get('email', '')}">
                {contact_data.get('email', 'N/A')}
            </a>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Office Card
    st.markdown(f'''
    <div class="contact-info-card">
        <div class="contact-info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
        </div>
        <div class="contact-info-title">
            Office <span class="verified-badge">Verified</span>
        </div>
        <div class="contact-info-detail">
            {contact_data.get('office', 'N/A')}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)