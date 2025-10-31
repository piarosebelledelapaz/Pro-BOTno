#!/bin/bash
# Test pipeline for refugee case analyzer using uv

set -e  # Exit on error

echo "=================================="
echo "Testing Refugee Case Analyzer"
echo "Using uv for dependency management"
echo "=================================="
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    echo "   Please set it with: export OPENAI_API_KEY='your-key'"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv is installed"
echo "✓ OPENAI_API_KEY is set"
echo ""

# Install dependencies
echo "📦 Installing dependencies with uv..."
cd "$(dirname "$0")"
uv pip install -q langchain_chroma langchain_huggingface langchain-openai sentence-transformers SPARQLWrapper requests 2>&1 | grep -v "^Requirement already satisfied" || true
echo "✓ Dependencies installed"
echo ""

# Test 1: Help command
echo "Test 1: Display help"
echo "===================="
uv run python src/refugee_case_analyzer.py --help
echo ""
echo "✓ Help command works"
echo ""

# Test 2: Simple query from command line
echo "Test 2: Simple Swiss law query"
echo "==============================="
echo "Query: 'What are the basic rights of asylum seekers in Switzerland?'"
echo ""
uv run python src/refugee_case_analyzer.py \
    --no-metadata \
    --quiet \
    "What are the basic rights of asylum seekers in Switzerland regarding housing and work?"
echo ""
echo "✓ Simple query works"
echo ""

# Test 3: Case from file
if [ -f "examples/sample_cases/case1_syrian_family.txt" ]; then
    echo "Test 3: Analyze Syrian family case from file"
    echo "============================================="
    uv run python src/refugee_case_analyzer.py \
        --file examples/sample_cases/case1_syrian_family.txt \
        --no-metadata \
        --quiet
    echo ""
    echo "✓ File input works"
    echo ""
fi

# Test 4: RAG-only mode (no Fedlex - faster)
echo "Test 4: RAG-only mode (international law)"
echo "=========================================="
echo "Query: 'What does the Geneva Convention say about refugee children?'"
echo ""
uv run python src/refugee_case_analyzer.py \
    --no-fedlex \
    --no-metadata \
    --quiet \
    "What does the Geneva Convention say about refugee children?"
echo ""
echo "✓ RAG-only mode works"
echo ""

# Test 5: Stdin input
echo "Test 5: Input from stdin"
echo "========================"
echo "A refugee from Ukraine seeks temporary protection in Switzerland." | \
    uv run python src/refugee_case_analyzer.py \
        --no-metadata \
        --quiet
echo ""
echo "✓ Stdin input works"
echo ""

echo "=================================="
echo "✓ All tests passed!"
echo "=================================="
echo ""
echo "The pipeline is working correctly with uv."
echo ""
echo "Usage examples:"
echo "  # Simple query"
echo "  uv run python src/refugee_case_analyzer.py 'Your question here'"
echo ""
echo "  # From file"
echo "  uv run python src/refugee_case_analyzer.py --file case.txt"
echo ""
echo "  # With French Swiss laws"
echo "  uv run python src/refugee_case_analyzer.py --language fr 'Question'"
echo ""

