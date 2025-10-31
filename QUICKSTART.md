# Quick Start Guide - Refugee Case Analyzer

This guide shows you how to quickly set up and use the Refugee Case Analyzer CLI tool with `uv`.

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Vector Database**: Ensure you have the vector database at `vector_db_data/` in the project root.

## Installation

Install dependencies with uv:

```bash
cd Pro-BOTno
uv pip install langchain_chroma langchain_huggingface langchain-openai sentence-transformers SPARQLWrapper requests
```

## Usage

### 1. Simple Query from Command Line

```bash
uv run python src/refugee_case_analyzer.py "What are the rights of asylum seekers in Switzerland?"
```

### 2. Analyze Case from File

```bash
uv run python src/refugee_case_analyzer.py --file examples/sample_cases/case1_syrian_family.txt
```

### 3. Read from Stdin

```bash
echo "A Syrian refugee seeks asylum in Switzerland..." | \
    uv run python src/refugee_case_analyzer.py
```

### 4. Interactive Mode

```bash
uv run python src/refugee_case_analyzer.py --interactive
# Type or paste case description
# Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done
```

## Options

### Language Options

Query Swiss laws in different languages:

```bash
# German (default)
uv run python src/refugee_case_analyzer.py "Query" --language de

# French
uv run python src/refugee_case_analyzer.py "Query" --language fr

# Italian
uv run python src/refugee_case_analyzer.py "Query" --language it

# Romansh
uv run python src/refugee_case_analyzer.py "Query" --language rm
```

### Performance Options

```bash
# Disable Swiss legislation queries (faster, RAG only)
uv run python src/refugee_case_analyzer.py --no-fedlex "Query"

# Disable XML fetching (faster but less detailed)
uv run python src/refugee_case_analyzer.py --no-xml "Query"

# Quiet mode (no progress messages)
uv run python src/refugee_case_analyzer.py --quiet "Query"

# No metadata in output (just the analysis)
uv run python src/refugee_case_analyzer.py --no-metadata "Query"
```

### Model Selection

```bash
# Use GPT-4o (default)
uv run python src/refugee_case_analyzer.py --model gpt-4o "Query"

# Use GPT-4
uv run python src/refugee_case_analyzer.py --model gpt-4 "Query"

# Use GPT-3.5 Turbo (faster, cheaper)
uv run python src/refugee_case_analyzer.py --model gpt-3.5-turbo "Query"
```

## Testing the Pipeline

Run the comprehensive test suite:

```bash
./test_pipeline.sh
```

This will:
1. Verify uv and API key are configured
2. Install dependencies
3. Run multiple test cases
4. Verify all functionality works

## Example Use Cases

### Syrian Family Seeking Asylum

```bash
uv run python src/refugee_case_analyzer.py --file examples/sample_cases/case1_syrian_family.txt
```

### Unaccompanied Minor

```bash
uv run python src/refugee_case_analyzer.py --file examples/sample_cases/case2_unaccompanied_minor.txt
```

### Appeal Case

```bash
uv run python src/refugee_case_analyzer.py --file examples/sample_cases/case3_rejected_appeal.txt
```

### Quick Question

```bash
uv run python src/refugee_case_analyzer.py \
    "Can asylum seekers work in Switzerland during their application process?"
```

## Output Format

The tool outputs a comprehensive analysis with:

1. **Legal Analysis**: Detailed legal advice with citations
2. **Metadata** (optional):
   - Data sources used (Fedlex, RAG, or both)
   - Routing decision
   - Referenced documents
   - Swiss legislation details

### Example Output Structure

```
================================================================================
REFUGEE CASE LEGAL ANALYSIS
================================================================================

LEGAL ANALYSIS:
--------------------------------------------------------------------------------
[Comprehensive legal analysis with exact citations from Swiss laws and 
international legal documents]

================================================================================
METADATA
================================================================================

Data Source: BOTH
Route Decision: BOTH
✓ Swiss Federal Legislation (Fedlex) included
✓ General Legal Documents included

REFERENCED DOCUMENTS:
--------------------------------------------------------------------------------
1. /path/to/document1.pdf
2. /path/to/document2.pdf

SWISS LEGISLATION DETAILS:
--------------------------------------------------------------------------------
[Detailed Swiss law information including SR numbers, XML content, etc.]

================================================================================
END OF ANALYSIS
================================================================================
```

## Troubleshooting

### "No module named langchain_chroma"

Install dependencies:
```bash
uv pip install langchain_chroma langchain_huggingface langchain-openai sentence-transformers SPARQLWrapper requests
```

### "Vector database not found"

Ensure `vector_db_data/` exists in the project root. If not, specify custom path:
```bash
uv run python src/refugee_case_analyzer.py --db-folder /path/to/db "Query"
```

### "OpenAI API key not found"

Set the environment variable:
```bash
export OPENAI_API_KEY="your-key"
```

### Slow performance

Try these options:
```bash
# Disable XML fetching
uv run python src/refugee_case_analyzer.py --no-xml "Query"

# Use only RAG (no Fedlex)
uv run python src/refugee_case_analyzer.py --no-fedlex "Query"

# Use faster model
uv run python src/refugee_case_analyzer.py --model gpt-3.5-turbo "Query"
```

## Advanced Usage

### Batch Processing

Process multiple cases:

```bash
for case_file in examples/sample_cases/*.txt; do
    echo "Processing: $case_file"
    uv run python src/refugee_case_analyzer.py --file "$case_file" --no-metadata > "output_$(basename $case_file)"
done
```

### Pipe to File

Save analysis to file:

```bash
uv run python src/refugee_case_analyzer.py "Query" > analysis.txt
```

### Combined with grep/search

Extract specific information:

```bash
uv run python src/refugee_case_analyzer.py "Query" | grep -A 5 "Article"
```

## Getting Help

```bash
uv run python src/refugee_case_analyzer.py --help
```

For detailed documentation, see:
- [Full Documentation](docs/FEDLEX_MODULE.md)
- [README](README.md)

