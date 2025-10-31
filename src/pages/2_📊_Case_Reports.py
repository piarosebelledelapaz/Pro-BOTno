"""
Page 2: Case Reports
View and download completed case analysis reports
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_case_metadata(case_dir: str) -> dict:
    """Load case metadata from JSON file"""
    metadata_path = os.path.join(case_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return None

def get_all_cases() -> list:
    """Get list of all case directories"""
    cases_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cases")
    
    if not os.path.exists(cases_dir):
        return []
    
    cases = []
    for case_dir in os.listdir(cases_dir):
        full_path = os.path.join(cases_dir, case_dir)
        if os.path.isdir(full_path):
            metadata = load_case_metadata(full_path)
            if metadata:
                metadata["case_dir"] = full_path
                cases.append(metadata)
    
    # Sort by creation date (newest first)
    cases.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return cases

# Page configuration
st.title("📊 Case Reports")
st.markdown("View and access completed legal analysis reports")

st.markdown("---")

# Get all cases
cases = get_all_cases()

if not cases:
    st.info("""
    ### No Cases Found
    
    No case reports have been generated yet. 
    
    To create a new case report:
    1. Navigate to **"New Case Intake"** in the sidebar
    2. Upload case materials
    3. Complete the assessment process
    """)
    
else:
    st.success(f"**{len(cases)}** case(s) found")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search by name or UNHCR number",
            placeholder="Enter name or UNHCR number..."
        )
    
    with col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Name (A-Z)", "Name (Z-A)"]
        )
    
    # Filter cases
    filtered_cases = cases
    
    if search_term:
        search_term = search_term.lower()
        filtered_cases = [
            c for c in cases
            if search_term in c.get("name", "").lower() or
               search_term in c.get("unhcr_number", "").lower()
        ]
    
    # Sort cases
    if sort_option == "Oldest First":
        filtered_cases.sort(key=lambda x: x.get("created_at", ""))
    elif sort_option == "Name (A-Z)":
        filtered_cases.sort(key=lambda x: x.get("name", ""))
    elif sort_option == "Name (Z-A)":
        filtered_cases.sort(key=lambda x: x.get("name", ""), reverse=True)
    
    st.markdown("---")
    
    # Display cases
    if not filtered_cases:
        st.warning("No cases match your search criteria")
    else:
        for i, case in enumerate(filtered_cases):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### {case.get('name', 'Unknown')}")
                    st.markdown(f"**UNHCR Number:** `{case.get('unhcr_number', 'N/A')}`")
                
                with col2:
                    created_date = datetime.fromisoformat(case.get('created_at', ''))
                    st.markdown(f"**Created:** {created_date.strftime('%B %d, %Y')}")
                    st.markdown(f"**Time:** {created_date.strftime('%H:%M')}")
                
                with col3:
                    # Download PDF button
                    pdf_path = case.get("pdf_report")
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download",
                                data=f,
                                file_name=f"report_{case.get('unhcr_number')}.pdf",
                                mime="application/pdf",
                                key=f"download_{i}"
                            )
                    else:
                        st.warning("PDF not found")
                
                # Expandable details
                with st.expander("📋 View Case Details"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("#### Files")
                        
                        # Audio file
                        if case.get("audio_file"):
                            if os.path.exists(case["audio_file"]):
                                st.success(f"✅ Audio: {os.path.basename(case['audio_file'])}")
                            else:
                                st.error("❌ Audio file missing")
                        
                        # Transcripts
                        if case.get("transcript_english"):
                            if os.path.exists(case["transcript_english"]):
                                st.success("✅ English Transcript")
                                
                                # Show transcript preview
                                with open(case["transcript_english"], "r", encoding="utf-8") as f:
                                    transcript = f.read()
                                    with st.expander("Preview Transcript"):
                                        st.text_area(
                                            "English Translation",
                                            transcript[:500] + "...",
                                            height=150,
                                            disabled=True
                                        )
                        
                        # Forms
                        form_count = len(case.get("forms", []))
                        if form_count > 0:
                            st.success(f"✅ {form_count} PDF form(s)")
                    
                    with detail_col2:
                        st.markdown("#### Actions")
                        
                        action_col1, action_col2 = st.columns(2)
                        
                        with action_col1:
                            # View full report button
                            if st.button("🔍 View Analysis", key=f"view_{i}"):
                                st.session_state.selected_case = case
                                st.session_state.show_analysis = True
                        
                        with action_col2:
                            # Open folder button
                            if st.button("📁 Open Folder", key=f"folder_{i}"):
                                case_dir = case.get("case_dir")
                                st.info(f"Case files location:\n\n`{case_dir}`")
                        
                        st.markdown("---")
                        
                        # Delete button (with confirmation)
                        if st.button("🗑️ Delete Case", key=f"delete_{i}", type="secondary"):
                            st.warning("⚠️ Delete functionality not implemented in this PoC")
                
                st.markdown("---")
        
        # Show analysis if selected
        if st.session_state.get("show_analysis"):
            selected_case = st.session_state.get("selected_case")
            
            st.markdown("---")
            st.markdown("## 📄 Legal Analysis Report")
            
            if selected_case:
                st.markdown(f"### {selected_case.get('name')} - {selected_case.get('unhcr_number')}")
                
                # Show PDF using iframe
                pdf_path = selected_case.get("pdf_report")
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    st.markdown("#### PDF Report")
                    st.info("Download the PDF using the button above to view the full report with all formatting and appendices.")
                    
                    # Display basic information
                    st.markdown("#### Report Contents")
                    
                    with st.expander("📑 Report Structure", expanded=True):
                        st.markdown("""
                        The legal analysis report includes:
                        
                        1. **Executive Summary**
                           - Personal data
                           - Overview of situation
                           - Family composition
                        
                        2. **Legal Analysis and Recommendations**
                           - Summary of legally relevant facts
                           - Applicable law
                           - Legal assessment
                           - Conclusions and recommendations
                        
                        3. **Bibliography**
                           - General legal documents cited
                           - Swiss federal legislation referenced
                        
                        4. **Appendix I: Asylum Seeker Forms**
                           - Original submitted forms
                           - Extracted content
                        
                        5. **Appendix II: Transcribed Interview**
                           - Full interview transcript
                           - English translation
                        
                        6. **Appendix III: Relevant Case Law**
                           - Case law summary
                           - Referenced legal documents
                           - Source excerpts
                        """)
                    
                    # Show transcript
                    transcript_path = selected_case.get("transcript_english")
                    if transcript_path and os.path.exists(transcript_path):
                        with st.expander("📝 Interview Transcript (English)", expanded=False):
                            with open(transcript_path, "r", encoding="utf-8") as f:
                                transcript = f.read()
                            st.text_area(
                                "Full Transcript",
                                transcript,
                                height=300,
                                disabled=True
                            )
                    
                    if st.button("← Back to Case List"):
                        st.session_state.show_analysis = False
                        st.rerun()
                else:
                    st.error("PDF report not found")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Statistics")
st.sidebar.metric("Total Cases", len(cases))

if cases:
    # Calculate some stats
    this_week = sum(1 for c in cases if 
                   (datetime.now() - datetime.fromisoformat(c.get('created_at', ''))).days <= 7)
    st.sidebar.metric("This Week", this_week)
    
    this_month = sum(1 for c in cases if 
                    (datetime.now() - datetime.fromisoformat(c.get('created_at', ''))).days <= 30)
    st.sidebar.metric("This Month", this_month)

