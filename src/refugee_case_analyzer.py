#!/usr/bin/env python3
"""
Refugee Case Analyzer - Standalone CLI Tool

This tool analyzes refugee cases and provides relevant case law and legal analysis
using both general legal documents (RAG) and Swiss federal legislation (Fedlex).

Usage:
    # From command line argument
    python refugee_case_analyzer.py "A Syrian refugee seeks asylum in Switzerland..."
    
    # From stdin
    echo "Case details..." | python refugee_case_analyzer.py
    
    # From file
    python refugee_case_analyzer.py --file case.txt
    
    # Interactive mode
    python refugee_case_analyzer.py --interactive
"""

import os
import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from modules.enhanced_rag import build_enhanced_rag_chain


# Configuration
DEFAULT_DB_FOLDER = "vector_db_data"
DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
DEFAULT_LLM_MODEL = "gpt-5"  # Using gpt-5 (latest GPT-5 model)
ENABLE_FEDLEX = True
FETCH_XML = True
XML_LANGUAGE = 'de'


class RefugeeCaseAnalyzer:
    """Standalone refugee case analyzer with Fedlex and RAG integration"""
    
    def __init__(
        self,
        api_key: str = None,
        db_folder: str = DEFAULT_DB_FOLDER,
        model_name: str = DEFAULT_MODEL_NAME,
        llm_model: str = DEFAULT_LLM_MODEL,
        enable_fedlex: bool = ENABLE_FEDLEX,
        fetch_xml: bool = FETCH_XML,
        xml_language: str = XML_LANGUAGE,
        verbose: bool = True
    ):
        """
        Initialize the refugee case analyzer
        
        Args:
            api_key: OpenAI API key
            db_folder: Path to ChromaDB vector database
            model_name: HuggingFace embedding model name
            llm_model: OpenAI LLM model name
            enable_fedlex: Enable Swiss legislation queries
            fetch_xml: Fetch full XML legal texts
            xml_language: Language for XML documents
            verbose: Print progress messages
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.db_folder = db_folder
        self.model_name = model_name
        self.llm_model = llm_model
        self.enable_fedlex = enable_fedlex
        self.fetch_xml = fetch_xml
        self.xml_language = xml_language
        self.verbose = verbose
        
        self.chain = None
        self._initialize()
    
    def _log(self, message: str):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)
    
    def _initialize(self):
        """Initialize embeddings, vector database, and RAG chain"""
        self._log("Initializing Refugee Case Analyzer...")
        
        # Load embeddings
        self._log(f"Loading embedding model: {self.model_name}")
        embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"}
        )
        
        # Load vector database
        self._log(f"Loading vector database from: {self.db_folder}")
        if not os.path.exists(self.db_folder):
            raise FileNotFoundError(
                f"Vector database not found at: {self.db_folder}\n"
                f"Please ensure the database is created and the path is correct."
            )
        
        vector_db = Chroma(
            persist_directory=self.db_folder,
            embedding_function=embeddings
        )
        
        # Build enhanced RAG chain
        self._log(f"Building RAG chain with LLM: {self.llm_model}")
        self._log(f"Fedlex enabled: {self.enable_fedlex}")
        self._log(f"XML fetching: {self.fetch_xml}")
        
        self.chain = build_enhanced_rag_chain(
            vector_db=vector_db,
            api_key=self.api_key,
            k=4,
            model=self.llm_model,
            fetch_xml=self.fetch_xml,
            xml_language=self.xml_language,
            enable_fedlex=self.enable_fedlex
        )
        
        self._log("✓ Initialization complete\n")
    
    def analyze_case(self, case_description: str) -> dict:
        """
        Analyze a refugee case and return relevant case law and legal analysis
        
        Args:
            case_description: Description of the refugee case
            
        Returns:
            Dictionary with analysis results
        """
        if not case_description or not case_description.strip():
            raise ValueError("Case description cannot be empty")
        
        self._log("Analyzing refugee case...")
        self._log(f"Input length: {len(case_description)} characters\n")
        
        # Run the enhanced chain
        response = self.chain(case_description.strip())
        
        self._log("✓ Analysis complete\n")
        
        return response
    
    def format_output(self, response: dict, include_metadata: bool = True) -> str:
        """
        Format the analysis response for stdout output
        
        Args:
            response: Response from analyze_case
            include_metadata: Include metadata in output
            
        Returns:
            Formatted string output
        """
        output_lines = []
        
        # Header
        output_lines.append("=" * 80)
        output_lines.append("REFUGEE CASE LEGAL ANALYSIS")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # Main analysis
        output_lines.append("LEGAL ANALYSIS:")
        output_lines.append("-" * 80)
        output_lines.append(response.get("answer", "No analysis available."))
        output_lines.append("")
        
        if include_metadata:
            # Metadata section
            output_lines.append("=" * 80)
            output_lines.append("METADATA")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            source = response.get("source", "UNKNOWN")
            route = response.get("route_decision", "N/A")
            
            output_lines.append(f"Data Source: {source}")
            output_lines.append(f"Route Decision: {route}")
            
            if response.get("fallback_used"):
                output_lines.append("⚠️  FALLBACK USED: No Swiss legislation found, used general documents")
            
            if source in ["FEDLEX", "BOTH"]:
                if response.get("fedlex_results_found", True):
                    output_lines.append("✓ Swiss Federal Legislation (Fedlex) included")
                else:
                    output_lines.append("ℹ️  No Swiss Federal Legislation found")
            
            if source in ["RAG", "BOTH"] or "Fallback" in source:
                output_lines.append("✓ General Legal Documents included")
            
            output_lines.append("")
            
            # RAG sources
            if response.get("context"):
                output_lines.append("REFERENCED DOCUMENTS:")
                output_lines.append("-" * 80)
                docs = response.get("context", [])
                for i, doc in enumerate(docs, 1):
                    meta = getattr(doc, "metadata", {}) or {}
                    source_path = meta.get("source", "Unknown")
                    output_lines.append(f"{i}. {source_path}")
                output_lines.append("")
            
            # Swiss legislation details
            if response.get("sparql_results") and "No results found" not in response.get("sparql_results", ""):
                output_lines.append("SWISS LEGISLATION DETAILS:")
                output_lines.append("-" * 80)
                # Truncate if too long
                sparql_results = response.get("sparql_results", "")
                if len(sparql_results) > 3000:
                    output_lines.append(sparql_results[:3000])
                    output_lines.append(f"\n... (truncated, {len(sparql_results)} total characters)")
                else:
                    output_lines.append(sparql_results)
                output_lines.append("")
        
        output_lines.append("=" * 80)
        output_lines.append("END OF ANALYSIS")
        output_lines.append("=" * 80)
        
        return "\n".join(output_lines)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze refugee cases with relevant case law and legal analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze from command line
  python refugee_case_analyzer.py "A Syrian refugee family seeks asylum..."
  
  # Read from file
  python refugee_case_analyzer.py --file case.txt
  
  # Read from stdin
  echo "Case details..." | python refugee_case_analyzer.py
  
  # Interactive mode
  python refugee_case_analyzer.py --interactive
  
  # Disable Swiss legislation queries
  python refugee_case_analyzer.py --no-fedlex "Case details..."
  
  # Use different language for Swiss laws
  python refugee_case_analyzer.py --language fr "Case details..."
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "case_description",
        nargs="?",
        help="Case description as command line argument"
    )
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Read case description from file"
    )
    input_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode (multi-line input)"
    )
    
    # Configuration options
    parser.add_argument(
        "--db-folder",
        type=str,
        default=DEFAULT_DB_FOLDER,
        help=f"Path to vector database (default: {DEFAULT_DB_FOLDER})"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_LLM_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_LLM_MODEL})"
    )
    parser.add_argument(
        "--no-fedlex",
        action="store_true",
        help="Disable Swiss legislation queries"
    )
    parser.add_argument(
        "--no-xml",
        action="store_true",
        help="Disable XML fetching (faster but less detailed)"
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["de", "fr", "it", "rm"],
        default="de",
        help="Language for Swiss legal documents (default: de)"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    # Get case description from various sources
    case_description = None
    
    if args.case_description:
        case_description = args.case_description
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                case_description = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.interactive:
        print("Enter case description (press Ctrl+D or Ctrl+Z when done):", file=sys.stderr)
        case_description = sys.stdin.read()
    elif not sys.stdin.isatty():
        # Read from stdin
        case_description = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)
    
    if not case_description or not case_description.strip():
        print("Error: No case description provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize analyzer
        analyzer = RefugeeCaseAnalyzer(
            db_folder=args.db_folder,
            llm_model=args.model,
            enable_fedlex=not args.no_fedlex,
            fetch_xml=not args.no_xml,
            xml_language=args.language,
            verbose=not args.quiet
        )
        
        # Analyze case
        response = analyzer.analyze_case(case_description)
        
        # Format and output
        output = analyzer.format_output(response, include_metadata=not args.no_metadata)
        print(output)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        if not args.quiet:
            print("\nStack trace:", file=sys.stderr)
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

