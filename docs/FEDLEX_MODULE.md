# Fedlex SPARQL Module Documentation

## Overview

The Fedlex SPARQL module integrates Swiss federal legislation from the [Fedlex database](https://www.fedlex.admin.ch/) into the UNHCR Pro Bono Legal Assistant. This module enables the LLM to:

1. **Intelligently route queries** between general legal documents and Swiss legislation
2. **Generate SPARQL queries** automatically using natural language
3. **Fetch full XML legal texts** with exact article citations
4. **Provide precise legal analysis** based on actual Swiss law provisions

## Architecture

### Module Structure

```
src/
├── prompts/
│   ├── __init__.py
│   └── fedlex_prompts.py          # All prompts for SPARQL and legal analysis
├── modules/
│   ├── __init__.py
│   ├── fedlex_client.py           # SPARQL client and helper functions
│   └── enhanced_rag.py            # Combined RAG chain with routing
└── app.py                          # Updated Streamlit application
```

### Key Components

#### 1. Prompts (`prompts/fedlex_prompts.py`)

Contains refined, specialized prompts:

- **SPARQL_GENERATION_PROMPT**: Generates SPARQL queries from natural language
- **ROUTER_PROMPT**: Decides which data source(s) to use
- **RAG_PROMPT**: Analyzes general legal documents
- **SPARQL_INTERPRETATION_PROMPT**: Interprets Swiss legislation results
- **COMBINED_PROMPT**: Synthesizes both data sources

#### 2. Fedlex Client (`modules/fedlex_client.py`)

Core functionality:

```python
class FedlexSPARQLClient:
    def generate_sparql_query(question: str) -> str
        # Uses LLM to generate SPARQL from natural language
    
    def execute_query(sparql_query: str) -> Dict
        # Executes SPARQL against Fedlex endpoint
    
    def query_with_llm(question: str) -> Dict
        # End-to-end: generate + execute
    
    def fetch_xml_document(consolidation_uri: str, language: str) -> Dict
        # Fetches full legal text in XML format
```

Helper functions:

- `is_law_applicable()`: Check if a law is currently in force
- `construct_document_urls()`: Generate links to all language versions
- `format_sparql_results()`: Format results with XML content for LLM analysis

#### 3. Enhanced RAG (`modules/enhanced_rag.py`)

Orchestrates the complete workflow:

```python
def build_enhanced_rag_chain(
    vector_db,
    api_key,
    k=4,
    model="gpt-5",
    fetch_xml=True,
    xml_language='de',
    enable_fedlex=True
)
```

**Routing Logic:**

1. **FEDLEX**: Questions specifically about Swiss law → Query only Fedlex
2. **RAG**: General/international legal questions → Query only document database
3. **BOTH**: Comparative or comprehensive questions → Query both sources

## How It Works

### Query Flow

```
User Question
    ↓
[ROUTER] Analyze question
    ↓
    ├─→ FEDLEX
    │   ├─→ Generate SPARQL query (LLM)
    │   ├─→ Execute against Fedlex
    │   ├─→ Filter for applicable laws
    │   ├─→ Fetch XML for each law
    │   └─→ Interpret results with exact citations
    │
    ├─→ RAG
    │   ├─→ Retrieve relevant documents
    │   └─→ Analyze with general legal framework
    │
    └─→ BOTH
        ├─→ Execute both FEDLEX and RAG
        └─→ Synthesize comprehensive answer
```

### Example Workflow

**Question:** "What are the rights of unaccompanied minors seeking asylum in Switzerland?"

1. **Router Decision**: BOTH (Swiss law + international context)

2. **RAG Query**: Retrieves European and international documents about unaccompanied minors

3. **Fedlex Query**:
   - LLM generates SPARQL:
     ```sparql
     SELECT DISTINCT ?work ?consolidation ?title ?sr_number ?date 
                     ?dateApplicability ?dateEndApplicability 
     WHERE {
         ?work a jolux:ConsolidationAbstract ;
               jolux:dateDocument ?date ;
               jolux:isRealizedBy ?expression .
         
         ?consolidation jolux:isMemberOf ?work ;
                        jolux:dateApplicability ?dateApplicability .
         
         ?expression jolux:language <http://publications.europa.eu/resource/authority/language/DEU> ;
                     jolux:title ?title .
         
         FILTER(
             CONTAINS(LCASE(?title), "asyl") ||
             CONTAINS(LCASE(?title), "minderjährig")
         )
     }
     ORDER BY DESC(?date)
     LIMIT 10
     ```
   
   - Executes query against Fedlex
   - Filters for currently applicable laws
   - Fetches XML for each relevant law (e.g., Asylgesetz SR 142.31)

4. **LLM Analysis**:
   - Receives FULL XML content of Swiss laws
   - Extracts exact article citations
   - Provides precise legal analysis with quotes

5. **Response**: Comprehensive answer citing:
   - Specific articles from Swiss Asylgesetz
   - European directives on unaccompanied minors
   - Practical guidance for the case

## XML Citation System

### Why XML?

The XML format contains the **complete legal text** with structured article/section markers, enabling:

1. **Exact citations**: LLM can quote specific articles verbatim
2. **Verification**: Lawyers can verify citations against official sources
3. **Precision**: No hallucination or approximation of legal text
4. **Multilingual**: Support for German, French, Italian, and Romansh

### Example XML Structure

```xml
<act>
  <body>
    <article id="art_1">
      <title>Art. 1 Gegenstand</title>
      <paragraph>
        <text>Dieses Gesetz regelt...</text>
      </paragraph>
    </article>
    <article id="art_2">
      <title>Art. 2 Definitionen</title>
      ...
    </article>
  </body>
</act>
```

### LLM Prompt Guidance

The prompts explicitly instruct the LLM to:

```
CITATION REQUIREMENTS FOR XML CONTENT:
- When XML content is provided, extract and cite EXACT provisions
- Reference specific article numbers, paragraphs, and sections
- Quote relevant text passages verbatim
- Format: "According to Article X of [Law Title, SR Number]: '[exact quote]'"
- Note the language version used
```

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
```

### App Configuration (`app.py`)

```python
# Model Configuration
LLM_MODEL = "gpt-4"

# Fedlex Configuration
ENABLE_FEDLEX = True    # Enable/disable Swiss legislation queries
FETCH_XML = True        # Fetch full XML legal texts
XML_LANGUAGE = 'de'     # Language: 'de', 'fr', 'it', 'rm'
```

### Customization Options

**Disable Fedlex** (RAG-only mode):
```python
ENABLE_FEDLEX = False
```

**Disable XML Fetching** (faster but less detailed):
```python
FETCH_XML = False  # Only metadata, no full text
```

**Change Language**:
```python
XML_LANGUAGE = 'fr'  # French
XML_LANGUAGE = 'it'  # Italian
XML_LANGUAGE = 'rm'  # Romansh
```

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key"

# Run Streamlit app
cd src
streamlit run app.py
```

### API Usage (Programmatic)

```python
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from modules.enhanced_rag import build_enhanced_rag_chain

# Load vector database
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
vector_db = Chroma(
    persist_directory="vector_db_data",
    embedding_function=embeddings
)

# Build chain
chain = build_enhanced_rag_chain(
    vector_db=vector_db,
    api_key="your-openai-key",
    k=4,
    model="gpt-4",
    fetch_xml=True,
    xml_language='de',
    enable_fedlex=True
)

# Query
response = chain("What Swiss laws protect refugee children?")

print(response["answer"])
print(f"Source: {response['source']}")
print(f"Route: {response['route_decision']}")
```

## Prompt Engineering

### Key Refinements Made

1. **SPARQL Generation**:
   - Detailed schema documentation
   - Multiple concrete examples
   - Explicit rules for query structure
   - Language filtering instructions

2. **Routing**:
   - Clear decision guidelines
   - Jurisdiction-aware routing
   - Support for hybrid queries

3. **Legal Analysis**:
   - Structured analysis framework (Rights, Complications, Solutions, Procedures)
   - Mandatory citation requirements
   - XML-specific citation instructions
   - Professional lawyer-to-lawyer tone

4. **Combined Analysis**:
   - Clear separation of sources
   - Integration guidance
   - Conflict identification

### Customizing Prompts

All prompts are in `src/prompts/fedlex_prompts.py` and can be easily modified:

```python
# Example: Add emphasis on specific legal aspects
RAG_PROMPT = ChatPromptTemplate.from_template("""
...existing prompt...

ADDITIONAL FOCUS:
- Always check for procedural deadlines
- Identify any financial support available
- Note any recent legal changes

...rest of prompt...
""")
```

## Performance Considerations

### Speed vs. Completeness

| Configuration | Speed | Detail | Use Case |
|--------------|-------|--------|----------|
| `FETCH_XML=False` | Fast | Metadata only | Quick overview |
| `FETCH_XML=True` | Slower | Full citations | Detailed legal analysis |

### Token Usage

- **Without XML**: ~2,000-5,000 tokens per query
- **With XML**: ~10,000-50,000 tokens per query (depending on law size)

### Caching

The Streamlit app uses `@st.cache_resource` to cache:
- Embedding model loading
- Vector database loading
- Chain building

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/Pro-BOTno/src"
```

**SPARQL Query Errors:**
- Check Fedlex endpoint availability
- Verify LLM is generating valid SPARQL
- Review generated query in console output

**XML Fetching Failures:**
- Some laws may not have XML versions
- Try different language (`xml_language='de'` → `'fr'`)
- Check consolidation URI validity

**Routing Issues:**
- Review ROUTER_PROMPT decision logic
- Add more specific keywords for Swiss law detection
- Check console output for route decisions

## Testing

### Test Questions

**Swiss-specific (should route to FEDLEX):**
- "What are the requirements for asylum in Switzerland?"
- "Find Swiss laws about family reunification for refugees"
- "What is the Asylgesetz?"

**General (should route to RAG):**
- "What are international refugee rights under the Geneva Convention?"
- "How does European law protect unaccompanied minors?"

**Comprehensive (should route to BOTH):**
- "How does Swiss asylum law compare to international standards?"
- "What rights do refugee children have in Switzerland under both Swiss and international law?"

### Validation

1. Check routing decisions in console output
2. Verify XML content is fetched (look for XML blocks)
3. Confirm citations include exact article references
4. Validate links to official Fedlex documents

## Future Enhancements

Possible improvements:

1. **Caching**: Cache SPARQL results and XML content
2. **Multilingual**: Generate queries in all Swiss languages simultaneously
3. **Timeline**: Show evolution of laws over time
4. **PDF Support**: Fetch and parse PDF versions
5. **Cross-references**: Follow references between laws
6. **Semantic Search**: Use embeddings for better law matching
7. **Citation Extraction**: Automatically extract and highlight citations in response

## Resources

- [Fedlex Official Site](https://www.fedlex.admin.ch/)
- [Fedlex SPARQL Endpoint](https://fedlex.data.admin.ch/sparqlendpoint)
- [JOLux Ontology Documentation](http://data.legilux.public.lu/resource/ontology/jolux)
- [Swiss Legislation SR Numbers](https://www.admin.ch/opc/en/classified-compilation/national.html)

## Support

For issues or questions:
1. Check console output for detailed logging
2. Review generated SPARQL queries
3. Verify XML content is being fetched
4. Test with simpler queries first

## License

Same as parent project (see LICENSE file).

