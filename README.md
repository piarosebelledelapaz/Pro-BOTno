# ⚖️ Pro-BOTno: An AI-powered UNHCR Pro-bono Legal Assistant for Refugees

An intelligent legal assistant for pro bono lawyers at UNHCR working with refugees. The system combines:
- **General Legal Documents**: European and international legal documents via RAG (Retrieval-Augmented Generation)
- **Swiss Federal Legislation**: Official Swiss laws from Fedlex with exact legal citations via SPARQL

This project idea is made for the hackathon from the "Seminar: Digital  Platforms for Resilience Crisis" FS2025.
We are Team 4 (Cache me if you can) and the members are the following:
- Pia Rosebelle M. dela Paz
- Yunyi Zhang
- Solomon Haile Dereje


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation with uv (Recommended)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd Pro-BOTno

# Install dependencies with uv
uv pip install langchain_chroma langchain_huggingface langchain-openai \
    sentence-transformers SPARQLWrapper requests streamlit

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### CLI Tool (Standalone)

Analyze refugee cases from command line:

```bash
# Simple query
uv run python src/refugee_case_analyzer.py "What are asylum seekers' rights in Switzerland?"

# Analyze from file
uv run python src/refugee_case_analyzer.py --file case.txt

# Run test pipeline
./test_pipeline.sh
```

See [QUICKSTART.md](QUICKSTART.md) for detailed CLI usage.

#### Web Interface (Streamlit)

```bash
cd src
streamlit run app.py
```

## ✨ Features

### Intelligent Routing
The system automatically determines whether to query:
- **Swiss Federal Legislation** (Fedlex) for Swiss law questions
- **General Documents** (RAG) for international/European law
- **Both** for comprehensive or comparative questions

### Exact Legal Citations
- Fetches **full XML legal texts** from Swiss federal legislation
- Provides **exact article citations** with verbatim quotes
- Links to official documents in all Swiss languages (German, French, Italian, Romansh)

### Comprehensive Analysis
- Identifies immediate rights for refugees
- Highlights potential complications
- Suggests legal solutions and pathways
- Notes procedural requirements and timelines

## 🏗️ Architecture

```
src/
├── app.py                    # Streamlit web application
├── prompts/
│   └── fedlex_prompts.py    # All prompts for legal analysis
├── modules/
│   ├── fedlex_client.py     # Swiss legislation SPARQL client
│   └── enhanced_rag.py      # Combined RAG chain with routing
└── requirements.txt
```

### Key Technologies

- **LangChain**: Orchestration and RAG pipeline
- **OpenAI GPT-4**: Legal analysis and SPARQL generation
- **ChromaDB**: Vector database for document retrieval
- **SPARQLWrapper**: Swiss Fedlex database queries
- **Streamlit**: Web interface
- **HuggingFace**: Multilingual embeddings

## 📖 Usage

### CLI Tool (Primary Interface)

The standalone CLI tool analyzes refugee cases and outputs legal analysis to stdout:

```bash
# Basic usage (using wrapper script)
./analyze "What are asylum seekers' rights in Switzerland?"

# Or use uv run directly
uv run python src/refugee_case_analyzer.py "Case description or legal question"

# From file (analyze sample cases)
./analyze --file examples/sample_cases/case1_syrian_family.txt

# Interactive mode (multi-line input)
./analyze --interactive

# Pipe from stdin
echo "Case details..." | ./analyze

# With options (French laws, no metadata, quiet mode)
./analyze --language fr --no-metadata --quiet "Legal question"

# Test the pipeline
./test_pipeline.sh
```

**Key Features:**
- 📥 **Input**: Command line, file, stdin, or interactive mode
- 📤 **Output**: Structured legal analysis with citations to stdout
- 🇨🇭 **Swiss Laws**: Full XML legal texts with exact article citations
- 🌍 **International**: RAG database with European/international law
- 🔀 **Intelligent Routing**: Auto-detects best data source
- ⚡ **Fallback**: Switches to RAG if no Swiss laws found
- 🌐 **Multilingual**: DE, FR, IT, RM Swiss law support

**See [QUICKSTART.md](QUICKSTART.md) for complete CLI documentation.**

### Web Interface (Alternative)

1. Launch the app: `cd src && streamlit run app.py`
2. Enter your legal question
3. Review the comprehensive analysis with citations
4. Check the sources and Swiss legislation details

### Example Questions

**Swiss Law Questions:**
- "What are the requirements for asylum in Switzerland?"
- "What Swiss laws protect unaccompanied refugee minors?"
- "Find legislation about family reunification in Switzerland"

**International Law Questions:**
- "What are refugee rights under the Geneva Convention?"
- "How does European law protect asylum seekers?"

**Comparative Questions:**
- "How does Swiss asylum law compare to international standards?"
- "What rights do refugee children have under both Swiss and international law?"

## ⚙️ Configuration

Edit `src/app.py` to customize:

```python
# Model Configuration
LLM_MODEL = "gpt-4"              # OpenAI model to use

# Fedlex Configuration
ENABLE_FEDLEX = True             # Enable Swiss legislation queries
FETCH_XML = True                 # Fetch full legal texts (slower but detailed)
XML_LANGUAGE = 'de'              # 'de', 'fr', 'it', or 'rm'
```

## 📚 Documentation

- **[Fedlex Module Documentation](docs/FEDLEX_MODULE.md)**: Comprehensive guide to the Swiss legislation integration
- **[Test Script](examples/test_fedlex.py)**: Command-line testing without Streamlit

## 🔧 Development

### Project Structure

```
Pro-BOTno/
├── src/
│   ├── app.py                      # Main Streamlit application
│   ├── requirements.txt            # Python dependencies
│   ├── prompts/
│   │   └── fedlex_prompts.py      # Legal analysis prompts
│   └── modules/
│       ├── fedlex_client.py       # Fedlex SPARQL client
│       └── enhanced_rag.py        # Enhanced RAG chain
├── docs/
│   └── FEDLEX_MODULE.md           # Detailed module documentation
├── examples/
│   └── test_fedlex.py             # Testing script
└── README.md
```

### Running Tests

```bash
cd examples
python test_fedlex.py
```

## 🌍 Swiss Legislation Integration

### How It Works

1. **LLM generates SPARQL queries** from natural language questions
2. **Queries Fedlex database** for relevant Swiss laws
3. **Filters for applicable laws** (checks if currently in force)
4. **Fetches full XML legal texts** with complete articles
5. **LLM analyzes XML** to extract exact citations and provisions

### Example Output

For the question "What Swiss laws protect asylum seekers?":

```
According to Article 3 of the Swiss Asylum Act (SR 142.31):
"Switzerland shall grant asylum to refugees in accordance with 
the provisions of this Act."

[Links to official documents in DE, FR, IT, RM]
[Full XML legal text provided for verification]
```

## 🎯 Hackathon Challenge

**Challenge**: Provide precise legal assistance to pro bono lawyers helping refugees

**Solution**: 
- Combines international legal knowledge with Swiss-specific legislation
- Provides verifiable citations from official sources
- Enables quick legal research across multiple jurisdictions
- Supports all Swiss national languages

## 👥 Team Members

[Add your team members here]

## 🛠️ Tech Stack

- **Backend**: Python, LangChain
- **LLM**: OpenAI GPT-4
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace (paraphrase-multilingual-mpnet-base-v2)
- **SPARQL**: SPARQLWrapper
- **Frontend**: Streamlit
- **Data Sources**: 
  - Swiss Fedlex database (SPARQL endpoint)
  - European legal document corpus (vector database)

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- [Fedlex](https://www.fedlex.admin.ch/) - Swiss Federal Legislation
- UNHCR - United Nations High Commissioner for Refugees
- OpenAI - GPT-4 language model

---

**For detailed technical documentation, see [docs/FEDLEX_MODULE.md](docs/FEDLEX_MODULE.md)**
