# UNHCR Refugee Assistance Portal

A comprehensive web portal for processing and analyzing refugee cases, built for UNHCR pro bono lawyers.

## 🎯 Overview

This portal provides an end-to-end solution for refugee case management:

1. **Audio Interview Processing**: Upload audio files in any language, automatically transcribed and translated to English using OpenAI Whisper
2. **Document Management**: Upload and process PDF forms with automatic text extraction
3. **AI-Powered Assessment**: Interactive chat interface with AI-generated follow-up questions
4. **Legal Analysis**: Comprehensive legal research using RAG and Swiss Federal Legislation (Fedlex)
5. **Professional Reports**: Generate PDF reports with appendices, bibliography, and proper legal citations

## 🚀 Quick Start

### Prerequisites

1. Python 3.8 or higher
2. OpenAI API key

### Installation

```bash
# Install dependencies
pip install -r src/requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Running the Portal

```bash
# Make the run script executable
chmod +x run_portal.sh

# Run the portal
./run_portal.sh
```

Or run directly with:

```bash
cd src
streamlit run portal.py
```

The portal will open at `http://localhost:8501`

## 📋 Features

### 1. Case Intake System

**Page: New Case Intake**

- Upload audio interviews in any language
- Automatic transcription using Whisper
- Automatic translation to English
- PDF form upload and text extraction
- UNHCR registration number tracking
- Additional context fields

### 2. Interactive Assessment

**Built-in Chat Interface**

- AI analyzes the case and generates relevant follow-up questions
- Interactive chat for clarifications
- Suggested questions based on case analysis
- Full conversation history saved

### 3. Legal Analysis Engine

**Powered by Enhanced RAG + Fedlex**

- Queries general legal document database (international law, European directives)
- Searches Swiss Federal Legislation via Fedlex SPARQL
- Extracts exact legal provisions with citations
- Generates bibliography with proper references

### 4. PDF Report Generation

**Comprehensive Legal Reports**

The generated PDF includes:

- **Title Page**: Case identification, UNHCR number, generation date
- **Executive Summary**: Personal data, overview, family composition
- **Legal Analysis**: 
  - Summary of legally relevant facts (with references to Appendix I & II)
  - Applicable law
  - Legal assessment
  - Recommendations
- **Bibliography**: 
  - General legal documents
  - Swiss federal legislation with SR numbers
- **Appendix I**: Asylum seeker forms (original files + extracted text)
- **Appendix II**: Transcribed and translated interview
- **Appendix III**: Relevant case law and legal sources

### 5. Case Management

**Page: Case Reports**

- View all processed cases
- Search by name or UNHCR number
- Sort by date or name
- Download PDF reports
- View case details and transcripts
- Access original files

## 🏗️ Architecture

### Frontend
- **Streamlit**: Multi-page web application
- **Pages**:
  - `portal.py`: Main landing page
  - `pages/1_📝_New_Case_Intake.py`: Case intake workflow
  - `pages/2_📊_Case_Reports.py`: Case viewing and management

### Backend
- **`backend/case_processor.py`**: Core legal analysis engine
  - Refactored from `refugee_case_analyzer.py`
  - Bibliography generation
  - Follow-up question generation
  - Legal summary structuring
  
- **`backend/pdf_generator.py`**: PDF report generation
  - Professional formatting with ReportLab
  - Multi-section reports with appendices
  - Bibliography with proper citations

### Legal Analysis
- **`modules/enhanced_rag.py`**: Enhanced RAG with Fedlex integration
- **`modules/fedlex_client.py`**: Swiss legislation SPARQL client
- **`prompts/fedlex_prompts.py`**: Legal analysis prompts

### Data Storage

```
src/
├── cases/
│   └── {UNHCR_NUMBER}/
│       ├── audio/
│       │   └── interview.mp3
│       ├── transcripts/
│       │   ├── original.txt
│       │   └── english.txt
│       ├── forms/
│       │   └── *.pdf
│       ├── reports/
│       │   └── legal_analysis.pdf
│       └── metadata.json
└── vector_db_data/
    └── (ChromaDB legal documents)
```

## 🔧 Configuration

### OpenAI Models

The portal uses:
- **GPT-4**: Legal analysis and chat
- **Whisper-1**: Audio transcription and translation

### Legal Databases

- **Vector DB**: ChromaDB with legal documents (international law, European directives)
- **Fedlex**: Swiss Federal Legislation via SPARQL
- **Embeddings**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

### Fedlex Configuration

In `backend/case_processor.py`:

```python
enable_fedlex = True      # Enable Swiss legislation queries
fetch_xml = True          # Fetch full legal texts
xml_language = "de"       # Language: de, fr, it, rm
```

## 📝 Usage Workflow

### Complete Case Processing

1. **Start New Case**
   - Navigate to "New Case Intake"
   - Enter asylum seeker name and UNHCR number
   - Upload audio interview file
   - Upload PDF forms (optional)
   - Add additional context (optional)
   - Click "Process Files"

2. **Review Transcription**
   - View original transcription
   - Review English translation
   - Check extracted form data
   - Continue to assessment

3. **Interactive Assessment**
   - Review AI-generated follow-up questions
   - Use chat interface to provide answers
   - Ask additional questions as needed
   - Complete when ready

4. **Generate Report**
   - System processes case in background
   - Runs comprehensive legal analysis
   - Generates professional PDF report
   - All files saved to case directory

5. **Access Report**
   - Download PDF immediately
   - Or access later from "Case Reports" page
   - View full analysis and appendices

## 🎯 Example Use Case

**Scenario**: Syrian refugee family seeking asylum in Switzerland

1. **Upload**: Audio interview in Arabic (30 minutes)
2. **Transcription**: Automatically transcribed and translated to English
3. **Forms**: Upload UNHCR registration forms (PDFs)
4. **Assessment**: AI asks about:
   - Specific persecution claims
   - Family members and dependents
   - Timeline of events
   - Previous asylum applications
5. **Analysis**: System generates comprehensive legal analysis including:
   - Relevant Swiss asylum laws (Asylgesetz)
   - Geneva Convention provisions
   - Case law on family reunification
   - Procedural requirements
6. **Report**: Professional PDF with all documentation and legal analysis

## 🔒 Security & Privacy

**Note**: This is a proof-of-concept system. For production use:

- Implement user authentication
- Add role-based access control
- Encrypt sensitive data at rest
- Use secure file storage
- Add audit logging
- Implement data retention policies
- Ensure GDPR compliance

## 📚 API Usage

### OpenAI API

**Whisper API** (Audio transcription):
```python
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)
```

**Chat Completions** (Legal analysis):
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    temperature=0
)
```

### Costs

Estimated costs per case:
- Audio transcription: ~$0.006 per minute
- Legal analysis: ~$0.50-2.00 (depends on complexity)
- **Total**: ~$1-5 per case

## 🐛 Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY='your-api-key'
```

### "Vector database not found"
Ensure you're running from the correct directory with `vector_db_data/` present.

### "Audio transcription failed"
- Check file format (supported: mp3, wav, m4a, ogg)
- Ensure file is not corrupted
- Check API key has audio transcription access

### "PDF generation failed"
```bash
pip install --upgrade reportlab PyPDF2
```

## 🚧 Limitations (PoC)

This is a proof-of-concept with the following limitations:

- No user authentication
- No access control
- No case deletion functionality
- Limited error handling
- No data encryption
- Single-user operation
- Local file storage only

## 🔮 Future Enhancements

Potential improvements:
- Multi-user authentication
- Cloud storage integration
- Case collaboration features
- Email notifications
- Advanced search and filtering
- Analytics dashboard
- Multi-language UI
- Mobile app
- API endpoints for integration

## 📄 License

See LICENSE file in the repository root.

## 🤝 Support

For technical support or questions about the portal, contact your system administrator.

---

**Built for UNHCR Pro Bono Legal Assistance**
*Supporting lawyers in providing legal representation to refugees worldwide*

