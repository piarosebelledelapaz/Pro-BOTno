"""
Page 1: New Case Intake
Handles audio upload, transcription, form processing, and initial assessment
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import tempfile
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        st.stop()
    return OpenAI(api_key=api_key)

def create_case_directory(unhcr_number: str) -> str:
    """Create directory for case files"""
    cases_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cases")
    os.makedirs(cases_dir, exist_ok=True)
    
    case_dir = os.path.join(cases_dir, unhcr_number)
    os.makedirs(case_dir, exist_ok=True)
    
    # Create subdirectories
    os.makedirs(os.path.join(case_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "forms"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "transcripts"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "reports"), exist_ok=True)
    
    return case_dir

def transcribe_audio(audio_file, client: OpenAI) -> tuple[str, str]:
    """
    Transcribe and translate audio using Whisper
    Returns: (transcription, translation)
    """
    # Get the original file extension
    file_extension = os.path.splitext(audio_file.name)[1] if hasattr(audio_file, 'name') else '.mp3'
    
    # Save uploaded file temporarily with correct extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_path = tmp_file.name
    
    try:
        # Transcribe (original language)
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        
        # Translate to English
        with open(tmp_path, "rb") as audio:
            translation = client.audio.translations.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        
        return str(transcription), str(translation)
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

# Page configuration
st.title("📝 New Case Intake")
st.markdown("Upload case materials and begin the assessment process")

# Initialize session state
if "case_data" not in st.session_state:
    st.session_state.case_data = {}
if "step" not in st.session_state:
    st.session_state.step = 1
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "follow_up_questions" not in st.session_state:
    st.session_state.follow_up_questions = []

# Progress indicator
progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
with progress_col1:
    if st.session_state.step >= 1:
        st.success("1️⃣ Upload")
    else:
        st.info("1️⃣ Upload")
with progress_col2:
    if st.session_state.step >= 2:
        st.success("2️⃣ Transcribe")
    else:
        st.info("2️⃣ Transcribe")
with progress_col3:
    if st.session_state.step >= 3:
        st.success("3️⃣ Assess")
    else:
        st.info("3️⃣ Assess")
with progress_col4:
    if st.session_state.step >= 4:
        st.success("4️⃣ Complete")
    else:
        st.info("4️⃣ Complete")

st.markdown("---")

# Step 1: Upload Files
if st.session_state.step == 1:
    st.subheader("Step 1: Upload Case Materials")
    
    with st.form("upload_form"):
        # Basic information
        st.markdown("#### Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            asylum_seeker_name = st.text_input(
                "Asylum Seeker Name *",
                help="Full name of the asylum seeker"
            )
        
        with col2:
            unhcr_number = st.text_input(
                "UNHCR Registration Number *",
                help="Unique UNHCR registration identifier"
            )
        
        # Audio upload
        st.markdown("#### Interview Audio")
        audio_file = st.file_uploader(
            "Upload Interview Audio *",
            type=["mp3", "wav", "m4a", "ogg"],
            help="Audio file in any language - will be transcribed and translated"
        )
        
        # PDF uploads
        st.markdown("#### Supporting Documents")
        pdf_files = st.file_uploader(
            "Upload PDF Forms",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload asylum application forms and other documents"
        )
        
        # Additional context
        st.markdown("#### Additional Information (Optional)")
        additional_context = st.text_area(
            "Additional Context",
            help="Any additional information about the case",
            height=100
        )
        
        submit_button = st.form_submit_button("Process Files")
        
        if submit_button:
            if not asylum_seeker_name or not unhcr_number or not audio_file:
                st.error("Please fill in all required fields marked with *")
            else:
                # Store data
                st.session_state.case_data["name"] = asylum_seeker_name
                st.session_state.case_data["unhcr_number"] = unhcr_number
                st.session_state.case_data["additional_context"] = additional_context
                st.session_state.case_data["audio_file"] = audio_file
                st.session_state.case_data["pdf_files"] = pdf_files
                
                # Move to next step
                st.session_state.step = 2
                st.rerun()

# Step 2: Transcription and Translation
elif st.session_state.step == 2:
    st.subheader("Step 2: Processing Audio")
    
    st.info(f"**Case:** {st.session_state.case_data['name']} ({st.session_state.case_data['unhcr_number']})")
    
    if "transcription" not in st.session_state.case_data:
        with st.spinner("🎤 Transcribing and translating audio... This may take a few minutes."):
            client = get_openai_client()
            
            # Transcribe and translate
            transcription, translation = transcribe_audio(
                st.session_state.case_data["audio_file"],
                client
            )
            
            st.session_state.case_data["transcription"] = transcription
            st.session_state.case_data["translation"] = translation
            
            # Process PDFs
            forms_text = ""
            if st.session_state.case_data.get("pdf_files"):
                for pdf in st.session_state.case_data["pdf_files"]:
                    forms_text += f"\n\n--- {pdf.name} ---\n\n"
                    forms_text += extract_text_from_pdf(pdf)
            
            st.session_state.case_data["forms_text"] = forms_text
            
            st.success("✅ Processing complete!")
            st.rerun()
    
    # Display results
    st.success("✅ Audio processed successfully!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Original Transcription")
        with st.expander("View Full Transcription", expanded=False):
            st.text_area(
                "Original Language",
                st.session_state.case_data["transcription"],
                height=200,
                disabled=True
            )
    
    with col2:
        st.markdown("#### English Translation")
        with st.expander("View Full Translation", expanded=True):
            st.text_area(
                "English",
                st.session_state.case_data["translation"],
                height=200,
                disabled=True
            )
    
    if st.session_state.case_data.get("forms_text"):
        st.markdown("#### Extracted Form Data")
        with st.expander("View Extracted Text", expanded=False):
            st.text_area(
                "Forms",
                st.session_state.case_data["forms_text"][:1000] + "...",
                height=150,
                disabled=True
            )
    
    if st.button("Continue to Assessment →"):
        st.session_state.step = 3
        st.rerun()

# Step 3: Interactive Assessment
elif st.session_state.step == 3:
    st.subheader("Step 3: Interactive Assessment")
    
    st.info(f"**Case:** {st.session_state.case_data['name']} ({st.session_state.case_data['unhcr_number']})")
    
    # Generate follow-up questions if not already done
    if not st.session_state.follow_up_questions:
        with st.spinner("🤔 Analyzing case and generating follow-up questions..."):
            # Import case processor
            from backend.case_processor import CaseProcessor
            
            processor = CaseProcessor()
            
            # Build case summary
            case_info = f"""
            Name: {st.session_state.case_data['name']}
            UNHCR Number: {st.session_state.case_data['unhcr_number']}
            
            Interview Translation:
            {st.session_state.case_data['translation'][:1000]}
            
            Additional Context:
            {st.session_state.case_data.get('additional_context', 'None provided')}
            """
            
            questions = processor.ask_follow_up_questions(case_info)
            st.session_state.follow_up_questions = questions
    
    # Display questions and chat interface
    st.markdown("### 💬 Follow-up Questions")
    st.markdown("The AI has identified areas that need clarification. Please provide answers to help build a complete case file.")
    
    # Show suggested questions
    with st.expander("📋 Suggested Questions", expanded=True):
        for i, question in enumerate(st.session_state.follow_up_questions, 1):
            st.markdown(f"**{i}.** {question}")
    
    st.markdown("---")
    
    # Chat interface
    st.markdown("### Chat with AI Assistant")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your response or ask a question..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                client = get_openai_client()
                
                # Build context
                context = f"""
                Case Context:
                - Name: {st.session_state.case_data['name']}
                - UNHCR Number: {st.session_state.case_data['unhcr_number']}
                - Interview: {st.session_state.case_data['translation'][:500]}...
                
                You are helping gather information for a refugee case assessment to build a legal case to petition for asylum.
                Be empathetic, professional, and focused on gathering legally relevant information.

                Once you've gathered what you believe is sufficient information, ask the user if they have any more information, then ask the user to end to the session by clicking the button below.
                """
                
                messages = [
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}
                ]
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message.content
                
                st.markdown(assistant_message)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
    
    st.markdown("---")
    
    # Completion button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Complete Assessment and Generate Report", type="primary", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

# Step 4: Case Processing and Completion
elif st.session_state.step == 4:
    st.subheader("Step 4: Generating Legal Analysis")
    
    st.info(f"**Case:** {st.session_state.case_data['name']} ({st.session_state.case_data['unhcr_number']})")
    
    if "legal_analysis" not in st.session_state.case_data:
        with st.spinner("⚖️ Running comprehensive legal analysis... This may take up to 15 minutes. It is safe to close this tab. The final information will be sent to your lawyer."):
            # Import processors
            from backend.case_processor import CaseProcessor
            from backend.pdf_generator import PDFReportGenerator
            
            # Create case directory
            case_dir = create_case_directory(st.session_state.case_data['unhcr_number'])
            
            # Save original files with correct extension
            audio_file_obj = st.session_state.case_data["audio_file"]
            audio_extension = os.path.splitext(audio_file_obj.name)[1] if hasattr(audio_file_obj, 'name') else '.mp3'
            audio_path = os.path.join(case_dir, "audio", f"interview{audio_extension}")
            with open(audio_path, "wb") as f:
                audio_file_obj.seek(0)
                f.write(audio_file_obj.read())
            
            # Save transcripts
            trans_path = os.path.join(case_dir, "transcripts", "original.txt")
            with open(trans_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.case_data["transcription"])
            
            trans_en_path = os.path.join(case_dir, "transcripts", "english.txt")
            with open(trans_en_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.case_data["translation"])
            
            # Save forms
            form_paths = []
            if st.session_state.case_data.get("pdf_files"):
                for pdf in st.session_state.case_data["pdf_files"]:
                    pdf_path = os.path.join(case_dir, "forms", pdf.name)
                    with open(pdf_path, "wb") as f:
                        pdf.seek(0)
                        f.write(pdf.read())
                    form_paths.append(pdf_path)
            
            # Process case
            processor = CaseProcessor()
            
            case_summary = f"""
            Case Summary for {st.session_state.case_data['name']}
            UNHCR Number: {st.session_state.case_data['unhcr_number']}
            
            {st.session_state.case_data.get('additional_context', '')}
            """
            
            legal_analysis = processor.process_case(
                case_summary=case_summary,
                transcription=st.session_state.case_data["translation"],
                forms_text=st.session_state.case_data.get("forms_text"),
                chat_history=st.session_state.chat_history
            )
            
            st.session_state.case_data["legal_analysis"] = legal_analysis
            
            # Extract case summary from chat history
            case_summary_info = processor.extract_case_summary_from_chat(
                st.session_state.chat_history,
                st.session_state.case_data["translation"]
            )
            
            # Generate PDF report
            pdf_generator = PDFReportGenerator()
            
            pdf_path = os.path.join(case_dir, "reports", "legal_analysis.pdf")
            
            case_data_for_pdf = {
                "name": st.session_state.case_data["name"],
                "unhcr_number": st.session_state.case_data["unhcr_number"],
                "personal_info": {
                    "UNHCR Number": st.session_state.case_data["unhcr_number"],
                    "Name": st.session_state.case_data["name"]
                },
                "overview": case_summary_info["overview"],
                "family_composition": case_summary_info["family_composition"]
            }
            
            pdf_generator.generate_report(
                output_path=pdf_path,
                case_data=case_data_for_pdf,
                legal_analysis=legal_analysis,
                transcription=st.session_state.case_data["translation"],
                forms_text=st.session_state.case_data.get("forms_text"),
                forms_files=form_paths
            )
            
            st.session_state.case_data["pdf_path"] = pdf_path
            
            # Save case metadata
            metadata = {
                "unhcr_number": st.session_state.case_data["unhcr_number"],
                "name": st.session_state.case_data["name"],
                "created_at": datetime.now().isoformat(),
                "audio_file": audio_path,
                "transcript_original": trans_path,
                "transcript_english": trans_en_path,
                "forms": form_paths,
                "pdf_report": pdf_path
            }
            
            metadata_path = os.path.join(case_dir, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            st.success("✅ Analysis complete!")
            st.rerun()
    
    # Display completion
    st.success("🎉 Case Analysis Complete!")
    
    st.markdown("""
    ### Summary
    
    Your case has been successfully processed and analyzed. The system has:
    
    - ✅ Transcribed and translated the interview
    - ✅ Processed all uploaded forms
    - ✅ Conducted comprehensive legal research
    - ✅ Generated a professional report with appendices
    - ✅ Created bibliography with legal citations
    """)
    
    # Display report location
    st.info(f"""
    **📁 Case Files Location:**
    
    All files have been saved to: `cases/{st.session_state.case_data['unhcr_number']}/`
    
    - Audio recording
    - Transcripts (original and English)
    - Uploaded forms
    - Legal analysis report (PDF)
    """)
    
    # Download button
    if os.path.exists(st.session_state.case_data["pdf_path"]):
        with open(st.session_state.case_data["pdf_path"], "rb") as f:
            st.download_button(
                label="📥 Download Legal Analysis Report (PDF)",
                data=f,
                file_name=f"legal_analysis_{st.session_state.case_data['unhcr_number']}.pdf",
                mime="application/pdf",
                type="primary"
            )
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 View Report Details", use_container_width=True):
            st.info("Navigate to 'Case Reports' in the sidebar to view detailed analysis")
    
    with col2:
        if st.button("➕ Start New Case", use_container_width=True):
            # Reset session state
            st.session_state.case_data = {}
            st.session_state.step = 1
            st.session_state.chat_history = []
            st.session_state.follow_up_questions = []
            st.rerun()

