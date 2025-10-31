"""
Fedlex SPARQL Client Module

This module provides functionality for querying the Swiss Fedlex legal database
using SPARQL queries, including LLM-generated queries and XML document fetching.
"""

import re
import requests
from datetime import datetime
from typing import Optional, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
from langchain_core.output_parsers import StrOutputParser

from prompts.fedlex_prompts import (
    SPARQL_GENERATION_PROMPT,
    FEDLEX_SCHEMA_INFO
)


# ============================================================================
# CONSTANTS
# ============================================================================

FEDLEX_SPARQL_ENDPOINT = "https://fedlex.data.admin.ch/sparqlendpoint"

SWISS_LANGUAGES = {
    'de': 'German',
    'fr': 'French',
    'it': 'Italian',
    'rm': 'Romansh'
}

LANGUAGE_URIS = {
    'de': '<http://publications.europa.eu/resource/authority/language/DEU>',
    'fr': '<http://publications.europa.eu/resource/authority/language/FRA>',
    'it': '<http://publications.europa.eu/resource/authority/language/ITA>',
    'rm': '<http://publications.europa.eu/resource/authority/language/RMH>'
}


# ============================================================================
# FEDLEX SPARQL CLIENT
# ============================================================================

class FedlexSPARQLClient:
    """Enhanced client for querying Swiss Fedlex with LLM-generated SPARQL"""

    def __init__(self, endpoint: str = FEDLEX_SPARQL_ENDPOINT, llm=None):
        """
        Initialize Fedlex SPARQL client
        
        Args:
            endpoint: SPARQL endpoint URL
            llm: Language model for generating SPARQL queries
        """
        self.endpoint = endpoint
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        self.llm = llm

        self.prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
PREFIX schema: <http://schema.org/>
"""

    def generate_sparql_query(self, natural_language_question: str) -> str:
        """
        Use LLM to generate SPARQL query from natural language
        
        Args:
            natural_language_question: User's question in natural language
            
        Returns:
            Generated SPARQL query string
        """
        if not self.llm:
            raise ValueError("LLM not initialized for SPARQL generation")

        query_chain = SPARQL_GENERATION_PROMPT | self.llm | StrOutputParser()
        generated_query = query_chain.invoke({
            "schema_info": FEDLEX_SCHEMA_INFO,
            "question": natural_language_question
        })

        # Clean up the generated query
        generated_query = generated_query.strip()

        # Remove markdown code blocks if present
        generated_query = re.sub(r'^```sparql\s*', '', generated_query)
        generated_query = re.sub(r'^```\s*', '', generated_query)
        generated_query = re.sub(r'\s*```$', '', generated_query)

        # Remove any prefix declarations (we add them ourselves)
        lines = generated_query.split('\n')
        query_lines = [line for line in lines if not line.strip().startswith('PREFIX')]
        generated_query = '\n'.join(query_lines).strip()

        return generated_query

    def execute_query(self, sparql_query: str, include_prefixes: bool = True) -> Dict:
        """
        Execute a SPARQL query and return results
        
        Args:
            sparql_query: SPARQL query string
            include_prefixes: Whether to prepend standard prefixes
            
        Returns:
            Query results dictionary
        """
        try:
            if include_prefixes:
                full_query = self.prefixes + "\n" + sparql_query
            else:
                full_query = sparql_query

            print(f"\n[EXECUTING SPARQL QUERY]:\n{full_query}\n")

            self.sparql.setQuery(full_query)
            results = self.sparql.query().convert()
            return results
        except Exception as e:
            return {"error": str(e)}

    def query_with_llm(self, natural_language_question: str) -> Dict:
        """
        Generate and execute SPARQL query from natural language
        
        Args:
            natural_language_question: User's question
            
        Returns:
            Dictionary with results, generated query, and question
        """
        try:
            sparql_query = self.generate_sparql_query(natural_language_question)
            results = self.execute_query(sparql_query)

            return {
                "results": results,
                "generated_query": sparql_query,
                "question": natural_language_question
            }
        except Exception as e:
            return {
                "error": str(e),
                "question": natural_language_question
            }

    def fetch_xml_document(
        self, 
        consolidation_uri: str, 
        language: str = 'de', 
        timeout: int = 30
    ) -> Dict:
        """
        Fetch XML plaintext document from Fedlex given a consolidation URI
        
        Args:
            consolidation_uri: The consolidation URI
            language: Language code ('de', 'fr', 'it', 'rm')
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with status, content, and metadata
        """
        try:
            # Build SPARQL query to get XML download link
            query = f"""
            SELECT ?xml_link WHERE {{
                <{consolidation_uri}> jolux:isRealizedBy ?expression .

                ?expression jolux:language {LANGUAGE_URIS.get(language, LANGUAGE_URIS['de'])} ;
                            jolux:isEmbodiedBy ?manifestation .

                ?manifestation jolux:format <http://publications.europa.eu/resource/authority/file-type/XML> ;
                               jolux:isExemplifiedBy ?xml_link .
            }}
            LIMIT 1
            """

            results = self.execute_query(query)

            if "error" in results:
                return {
                    "status": "error",
                    "consolidation_uri": consolidation_uri,
                    "error": f"SPARQL query error: {results['error']}"
                }

            bindings = results.get("results", {}).get("bindings", [])

            if not bindings:
                return {
                    "status": "error",
                    "consolidation_uri": consolidation_uri,
                    "error": f"No XML document found for language '{language}'"
                }

            xml_url = bindings[0].get("xml_link", {}).get("value", "")

            if not xml_url:
                return {
                    "status": "error",
                    "consolidation_uri": consolidation_uri,
                    "error": "XML URL not found in query results"
                }

            # Fetch the XML content
            print(f"\n[FETCHING XML]: {xml_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(xml_url, headers=headers, timeout=timeout)
            response.raise_for_status()

            return {
                "status": "success",
                "consolidation_uri": consolidation_uri,
                "xml_url": xml_url,
                "language": language,
                "content": response.text,
                "size_bytes": len(response.content)
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "consolidation_uri": consolidation_uri,
                "error": f"HTTP request error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "consolidation_uri": consolidation_uri,
                "error": f"Unexpected error: {str(e)}"
            }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_law_applicable(
    date_applicability: str, 
    date_end_applicability: str, 
    reference_date: Optional[datetime] = None
) -> Dict:
    """
    Check if a law is applicable at a given date based on JOLux applicability dates.
    
    Args:
        date_applicability: Start date of applicability (ISO format string)
        date_end_applicability: End date of applicability (ISO format string)
        reference_date: Date to check against (defaults to today)
        
    Returns:
        Dictionary with applicability status and details
    """
    if reference_date is None:
        reference_date = datetime.now()

    result = {
        "is_applicable": False,
        "status": "unknown",
        "details": ""
    }

    try:
        # Parse dates
        start_date = datetime.fromisoformat(
            date_applicability.replace('Z', '+00:00')
        ) if date_applicability else None
        end_date = datetime.fromisoformat(
            date_end_applicability.replace('Z', '+00:00')
        ) if date_end_applicability else None

        # Check applicability
        if start_date and not end_date:
            # Law is applicable from start_date onwards
            if reference_date >= start_date:
                result["is_applicable"] = True
                result["status"] = "currently_applicable"
                result["details"] = f"Applicable since {start_date.date()}"
            else:
                result["status"] = "not_yet_applicable"
                result["details"] = f"Will be applicable from {start_date.date()}"

        elif start_date and end_date:
            # Law has both start and end dates
            if start_date <= reference_date <= end_date:
                result["is_applicable"] = True
                result["status"] = "currently_applicable"
                result["details"] = f"Applicable from {start_date.date()} to {end_date.date()}"
            elif reference_date < start_date:
                result["status"] = "not_yet_applicable"
                result["details"] = f"Will be applicable from {start_date.date()} to {end_date.date()}"
            else:
                result["status"] = "expired"
                result["details"] = f"Was applicable from {start_date.date()} to {end_date.date()}"

        elif not start_date and not end_date:
            result["status"] = "no_dates_available"
            result["details"] = "Applicability dates not specified"

    except Exception as e:
        result["status"] = "error"
        result["details"] = f"Error parsing dates: {str(e)}"

    return result


def construct_document_urls(uri: str) -> Dict[str, str]:
    """
    Construct browser URLs for all Swiss languages from a Fedlex URI
    
    Args:
        uri: Fedlex URI
        
    Returns:
        Dictionary mapping language names to URLs
    """
    base_url = uri.replace(
        "https://fedlex.data.admin.ch", 
        "https://www.fedlex.admin.ch"
    )

    urls = {}
    for lang_code, lang_name in SWISS_LANGUAGES.items():
        urls[lang_name] = f"{base_url}/{lang_code}"

    return urls


def format_sparql_results(
    query_response: Dict,
    filter_applicable: bool = True,
    fetch_xml: bool = True,
    fedlex_client: Optional[FedlexSPARQLClient] = None,
    language: str = 'de'
) -> str:
    """
    Format SPARQL query response into readable text with proper URLs, 
    applicability filtering, and XML content for LLM analysis
    
    Args:
        query_response: Response from SPARQL query
        filter_applicable: If True, only show currently applicable laws
        fetch_xml: If True, fetch XML content for applicable laws
        fedlex_client: FedlexSPARQLClient instance for fetching XML
        language: Language code for XML fetching
        
    Returns:
        Formatted string with results and XML content
    """
    if "error" in query_response:
        return f"Error querying Fedlex: {query_response['error']}"

    results = query_response.get("results", {})
    generated_query = query_response.get("generated_query", "N/A")

    output = f"**Generated SPARQL Query:**\n```sparql\n{generated_query}\n```\n\n"

    if "error" in results:
        return output + f"Query execution error: {results['error']}"

    if "results" not in results or "bindings" not in results["results"]:
        return output + "No results found in Fedlex database."

    bindings = results["results"]["bindings"]
    if not bindings:
        return output + "No results found in Fedlex database."

    # Filter for applicable laws if requested
    filtered_bindings = []
    for binding in bindings:
        date_applicability = binding.get("dateApplicability", {}).get("value", "")
        date_end_applicability = binding.get("dateEndApplicability", {}).get("value", "")

        applicability = is_law_applicable(date_applicability, date_end_applicability)

        if not filter_applicable or applicability["is_applicable"]:
            binding["_applicability"] = applicability
            filtered_bindings.append(binding)

    if not filtered_bindings:
        return output + "No currently applicable laws found matching the criteria."

    output += f"**Found {len(filtered_bindings)} applicable result(s)** (out of {len(bindings)} total):\n\n"

    for i, binding in enumerate(filtered_bindings, 1):
        output += f"**Result {i}:**\n"

        # Extract URIs and metadata
        work_uri = binding.get("work", {}).get("value", "")
        consolidation_uri = binding.get("consolidation", {}).get("value", "")
        title = binding.get("title", {}).get("value", "N/A")
        sr_number = binding.get("sr_number", {}).get("value", "N/A")
        date = binding.get("date", {}).get("value", "N/A")
        lang = binding.get("lang", {}).get("value", "N/A")

        applicability = binding.get("_applicability", {})

        output += f"  - **Title**: {title}\n"
        output += f"  - **SR Number**: {sr_number}\n"
        output += f"  - **Date**: {date}\n"
        if lang != "N/A":
            output += f"  - **Language**: {lang}\n"

        # Add applicability status
        output += f"  - **Applicability Status**: {applicability.get('status', 'unknown')}\n"
        output += f"  - **Details**: {applicability.get('details', 'N/A')}\n"

        # Add document links in all languages
        if work_uri:
            output += "\n  **Document Links (all languages):**\n"
            doc_urls = construct_document_urls(work_uri)
            for lang_name, url in doc_urls.items():
                output += f"  - [{lang_name}]({url})\n"

        # Fetch XML content if requested - THIS IS KEY FOR LLM ANALYSIS
        if fetch_xml and consolidation_uri and fedlex_client:
            output += f"\n  **Fetching full XML legal text ({language})...**\n"
            xml_result = fedlex_client.fetch_xml_document(consolidation_uri, language=language)

            if xml_result["status"] == "success":
                xml_content = xml_result["content"]
                output += f"  - ✓ XML fetched successfully ({xml_result['size_bytes']} bytes)\n"
                output += f"  - XML URL: {xml_result['xml_url']}\n\n"
                
                # Include FULL XML content for LLM analysis with clear markers
                output += "  **FULL LEGAL TEXT (XML - for citation and analysis):**\n"
                output += "  ```xml\n"
                output += f"  {xml_content}\n"
                output += "  ```\n\n"
                
                output += "  ⚠️ **IMPORTANT**: The above XML contains the complete legal text. "
                output += "Please extract and cite specific articles, sections, and provisions "
                output += "relevant to the lawyer's question.\n"
                
                # Store for potential use
                binding["_xml_content"] = xml_content
            else:
                output += f"  - ✗ Error fetching XML: {xml_result.get('error', 'Unknown error')}\n"

        output += "\n" + "="*80 + "\n\n"

    return output

