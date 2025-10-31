# 🚀 Quick Start Guide - UNHCR Refugee Portal

## What Has Been Built

A complete web-based refugee case management portal with:

✅ **Audio Upload & Transcription** - Upload interviews in any language, automatically transcribed and translated to English  
✅ **PDF Form Processing** - Upload and extract text from asylum application forms  
✅ **AI-Powered Assessment** - Interactive chat with follow-up questions  
✅ **Legal Analysis Engine** - Comprehensive research using your existing RAG + Fedlex system  
✅ **Professional PDF Reports** - Complete with appendices, bibliography, and proper citations  
✅ **Case Management** - View, search, and download all case reports  

## Prerequisites

1. **OpenAI API Key** - Required for Whisper (transcription) and GPT-4 (legal analysis)
2. **Python 3.8+** - Already installed on your system
3. **Vector Database** - Already present in `src/vector_db_data/`

## Installation

```bash
# 1. Navigate to the project directory
cd /Users/aaron/Documents/Pro-BOTno

# 2. Install dependencies
pip install -r src/requirements.txt

# 3. Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## Running the Portal

### Option 1: Use the run script (recommended)

```bash
./run_portal.sh
```

### Option 2: Run directly

```bash
cd src
streamlit run portal.py
```

The portal will open automatically in your browser at **http://localhost:8501**

## Using the Portal

### Step-by-Step Workflow

#### 1. **Navigate to "New Case Intake"**
   - Click on "📝 New Case Intake" in the sidebar

#### 2. **Upload Case Materials**
   - Enter asylum seeker's name
   - Enter UNHCR registration number (e.g., "UNHCR-2024-001")
   - Upload audio interview file (mp3, wav, m4a, ogg)
   - Upload PDF forms (optional, can upload multiple)
   - Add any additional context
   - Click "Process Files"

#### 3. **Review Transcription**
   - View original transcription and English translation
   - Check extracted form data
   - Click "Continue to Assessment"

#### 4. **Interactive Assessment**
   - Review AI-generated follow-up questions
   - Use chat interface to provide answers
   - Click "Complete Assessment and Generate Report"

#### 5. **Download Report**
   - System generates comprehensive legal analysis (takes 2-5 minutes)
   - Download PDF report immediately
   - Or access later from "Case Reports" page

## What the System Does

### Audio Processing
- **Transcribes** audio in original language using Whisper
- **Translates** to English automatically
- **Saves** both versions for reference

### Legal Analysis
Your existing refugee case analyzer is integrated as a backend service:
- Queries your **ChromaDB** legal document database
- Searches **Swiss Federal Legislation** via Fedlex
- Generates **bibliography** with proper citations
- Extracts **case law** references

### PDF Report Structure

The generated PDF includes:

1. **Title Page** - Case identification
2. **Executive Summary**
   - Personal data
   - Overview of situation
   - Family composition
3. **Legal Analysis**
   - Legally relevant facts (refs to Appendix I & II)
   - Applicable law
   - Legal assessment
   - Recommendations
4. **Bibliography**
   - General legal documents
   - Swiss legislation with SR numbers
5. **Appendix I** - Asylum Seeker Forms
6. **Appendix II** - Transcribed Interview
7. **Appendix III** - Case Law and Sources

## File Structure

All case files are saved to:
```
src/cases/{UNHCR_NUMBER}/
├── audio/interview.mp3          # Original audio
├── transcripts/
│   ├── original.txt             # Original language
│   └── english.txt              # English translation
├── forms/*.pdf                  # Uploaded forms
├── reports/legal_analysis.pdf   # Final report
└── metadata.json                # Case metadata
```

## Testing with Sample Data

You can test with:
- **Audio**: Any audio file (even just a voice memo)
- **Text**: Use one of your sample cases:
  - `examples/sample_cases/case1_syrian_family.txt`
  - `examples/sample_cases/case2_unaccompanied_minor.txt`

For testing without audio files, you can create a simple audio recording or use text-to-speech.

## What's Different from Before

### Before
- Command-line tool (`refugee_case_analyzer.py`)
- Manual case description input
- Text output only
- No document management

### Now
- **Web portal** with multi-page interface
- **Audio upload** with automatic transcription
- **PDF form processing** with text extraction
- **Interactive chat** for follow-up questions
- **Professional PDF reports** with appendices
- **Case management** system
- **Bibliography generation** with citations
- **References to appendices** in legal analysis

## Key Features

### 1. Multi-Language Support
Upload audio in **any language** - Whisper automatically detects and translates

### 2. Smart Follow-Up Questions
AI analyzes the case and generates relevant questions to gather more information

### 3. Clean Backend Architecture
Your `refugee_case_analyzer.py` has been refactored into:
- `backend/case_processor.py` - Core legal analysis with bibliography
- `backend/pdf_generator.py` - Professional PDF reports
- Integrated with your existing RAG + Fedlex system

### 4. Professional Reports
PDFs include:
- Proper legal citations
- References to appendices (e.g., "see Appendix II")
- Bibliography section
- Source document excerpts

## Troubleshooting

### "OpenAI API key not found"
```bash
# Make sure you've set the environment variable
export OPENAI_API_KEY='sk-...'

# Verify it's set
echo $OPENAI_API_KEY
```

### "Vector database not found"
Make sure you're in the right directory:
```bash
ls src/vector_db_data/
# Should show: chroma.sqlite3 and other database files
```

### "Port 8501 already in use"
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run src/portal.py --server.port 8502
```

## API Costs (Approximate)

Per case:
- **Whisper transcription**: ~$0.006/minute of audio
- **GPT-4 analysis**: ~$0.50-2.00 depending on complexity
- **Total**: ~$1-5 per case

Example: 30-minute interview + analysis ≈ $2.50

## Next Steps

1. **Test the system** with a sample case
2. **Review the generated PDF** to ensure it meets your needs
3. **Customize prompts** in `src/prompts/fedlex_prompts.py` if needed
4. **Adjust settings** in `src/backend/case_processor.py`

## Support Files

- **Full Documentation**: `PORTAL_README.md`
- **Original README**: `README.md`
- **Fedlex Module Docs**: `docs/FEDLEX_MODULE.md`

## Configuration

Default settings in `src/backend/case_processor.py`:
```python
llm_model = "gpt-4"          # LLM for analysis
enable_fedlex = True         # Swiss legislation
fetch_xml = True             # Full legal texts
xml_language = "de"          # German (also: fr, it, rm)
```

## Development Notes

This is a **proof-of-concept** system:
- ✅ Ready for testing and demonstration
- ⚠️ No authentication (single-user)
- ⚠️ No encryption (local files only)
- ⚠️ Not production-ready

For production use, you would need:
- User authentication
- Access control
- Data encryption
- Cloud storage
- Audit logging

## Questions?

See `PORTAL_README.md` for comprehensive documentation.

---

**Built on your existing Pro-BOTno legal assistance system**  
*Integrating your RAG + Fedlex architecture with a modern web interface*

