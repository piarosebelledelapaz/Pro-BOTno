#!/bin/bash
# Run the UNHCR Refugee Assistance Portal

# Check if we're in the right directory
if [ ! -f "src/portal.py" ]; then
    echo "Error: Please run this script from the Pro-BOTno root directory"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it using: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

echo "Starting UNHCR Refugee Assistance Portal..."
echo "========================================"
echo ""
echo "The portal will open in your browser at http://localhost:8501"
echo ""
echo "Features:"
echo "  - Audio transcription and translation"
echo "  - Interactive case assessment"
echo "  - Comprehensive legal analysis"
echo "  - PDF report generation"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd src
streamlit run portal.py

