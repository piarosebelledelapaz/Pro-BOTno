"""
UNHCR Refugee Assistance Portal
Main entry point for the multi-page Streamlit application
"""

import streamlit as st
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="UNHCR Refugee Assistance Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e0f2fe;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0284c7;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #dcfce7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #16a34a;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #eab308;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🛡️ UNHCR Portal")
st.sidebar.markdown("---")

# Main content
st.markdown('<h1 class="main-header">🛡️ UNHCR Refugee Assistance Portal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Supporting Pro Bono Lawyers in Refugee Legal Assistance</p>', unsafe_allow_html=True)

st.markdown("---")

# Welcome message
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div class="info-box">
    <h3>Welcome to the UNHCR Refugee Assistance Portal</h3>
    <p>This portal provides comprehensive tools for processing and analyzing refugee cases.</p>
    </div>
    """, unsafe_allow_html=True)

# Features overview
st.markdown("### 📋 Portal Features")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.markdown("""
    #### 🎤 Case Intake System
    - Upload audio interviews (any language)
    - Automatic transcription with Whisper
    - Translation to English
    - PDF form upload and processing
    - UNHCR registration tracking
    """)
    
    st.markdown("""
    #### 💬 Interactive Assessment
    - AI-powered follow-up questions
    - Chat interface for clarifications
    - Comprehensive case documentation
    - Real-time case summary generation
    """)

with feature_col2:
    st.markdown("""
    #### ⚖️ Legal Analysis
    - Advanced RAG-based legal research
    - Swiss Federal Legislation (Fedlex) integration
    - International refugee law database
    - Case law and precedent analysis
    """)
    
    st.markdown("""
    #### 📄 Report Generation
    - Professional PDF reports
    - Comprehensive appendices
    - Bibliography with citations
    - Ready for legal review
    """)

st.markdown("---")

# Getting started
st.markdown("### 🚀 Getting Started")

st.markdown("""
1. **Navigate to "New Case Intake"** in the sidebar to begin processing a new refugee case
2. **Upload required documents**: Audio interview and PDF forms
3. **Complete the interactive assessment** with AI-generated follow-up questions
4. **Generate the legal analysis** which processes in the background
5. **Review the final report** in the "Case Reports" section
""")

st.markdown("---")

# System status
st.markdown("### 🔧 System Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    # Check OpenAI API
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API Connected")
    else:
        st.error("❌ OpenAI API Key Missing")

with status_col2:
    # Check vector database
    db_path = os.path.join(os.path.dirname(__file__), "vector_db_data")
    if os.path.exists(db_path):
        st.success("✅ Legal Database Loaded")
    else:
        st.error("❌ Legal Database Not Found")

with status_col3:
    # Check case storage
    cases_path = os.path.join(os.path.dirname(__file__), "cases")
    if os.path.exists(cases_path):
        case_count = len([d for d in os.listdir(cases_path) if os.path.isdir(os.path.join(cases_path, d))])
        st.info(f"📁 {case_count} Cases Stored")
    else:
        st.info("📁 0 Cases Stored")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem 0;">
    <p><strong>UNHCR Pro Bono Legal Assistance System</strong></p>
    <p>For technical support, contact your system administrator</p>
    <p><em>This is a proof-of-concept system for demonstration purposes</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Navigation")
st.sidebar.info("""
Use the pages in the sidebar to:
- **New Case Intake**: Start a new case
- **Case Reports**: View generated reports
- **System Status**: Check system health
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configuration")
st.sidebar.text(f"Model: GPT-5")
st.sidebar.text(f"Fedlex: Enabled")
st.sidebar.text(f"Language: Multi-lingual")

