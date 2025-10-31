"""
Enhanced RAG Module

This module combines traditional RAG (Retrieval-Augmented Generation) with
Swiss Fedlex SPARQL queries to provide comprehensive legal assistance.
"""

from typing import Dict, List, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from prompts.fedlex_prompts import (
    ROUTER_PROMPT,
    RAG_PROMPT,
    SPARQL_INTERPRETATION_PROMPT,
    COMBINED_PROMPT
)
from modules.fedlex_client import FedlexSPARQLClient, format_sparql_results


# ============================================================================
# ENHANCED RAG CHAIN BUILDER
# ============================================================================

def build_enhanced_rag_chain(
    vector_db,
    api_key: str,
    k: int = 4,
    model: str = "gpt-5",
    fetch_xml: bool = True,
    xml_language: str = 'de',
    enable_fedlex: bool = True
):
    """
    Build enhanced RAG chain with routing between general documents and Swiss legislation
    
    Args:
        vector_db: ChromaDB vector database for general documents
        api_key: OpenAI API key
        k: Number of documents to retrieve from RAG
        model: LLM model name
        fetch_xml: Whether to fetch full XML legal texts
        xml_language: Language for XML fetching ('de', 'fr', 'it', 'rm')
        enable_fedlex: Whether to enable Fedlex queries (can be disabled for testing)
        
    Returns:
        Callable chain function
    """
    llm = ChatOpenAI(model=model, openai_api_key=api_key, temperature=0)
    
    # Initialize Fedlex client with LLM for SPARQL generation
    fedlex_client = None
    if enable_fedlex:
        fedlex_client = FedlexSPARQLClient(llm=llm)
    
    retriever = vector_db.as_retriever(search_kwargs={"k": k})

    def format_docs(docs: List[Any]) -> str:
        """Format retrieved documents for prompt context"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            meta = getattr(doc, "metadata", {}) or {}
            source = meta.get("source", "Unknown")
            formatted.append(
                f"--- Document {i} (Source: {source}) ---\n{doc.page_content}"
            )
        return "\n\n".join(formatted)

    def query_fedlex_intelligent(question: str) -> tuple[str, bool]:
        """
        Query Fedlex using LLM-generated SPARQL and fetch XML content
        
        Returns:
            tuple: (formatted_results, has_results)
        """
        if not fedlex_client:
            return "Fedlex is not enabled.", False
            
        try:
            print("\n[FEDLEX] Generating SPARQL query using LLM...")
            query_response = fedlex_client.query_with_llm(question)
            
            formatted = format_sparql_results(
                query_response,
                filter_applicable=True,
                fetch_xml=fetch_xml,
                fedlex_client=fedlex_client,
                language=xml_language
            )
            
            # Check if results were found
            has_results = not any([
                "No results found" in formatted,
                "No currently applicable laws found" in formatted,
                "Error querying Fedlex" in formatted
            ])
            
            return formatted, has_results
        except Exception as e:
            return f"Error querying Fedlex: {str(e)}", False

    def enhanced_chain(input_text: str) -> Dict[str, Any]:
        """
        Main chain logic with intelligent routing
        
        Args:
            input_text: User's question
            
        Returns:
            Dictionary with answer, context, source, and metadata
        """
        # Step 1: Route the question
        print("\n" + "="*80)
        print("[ROUTER] Analyzing question to determine best data source...")
        print("="*80)
        
        route_chain = ROUTER_PROMPT | llm | StrOutputParser()
        route_decision = route_chain.invoke({"input": input_text})
        route = route_decision.strip().upper()
        
        print(f"[ROUTER] Decision: {route}")
        print(f"[ROUTER] Explanation: ", end="")
        if route == "RAG":
            print("Question is about general/international legal documents only")
        elif route == "BOTH":
            print("Question involves Swiss context - using RAG to guide Fedlex searches")
        else:
            # Fallback to BOTH for any unexpected routing
            print("Defaulting to comprehensive search (BOTH)")
            route = "BOTH"
        print("="*80 + "\n")

        # Step 2: Execute based on routing decision
        
        if route == "RAG" or not enable_fedlex:
            # Query only general document database
            print("[RAG] Querying general legal document database...")
            docs = retriever.invoke(input_text)
            context = format_docs(docs)

            print("[RAG] Generating expert legal analysis...")
            rag_chain = RAG_PROMPT | llm | StrOutputParser()
            answer = rag_chain.invoke({
                "context": context,
                "input": input_text
            })

            return {
                "answer": answer,
                "context": docs,
                "source": "RAG",
                "route_decision": route
            }

        else:  # BOTH (default for Swiss-related questions)
            # Query both databases - RAG guides Fedlex searches
            print("[BOTH] Comprehensive search: RAG + Fedlex (RAG guides Fedlex)")
            
            print("  → Retrieving from general document database (provides context)...")
            docs = retriever.invoke(input_text)
            rag_context = format_docs(docs)
            
            # Use RAG context to inform the Fedlex query
            enriched_question = f"{input_text}\n\nContext from general documents: {rag_context[:500]}"
            
            print("  → Querying Swiss federal legislation (guided by RAG context)...")
            sparql_results, has_fedlex_results = query_fedlex_intelligent(enriched_question)

            # If no Fedlex results, still provide RAG-based analysis
            if not has_fedlex_results:
                print("[BOTH] ℹ️  No Swiss legislation found, providing RAG-based analysis")
                sparql_results = (
                    "**No applicable Swiss federal legislation found in Fedlex database.**\n"
                    "Analysis is based on general legal documents and international law.\n\n"
                    + sparql_results
                )

            print("[BOTH] Synthesizing comprehensive legal analysis...")
            combined_chain = COMBINED_PROMPT | llm | StrOutputParser()
            answer = combined_chain.invoke({
                "rag_context": rag_context,
                "sparql_results": sparql_results,
                "input": input_text
            })

            return {
                "answer": answer,
                "context": docs,
                "source": "BOTH (RAG-guided)",
                "sparql_results": sparql_results,
                "route_decision": route,
                "fedlex_results_found": has_fedlex_results
            }

    return enhanced_chain


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_response_for_display(response: Dict[str, Any]) -> str:
    """
    Format response dictionary into a clean display format
    
    Args:
        response: Response dictionary from enhanced_chain
        
    Returns:
        Formatted string for display
    """
    output = []
    
    # Main answer
    output.append("## Legal Analysis\n")
    output.append(response.get("answer", "No answer generated."))
    output.append("\n")
    
    # Source information
    source = response.get("source", "UNKNOWN")
    output.append(f"\n---\n**Data Source**: {source}\n")
    
    if source in ["FEDLEX", "BOTH"]:
        output.append("✓ Includes Swiss Federal Legislation (Fedlex)")
    if source in ["RAG", "BOTH"]:
        output.append("✓ Includes General Legal Documents")
    
    # RAG sources
    if response.get("context"):
        output.append("\n### Referenced Documents\n")
        for i, doc in enumerate(response["context"], 1):
            meta = getattr(doc, "metadata", {}) or {}
            source_path = meta.get("source", "Unknown")
            output.append(f"{i}. `{source_path}`")
    
    return "\n".join(output)


def get_xml_citations(response: Dict[str, Any]) -> List[str]:
    """
    Extract XML citations from response for verification
    
    Args:
        response: Response dictionary from enhanced_chain
        
    Returns:
        List of XML content strings
    """
    citations = []
    
    sparql_results = response.get("sparql_results", "")
    if sparql_results and "```xml" in sparql_results:
        # Extract XML blocks
        import re
        xml_blocks = re.findall(r'```xml\s*(.*?)\s*```', sparql_results, re.DOTALL)
        citations.extend(xml_blocks)
    
    return citations

