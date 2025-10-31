"""
Backend Case Processor
Refactored refugee case analyzer with bibliography generation
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from modules.enhanced_rag import build_enhanced_rag_chain


class CaseProcessor:
    """
    Backend service for processing refugee cases with legal analysis
    and bibliography generation
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        db_folder: str = "vector_db_data",
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        llm_model: str = "gpt-5",
        enable_fedlex: bool = True,
        fetch_xml: bool = True,
        xml_language: str = "de"
    ):
        """Initialize the case processor"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.db_folder = db_folder
        self.model_name = model_name
        self.llm_model = llm_model
        self.enable_fedlex = enable_fedlex
        self.fetch_xml = fetch_xml
        self.xml_language = xml_language
        
        self._initialize()
    
    def _initialize(self):
        """Initialize embeddings, vector database, and RAG chain"""
        print("[BACKEND] Initializing Case Processor...")
        
        # Load embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"}
        )
        
        # Load vector database
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            self.db_folder
        )
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Vector database not found at: {db_path}")
        
        vector_db = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )
        
        # Build enhanced RAG chain
        self.chain = build_enhanced_rag_chain(
            vector_db=vector_db,
            api_key=self.api_key,
            k=4,
            model=self.llm_model,
            fetch_xml=self.fetch_xml,
            xml_language=self.xml_language,
            enable_fedlex=self.enable_fedlex
        )
        
        # Initialize LLM for bibliography generation
        self.llm = ChatOpenAI(
            model=self.llm_model,
            openai_api_key=self.api_key,
            temperature=0
        )
        
        print("[BACKEND] ✓ Initialization complete")
    
    def process_case(
        self,
        case_summary: str,
        transcription: Optional[str] = None,
        forms_text: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a refugee case with comprehensive legal analysis
        
        Args:
            case_summary: Summary of the case
            transcription: Transcribed and translated interview
            forms_text: Extracted text from PDF forms
            chat_history: Chat conversation history
            
        Returns:
            Dictionary with analysis and bibliography
        """
        print("[BACKEND] Processing case...")
        
        # Build comprehensive case description
        full_case = self._build_case_description(
            case_summary, transcription, forms_text, chat_history
        )
        
        # Run legal analysis
        response = self.chain(full_case)
        
        # Extract bibliography
        bibliography = self._extract_bibliography(response)
        
        # Generate structured legal summary
        legal_summary = self._generate_legal_summary(
            response, transcription, forms_text
        )
        
        print("[BACKEND] ✓ Processing complete")
        
        return {
            "legal_analysis": response.get("answer", ""),
            "legal_summary": legal_summary,
            "bibliography": bibliography,
            "source_documents": self._format_source_documents(response),
            "case_law_summary": self._extract_case_law_summary(response),
            "raw_response": response,
            "processed_at": datetime.now().isoformat()
        }
    
    def _build_case_description(
        self,
        case_summary: str,
        transcription: Optional[str] = None,
        forms_text: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build comprehensive case description from all sources"""
        parts = []
        
        # Main case summary
        if case_summary:
            parts.append("=== CASE SUMMARY ===\n" + case_summary)
        
        # Interview transcription
        if transcription:
            parts.append("\n\n=== TRANSCRIBED INTERVIEW ===\n" + transcription)
        
        # Form data
        if forms_text:
            parts.append("\n\n=== ASYLUM APPLICATION FORMS ===\n" + forms_text)
        
        # Chat history
        if chat_history:
            chat_text = "\n".join([
                f"{'Lawyer' if msg['role'] == 'user' else 'Asylum Seeker'}: {msg['content']}"
                for msg in chat_history
            ])
            parts.append("\n\n=== FOLLOW-UP QUESTIONS ===\n" + chat_text)
        
        return "\n".join(parts)
    
    def _extract_bibliography(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract bibliography from response (sources, case law, legislation)
        """
        bibliography = []
        
        # Add source documents
        if response.get("context"):
            for i, doc in enumerate(response["context"], 1):
                meta = getattr(doc, "metadata", {}) or {}
                source_path = meta.get("source", "Unknown")
                
                bibliography.append({
                    "type": "General Legal Document",
                    "reference": f"[{i}]",
                    "title": os.path.basename(source_path),
                    "path": source_path,
                    "excerpt": doc.page_content[:200] + "..."
                })
        
        # Add Swiss legislation
        if response.get("sparql_results"):
            sparql_text = response["sparql_results"]
            # Parse legislation titles and SR numbers from SPARQL results
            legislation = self._parse_legislation_from_sparql(sparql_text)
            
            for i, law in enumerate(legislation, 1):
                bibliography.append({
                    "type": "Swiss Federal Legislation",
                    "reference": f"[L{i}]",
                    "title": law.get("title", "Unknown"),
                    "sr_number": law.get("sr_number", "N/A"),
                    "link": law.get("link", "")
                })
        
        return bibliography
    
    def _parse_legislation_from_sparql(self, sparql_results: str) -> List[Dict[str, str]]:
        """Parse legislation information from SPARQL results"""
        import re
        
        legislation = []
        
        # Extract legislation titles and SR numbers
        # Look for patterns like "SR X.XXX" or "SR-Number: X.XXX"
        sr_pattern = r'SR[- ](?:Number)?[:\s]*(\d+(?:\.\d+)*)'
        title_pattern = r'\*\*([^*]+)\*\*'
        link_pattern = r'https://fedlex\.admin\.ch/eli/[^\s)"]+'
        
        # Find all SR numbers
        sr_numbers = re.findall(sr_pattern, sparql_results)
        titles = re.findall(title_pattern, sparql_results)
        links = re.findall(link_pattern, sparql_results)
        
        # Combine them
        max_len = max(len(sr_numbers), len(titles), len(links))
        for i in range(max_len):
            legislation.append({
                "sr_number": sr_numbers[i] if i < len(sr_numbers) else "N/A",
                "title": titles[i] if i < len(titles) else "Swiss Legislation",
                "link": links[i] if i < len(links) else ""
            })
        
        return legislation
    
    def _format_source_documents(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format source documents for easy reference"""
        documents = []
        
        if response.get("context"):
            for doc in response["context"]:
                meta = getattr(doc, "metadata", {}) or {}
                documents.append({
                    "source": meta.get("source", "Unknown"),
                    "content": doc.page_content,
                    "metadata": meta
                })
        
        return documents
    
    def _extract_case_law_summary(self, response: Dict[str, Any]) -> str:
        """Extract summary of relevant case law from response"""
        # Use LLM to extract case law summary from the full analysis
        extraction_prompt = f"""
        Extract and summarize ONLY the case law and legal precedents mentioned in the following legal analysis.
        Focus on:
        - Specific cases cited
        - Legal precedents
        - Court decisions
        - Established legal principles
        
        If no specific case law is mentioned, return "No specific case law cited."
        
        Legal Analysis:
        {response.get('answer', '')}
        
        Case Law Summary:
        """
        
        chain = self.llm | StrOutputParser()
        summary = chain.invoke(extraction_prompt)
        
        return summary
    
    def _generate_legal_summary(
        self,
        response: Dict[str, Any],
        transcription: Optional[str] = None,
        forms_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured legal summary with references to appendices
        """
        analysis = response.get("answer", "")
        
        # Use LLM to structure the summary with proper references
        summary_prompt = f"""
        You are creating a legal summary for a refugee case file. Structure the following analysis into clear sections with proper references to appendices.
        
        - Use Title Case for subheadings (e.g., "Identity and Entry History").
        - Use numbered sections and subsections (1., 1.1, 1.2, etc.) and make the text bold to emphasize the difference. If you use numbered sections/subsections, make sure you do a line break and start in a new line after for the respective additional information regarding the topic.
        - Write in neutral, concise, and objective legal language.
        - Avoid bullet points unless listing more than three related items. If bullet points are used, do a line break to make sure every bullet point starts with a new line.
        - Only use proper punctuations, no weird symbols such as ■
        - Keep paragraphs between 2–5 sentences each.
        - Use **page-break markers** between major sections.
        - Use exact appendix references:
          - Asylum seeker forms → *(see Appendix I)*
          - Interview transcripts → *(see Appendix II)*
          - Case law → *(see Appendix III)*
        
        Create sections for:
        1. LEGALLY RELEVANT FACTS (with references to Appendix I and II): Based on the analysis provided, outline the relevant facts about the refugee. The situation, its family, history, or anything that is a factual information related to the refugee.
        2. APPLICABLE LAW (with references to Appendix III): In these section, review the applicable legal provisions based on the data
        3. LEGAL ASSESSMENT: In these section, utilize the provided data to evaluate how the facts meet the legal requirements
        4. CONCLUSION AND RECOMMENDATIONS: In this section, you will provide a professional conclusion and actionable recommendations. End with a brief summary of the key actions needed.
        Analysis to structure:
        {analysis}
        
        Ensure the final output is formatted according to the above structure with all sections numbered and the appropriate references to the appendices. Use the page-break markers (`—PAGE BREAK—`) to ensure clean separation of sections in the final PDF.
        Structured Summary:
        """
        
        chain = self.llm | StrOutputParser()
        structured_summary = chain.invoke(summary_prompt)
        
        return {
            "full_summary": structured_summary,
            "has_appendix_i": forms_text is not None,
            "has_appendix_ii": transcription is not None,
            "has_appendix_iii": response.get("context") or response.get("sparql_results")
        }
    
    def ask_follow_up_questions(self, case_info: str) -> List[str]:
        """
        Generate follow-up questions based on case information
        
        Args:
            case_info: Initial case information
            
        Returns:
            List of follow-up questions
        """
        question_prompt = f"""
        You are an immigration lawyer reviewing a refugee case. Based on the information provided, 
        what additional questions should be asked to properly assess the case?
        
        Generate 3-5 specific follow-up questions that would help clarify:
        - Legal status and documentation
        - Specific grounds for asylum (persecution, danger, etc.)
        - Family situation and dependents
        - Timeline and procedural status
        - Any missing critical information
        
        Case Information:
        {case_info}
        
        Return ONLY the questions, one per line, numbered 1-5.
        """
        
        chain = self.llm | StrOutputParser()
        response = chain.invoke(question_prompt)
        
        # Parse questions
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                question = line.lstrip('0123456789.-) ').strip()
                if question:
                    questions.append(question)
        
        return questions
    
    def extract_case_summary_from_chat(
        self,
        chat_history: List[Dict[str, str]],
        transcription: str
    ) -> Dict[str, str]:
        """
        Extract overview and family composition from chat history and transcription
        
        Args:
            chat_history: List of chat messages
            transcription: Interview transcription
            
        Returns:
            Dictionary with 'overview' and 'family_composition'
        """
        if not chat_history:
            return {
                "overview": "No additional information provided during assessment.",
                "family_composition": "See interview transcript in Appendix II."
            }
        
        # Build chat text
        chat_text = "\n".join([
            f"{'Lawyer' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in chat_history
        ])
        
        extraction_prompt = f"""
        Based on the interview transcript and follow-up Q&A session, extract:
        1. A brief overview of the asylum seeker's situation (2-3 sentences)
        2. Family composition (who they are traveling with, dependents, family members)
        
        Interview Transcript:
        {transcription[:1000]}...
        
        Follow-up Q&A:
        {chat_text}
        
        Provide your response in this exact format:
        OVERVIEW:
        [2-3 sentence overview]
        
        FAMILY_COMPOSITION:
        [family composition details]
        
        If information is not available, write "Information not provided."
        """
        
        chain = self.llm | StrOutputParser()
        response = chain.invoke(extraction_prompt)
        
        # Parse the response
        overview = "Information not provided."
        family_composition = "Information not provided."
        
        if "OVERVIEW:" in response and "FAMILY_COMPOSITION:" in response:
            parts = response.split("FAMILY_COMPOSITION:")
            overview_part = parts[0].replace("OVERVIEW:", "").strip()
            family_part = parts[1].strip()
            
            if overview_part and overview_part != "Information not provided.":
                overview = overview_part
            if family_part and family_part != "Information not provided.":
                family_composition = family_part
        
        return {
            "overview": overview,
            "family_composition": family_composition
        }

