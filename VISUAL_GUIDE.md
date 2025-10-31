# 📊 Visual Guide - UNHCR Refugee Portal

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNHCR REFUGEE PORTAL                         │
│                  Web Interface (Streamlit)                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
    ┌───────▼────────┐             ┌───────▼────────┐
    │  CASE INTAKE   │             │  CASE REPORTS  │
    │  Upload Files  │             │  View & Manage │
    │  Interactive   │             │  Download PDFs │
    └───────┬────────┘             └────────────────┘
            │
            ▼
    ┌─────────────────┐
    │ AUDIO PROCESSING│
    │  Whisper API    │
    │  Transcribe     │
    │  Translate      │
    └───────┬─────────┘
            │
            ▼
    ┌─────────────────┐
    │  BACKEND        │
    │  case_processor │
    │  Legal Analysis │
    └───────┬─────────┘
            │
            ▼
    ┌─────────────────┐
    │  PDF REPORT     │
    │  pdf_generator  │
    │  With Appendices│
    └─────────────────┘
```

---

## 📁 File Structure Map

```
Pro-BOTno/
│
├── 📄 START_HERE.md           ⭐ READ THIS FIRST
├── 📄 PROJECT_COMPLETE.md     ⭐ Project summary
├── 📄 PORTAL_README.md         📚 Full documentation
├── 📄 IMPLEMENTATION_SUMMARY.md 🔧 Technical details
│
├── 🔧 run_portal.sh           🚀 Start the portal
├── 🔍 check_setup.py          ✅ Verify installation
│
└── src/
    │
    ├── 🏠 portal.py            🌟 MAIN ENTRY POINT
    │
    ├── pages/
    │   ├── 1_📝_New_Case_Intake.py   ⬆️ Upload & process
    │   └── 2_📊_Case_Reports.py      📋 View cases
    │
    ├── backend/                🔒 NEW BACKEND
    │   ├── case_processor.py   ⚖️ Legal analysis engine
    │   └── pdf_generator.py    📄 PDF generation
    │
    ├── modules/                🔌 EXISTING (integrated)
    │   ├── enhanced_rag.py     🔍 RAG + Fedlex
    │   └── fedlex_client.py    🇨🇭 Swiss legislation
    │
    ├── prompts/                💬 EXISTING (reused)
    │   └── fedlex_prompts.py   📝 Legal prompts
    │
    ├── vector_db_data/         📚 EXISTING (reused)
    │   └── chroma.sqlite3      💾 Legal documents DB
    │
    └── cases/                  📁 GENERATED (at runtime)
        └── {UNHCR_NUMBER}/
            ├── audio/
            ├── transcripts/
            ├── forms/
            └── reports/
```

---

## 🔄 User Workflow

```
START
  │
  ▼
┌──────────────────────┐
│  1. OPEN PORTAL      │
│  ./run_portal.sh     │
│  http://localhost... │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  2. UPLOAD FILES     │
│  • Audio (any lang)  │
│  • PDF forms         │
│  • UNHCR number      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  3. AUTO PROCESS     │
│  ⏱️ 1-2 min          │
│  ✓ Transcribe        │
│  ✓ Translate         │
│  ✓ Extract PDFs      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  4. REVIEW RESULTS   │
│  📝 Original text    │
│  🌍 English trans    │
│  📋 Form data        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  5. AI QUESTIONS     │
│  🤖 Auto-generated   │
│  💬 Chat interface   │
│  📝 Gather info      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  6. LEGAL ANALYSIS   │
│  ⏱️ 2-5 min          │
│  🔍 RAG search       │
│  🇨🇭 Fedlex query    │
│  📚 Bibliography     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  7. PDF GENERATED    │
│  📥 Download         │
│  ✓ Full report       │
│  ✓ Appendices        │
│  ✓ Bibliography      │
└──────────┬───────────┘
           │
           ▼
          END
```

---

## 🎨 Portal Pages

### Page 1: Landing Page (`portal.py`)
```
╔════════════════════════════════════════════════╗
║     🛡️ UNHCR REFUGEE ASSISTANCE PORTAL         ║
╚════════════════════════════════════════════════╝

┌────────────────────────────────────────────────┐
│  Features                                      │
│  • 🎤 Audio processing                         │
│  • 💬 AI assessment                            │
│  • ⚖️ Legal analysis                           │
│  • 📄 PDF reports                              │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  System Status                                 │
│  ✅ OpenAI API    ✅ Database    📁 Cases      │
└────────────────────────────────────────────────┘
```

### Page 2: Case Intake (`pages/1_📝_New_Case_Intake.py`)
```
╔════════════════════════════════════════════════╗
║            📝 NEW CASE INTAKE                   ║
╚════════════════════════════════════════════════╝

Progress: 1️⃣ Upload  →  2️⃣ Transcribe  →  3️⃣ Assess  →  4️⃣ Complete

┌────────────────────────────────────────────────┐
│  Basic Information                             │
│  Name: ___________________________________     │
│  UNHCR Number: ___________________________     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Interview Audio                               │
│  [📎 Upload Audio File]                        │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Supporting Documents                          │
│  [📎 Upload PDF Forms (multiple)]              │
└────────────────────────────────────────────────┘

                [Process Files →]
```

### Page 3: Case Reports (`pages/2_📊_Case_Reports.py`)
```
╔════════════════════════════════════════════════╗
║            📊 CASE REPORTS                      ║
╚════════════════════════════════════════════════╝

🔍 Search: _______________  Sort: [Newest First ▼]

┌────────────────────────────────────────────────┐
│  Ahmad Al-Rashid          UNHCR-2024-001       │
│  Created: Oct 31, 2025                         │
│                           [📥 Download PDF]    │
│                                                │
│  📋 View Details                               │
│    ✓ Audio  ✓ Transcript  ✓ Forms  ✓ Report  │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│  Maria Santos            UNHCR-2024-002        │
│  Created: Oct 30, 2025                         │
│                           [📥 Download PDF]    │
└────────────────────────────────────────────────┘
```

---

## 📄 PDF Report Structure

```
┌─────────────────────────────────────────┐
│  REFUGEE CASE LEGAL ANALYSIS            │
│                                         │
│  Asylum Seeker: Ahmad Al-Rashid         │
│  UNHCR Number: UNHCR-2024-001           │
│  Date: October 31, 2025                 │
│                                         │
│  CONFIDENTIAL LEGAL DOCUMENT            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  EXECUTIVE SUMMARY                      │
│  • Personal Data                        │
│  • Overview of Situation                │
│  • Family Composition                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  LEGAL ANALYSIS                         │
│  • Legally Relevant Facts               │
│    (see Appendix I, Appendix II)        │
│  • Applicable Law                       │
│  • Legal Assessment                     │
│  • Recommendations                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  BIBLIOGRAPHY                           │
│  General Legal Documents                │
│  [1] European Convention...             │
│  [2] Geneva Convention...               │
│                                         │
│  Swiss Federal Legislation              │
│  [L1] Asylgesetz (SR 142.31)           │
│  [L2] Ausländer (SR 142.20)            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  APPENDIX I: ASYLUM SEEKER FORMS        │
│  • Original Files (2 documents)         │
│  • Extracted Content                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  APPENDIX II: INTERVIEW TRANSCRIPT      │
│  • Original Language                    │
│  • English Translation                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  APPENDIX III: RELEVANT CASE LAW        │
│  • Case Law Summary                     │
│  • Referenced Documents                 │
│  • Legal Sources                        │
└─────────────────────────────────────────┘
```

---

## 🔧 Backend Architecture

```
┌─────────────────────────────────────────────────┐
│              CaseProcessor                      │
│       (backend/case_processor.py)               │
├─────────────────────────────────────────────────┤
│                                                 │
│  Main Methods:                                  │
│  • process_case()                               │
│    └─ Comprehensive legal analysis              │
│                                                 │
│  • ask_follow_up_questions()                    │
│    └─ Generate AI questions                     │
│                                                 │
│  • _extract_bibliography()                      │
│    └─ Parse sources & legislation               │
│                                                 │
│  • _generate_legal_summary()                    │
│    └─ Structure with appendix refs              │
│                                                 │
│  • _extract_case_law_summary()                  │
│    └─ Extract relevant precedents               │
│                                                 │
├─────────────────────────────────────────────────┤
│  Uses:                                          │
│  • ChromaDB (existing)                          │
│  • Fedlex Client (existing)                     │
│  • Enhanced RAG (existing)                      │
│  • GPT-4 (for analysis)                         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│           PDFReportGenerator                    │
│        (backend/pdf_generator.py)               │
├─────────────────────────────────────────────────┤
│                                                 │
│  Main Methods:                                  │
│  • generate_report()                            │
│    └─ Create complete PDF                       │
│                                                 │
│  • _build_title_page()                          │
│  • _build_executive_summary()                   │
│  • _build_legal_analysis()                      │
│  • _build_bibliography()                        │
│  • _build_appendix_forms()                      │
│  • _build_appendix_transcript()                 │
│  • _build_appendix_case_law()                   │
│                                                 │
├─────────────────────────────────────────────────┤
│  Uses:                                          │
│  • ReportLab (PDF generation)                   │
│  • Professional styling                         │
│  • Structured sections                          │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Integration Points

```
NEW CODE ─────────────┐
                      │
┌─────────────────────▼──────────────────────┐
│  Streamlit Portal (NEW)                    │
│  • portal.py                               │
│  • pages/1_📝_New_Case_Intake.py           │
│  • pages/2_📊_Case_Reports.py              │
└─────────────────────┬──────────────────────┘
                      │
                      │ Uses
                      │
┌─────────────────────▼──────────────────────┐
│  Backend Services (NEW)                    │
│  • case_processor.py                       │
│  • pdf_generator.py                        │
└─────────────────────┬──────────────────────┘
                      │
                      │ Calls
                      │
┌─────────────────────▼──────────────────────┐
│  Existing Modules (REUSED)                 │
│  • enhanced_rag.py                         │
│  • fedlex_client.py                        │
│  • fedlex_prompts.py                       │
└─────────────────────┬──────────────────────┘
                      │
                      │ Queries
                      │
┌─────────────────────▼──────────────────────┐
│  Data Sources (EXISTING)                   │
│  • ChromaDB (vector_db_data/)              │
│  • Fedlex SPARQL (API)                     │
└────────────────────────────────────────────┘
                      ▲
                      │
EXISTING CODE ────────┘
```

---

## 🚀 Quick Start Commands

```bash
# 1. Check if everything is ready
python3 check_setup.py

# Expected output:
# ✓ Python version OK
# ✓ All dependencies installed
# ✓ API key set
# ✓ Database found
# ✓ All files present

# 2. Start the portal
./run_portal.sh

# Or manually:
cd src && streamlit run portal.py

# 3. Open browser
# http://localhost:8501
```

---

## 💡 Key Concepts

### Audio Processing
```
Audio File (any language)
    │
    ▼
[Whisper API]
    │
    ├──▶ Transcription (original language)
    │
    └──▶ Translation (English)
    
Both saved for reference
```

### Legal Analysis
```
Case Description
    │
    ▼
[Case Processor]
    │
    ├──▶ ChromaDB Query (international law)
    │
    ├──▶ Fedlex Query (Swiss law)
    │
    ├──▶ GPT-4 Analysis
    │
    └──▶ Bibliography Generation
    
Structured output with references
```

### PDF Generation
```
Analysis Results
    │
    ▼
[PDF Generator]
    │
    ├──▶ Title Page
    ├──▶ Executive Summary
    ├──▶ Legal Analysis (with refs)
    ├──▶ Bibliography
    ├──▶ Appendix I (Forms)
    ├──▶ Appendix II (Transcript)
    └──▶ Appendix III (Case Law)
    
Professional PDF with all sections
```

---

## 📊 Comparison Chart

| Aspect | Before | After |
|--------|--------|-------|
| **Interface** | Terminal | Web Portal |
| **Input** | Text only | Audio + PDFs |
| **Audio** | Manual transcription | Automatic (Whisper) |
| **Translation** | Manual | Automatic |
| **Assessment** | None | AI questions + chat |
| **Output** | Text file | Professional PDF |
| **Bibliography** | No | Yes, with citations |
| **Appendices** | No | Yes, 3 appendices |
| **Storage** | No | Organized file system |
| **Management** | No | Search, view, download |

---

## 🎯 What Each File Does

```
portal.py
└─▶ Landing page, system overview, navigation

pages/1_📝_New_Case_Intake.py
└─▶ 4-step workflow: Upload → Transcribe → Assess → Complete

pages/2_📊_Case_Reports.py
└─▶ View all cases, search, download reports

backend/case_processor.py
└─▶ Legal analysis, bibliography, questions, summaries

backend/pdf_generator.py
└─▶ Create professional PDFs with all sections

run_portal.sh
└─▶ Start the portal (checks API key, runs Streamlit)

check_setup.py
└─▶ Verify installation (Python, deps, API key, DB)
```

---

## 🎓 Learning Path

```
1. Start Here
   └─▶ READ: START_HERE.md
   
2. Run It
   └─▶ RUN: ./run_portal.sh
   
3. Test It
   └─▶ CREATE: A test case
   
4. Understand It
   └─▶ READ: portal.py
   └─▶ READ: pages/1_📝_New_Case_Intake.py
   └─▶ READ: backend/case_processor.py
   
5. Customize It
   └─▶ MODIFY: Prompts, styling, settings
   
6. Deploy It
   └─▶ READ: PORTAL_README.md (deployment section)
```

---

## ✨ Summary

This visual guide shows:
- 🏗️ System architecture
- 📁 File organization
- 🔄 User workflows
- 🎨 Page layouts
- 📄 PDF structure
- 🔧 Backend design
- 🔌 Integration points
- 🚀 Quick commands

**Everything connected and working together!**

---

**Ready to use? Run:** `./run_portal.sh` 🚀

