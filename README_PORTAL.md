# 🛡️ UNHCR Refugee Assistance Portal

> **Complete web-based system for processing and analyzing refugee cases**

---

## 📖 Quick Navigation

| Document | Purpose | Read When |
|----------|---------|-----------|
| **START_HERE.md** | Quick start guide | 🚀 First time setup |
| **VISUAL_GUIDE.md** | System diagrams | 👀 Understanding structure |
| **PROJECT_COMPLETE.md** | Project summary | 📋 What was built |
| **PORTAL_README.md** | Full documentation | 📚 Detailed reference |
| **IMPLEMENTATION_SUMMARY.md** | Technical details | 🔧 Deep dive |

---

## 🎯 What This Is

A comprehensive web portal that:

1. **Accepts audio interviews** in any language → transcribes & translates
2. **Processes PDF documents** → extracts text automatically  
3. **Conducts AI assessment** → generates follow-up questions
4. **Runs legal analysis** → using your existing RAG + Fedlex system
5. **Generates PDF reports** → with bibliography and appendices
6. **Manages all cases** → search, view, download

---

## 🚀 Get Started in 3 Steps

```bash
# 1. Install dependencies
pip install -r src/requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY='your-key-here'

# 3. Run the portal
./run_portal.sh
```

Open browser: **http://localhost:8501**

---

## 📦 What Was Delivered

### New Files (11 total)

**Application (3 files)**
- `src/portal.py` - Main landing page
- `src/pages/1_📝_New_Case_Intake.py` - Upload & processing
- `src/pages/2_📊_Case_Reports.py` - View & manage cases

**Backend (3 files)**
- `src/backend/__init__.py` - Package init
- `src/backend/case_processor.py` - Legal analysis engine
- `src/backend/pdf_generator.py` - PDF report generation

**Scripts (2 files)**
- `run_portal.sh` - Portal startup script
- `check_setup.py` - Setup verification

**Documentation (5 files)**
- `START_HERE.md` - Quick start guide ⭐
- `PROJECT_COMPLETE.md` - Project summary
- `PORTAL_README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `VISUAL_GUIDE.md` - System diagrams
- `README_PORTAL.md` - This file

### Modified Files (1 file)
- `src/requirements.txt` - Added: openai, reportlab, PyPDF2

### Integrated (Unchanged)
- ✅ All existing modules reused as-is
- ✅ ChromaDB database used directly
- ✅ Fedlex client integrated
- ✅ Prompts used without modification

---

## ✨ Key Features

### 🎤 Audio Processing
- Upload interviews in **any language**
- Automatic transcription with Whisper
- Automatic translation to English
- Both versions saved

### 📄 Document Management
- Multiple PDF upload
- Automatic text extraction
- Original files preserved
- Organized storage

### 💬 AI Assessment
- Auto-generated follow-up questions
- Interactive chat interface
- Context-aware responses
- Full history saved

### ⚖️ Legal Analysis
Your existing system enhanced with:
- Bibliography generation
- Case law extraction
- Structured summaries
- Appendix references

### 📊 PDF Reports
Professional reports with:
- Title page
- Executive summary
- Legal analysis
- Bibliography
- 3 Appendices (Forms, Interview, Case Law)

### 📁 Case Management
- View all cases
- Search by name/number
- Download PDFs
- Access transcripts

---

## 🏗️ Architecture

```
Frontend (Streamlit)
    ↓
Backend (case_processor.py)
    ↓
Legal Analysis (enhanced_rag.py + fedlex_client.py)
    ↓
Output (pdf_generator.py)
```

Built on your existing Pro-BOTno system:
- Reuses ChromaDB
- Integrates Fedlex
- Uses your prompts
- Clean separation

---

## 📊 System Comparison

| Feature | CLI Tool | New Portal |
|---------|----------|------------|
| Interface | Terminal | Web |
| Audio | Manual | Automatic |
| Documents | Text input | PDF upload |
| Assessment | None | AI questions |
| Output | Text | PDF |
| Bibliography | No | Yes |
| Appendices | No | Yes (3) |
| Storage | No | Yes |
| Management | No | Yes |

---

## 🎯 Requirements Met

All your requirements implemented:

✅ **Requirement 1**: Web portal with audio upload  
✅ **Requirement 2**: AI questions with chat interface  
✅ **Requirement 3**: Background processing with bibliography  
✅ **Requirement 4**: Professional PDF with appendices  

Plus additional features:
- Case management system
- Search functionality
- Setup verification
- Comprehensive documentation

---

## 💡 Usage Example

### Complete Workflow

1. **Upload** (2 min)
   - Audio file: 30-minute interview in Arabic
   - PDF forms: 2 UNHCR documents
   - UNHCR number: UNHCR-2024-001

2. **Process** (1-2 min)
   - Transcribe audio in Arabic
   - Translate to English
   - Extract PDF text

3. **Assess** (5-10 min)
   - AI generates 5 follow-up questions
   - Lawyer provides answers via chat
   - System gathers complete information

4. **Analyze** (2-5 min)
   - Search ChromaDB for international law
   - Query Fedlex for Swiss legislation
   - Generate bibliography
   - Extract case law

5. **Report** (10 sec)
   - Generate professional PDF
   - Include all appendices
   - Add bibliography
   - Ready to download

**Total time**: ~10-20 minutes  
**Cost**: ~$1-5 per case

---

## 📚 Documentation Structure

```
START_HERE.md
└─▶ Quick start, installation, first test

PROJECT_COMPLETE.md
└─▶ What was built, features, summary

VISUAL_GUIDE.md
└─▶ Diagrams, workflows, architecture

PORTAL_README.md
└─▶ Complete feature documentation

IMPLEMENTATION_SUMMARY.md
└─▶ Technical implementation details
```

---

## 🔧 Technical Stack

### Frontend
- Streamlit (multi-page app)
- Custom CSS styling
- File upload components
- Chat interface

### Backend
- Python 3.8+
- OpenAI API (Whisper + GPT-4)
- LangChain (RAG chains)
- ReportLab (PDF generation)

### Data
- ChromaDB (legal documents)
- Fedlex SPARQL (Swiss law)
- JSON (case metadata)
- File system (case storage)

---

## ⚙️ Configuration

### Backend Settings
File: `src/backend/case_processor.py`

```python
llm_model = "gpt-4"          # LLM model
enable_fedlex = True         # Swiss law queries
fetch_xml = True             # Full legal texts
xml_language = "de"          # German
```

### Costs
- Whisper: $0.006/min
- GPT-4: $0.50-2.00/case
- **Total**: ~$1-5/case

---

## 🧪 Testing

### Quick Test
```bash
# Verify setup
python3 check_setup.py

# Start portal
./run_portal.sh

# Create test case with:
# - Any audio file
# - Test name/number
# - Optional PDFs
```

### Full Test
Use sample cases from `examples/sample_cases/`:
- Syrian family case
- Unaccompanied minor
- Rejected appeal

---

## ⚠️ Important Notes

### This is a PoC

**Ready for:**
- ✅ Testing
- ✅ Demonstration
- ✅ Proof of concept

**Not ready for:**
- ❌ Production deployment
- ❌ Multi-user operation
- ❌ Sensitive data (no encryption)

### For Production
Need to add:
- Authentication
- Access control
- Data encryption
- Cloud storage
- Monitoring
- Backup

---

## 📞 Support

### Getting Help

1. **Setup issues**: Read `START_HERE.md`
2. **Understanding system**: Read `VISUAL_GUIDE.md`
3. **Feature questions**: Read `PORTAL_README.md`
4. **Technical details**: Read `IMPLEMENTATION_SUMMARY.md`

### Common Issues

**"Dependencies missing"**
```bash
pip install -r src/requirements.txt
```

**"API key not found"**
```bash
export OPENAI_API_KEY='sk-...'
```

**"Database not found"**
```bash
# Ensure you're in the right directory
ls src/vector_db_data/
```

---

## 🎓 Learning the System

### For Users
1. Read `START_HERE.md`
2. Run `./run_portal.sh`
3. Create a test case
4. Review generated PDF

### For Developers
1. Read `VISUAL_GUIDE.md`
2. Study `src/portal.py`
3. Examine `backend/case_processor.py`
4. Review `backend/pdf_generator.py`

### For Administrators
1. Read `PORTAL_README.md`
2. Run `check_setup.py`
3. Review configuration files
4. Plan deployment

---

## 🚀 Next Steps

1. **Install & Test**
   ```bash
   pip install -r src/requirements.txt
   export OPENAI_API_KEY='...'
   ./run_portal.sh
   ```

2. **Create Test Case**
   - Use a voice memo for audio
   - Test with sample data
   - Review generated PDF

3. **Customize**
   - Adjust prompts as needed
   - Modify PDF styling
   - Configure settings

4. **Deploy** (when ready)
   - Add authentication
   - Set up cloud hosting
   - Implement security

---

## ✅ Success Checklist

Before first use:
- [ ] Dependencies installed
- [ ] OpenAI API key set
- [ ] Setup checker passes
- [ ] Portal starts successfully
- [ ] Can access at localhost:8501

After first test:
- [ ] Audio transcribed correctly
- [ ] PDF extracted successfully
- [ ] AI questions generated
- [ ] Chat interface works
- [ ] PDF report created
- [ ] Case saved to storage

---

## 🎉 Summary

You have a **complete, working portal** that:

✅ Processes audio in any language  
✅ Manages document uploads  
✅ Provides AI-powered assessment  
✅ Generates comprehensive legal analysis  
✅ Produces professional PDF reports  
✅ Offers complete case management  

**All requirements met. Ready to use!**

---

## 📖 Read Next

👉 **START_HERE.md** - Get the portal running in 5 minutes

---

**Built for UNHCR Pro Bono Legal Assistance**  
*A complete proof-of-concept system*

**Start now:** `./run_portal.sh` 🚀

