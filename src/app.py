import os
import sys
import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_rag import build_enhanced_rag_chain, format_response_for_display

# Configuration
YOUR_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not YOUR_OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    st.stop()

DB_FOLDER = "vector_db_data"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "gpt-5"

# Fedlex Configuration
ENABLE_FEDLEX = True  # Set to False to disable Swiss legislation queries
FETCH_XML = True  # Set to False to skip XML fetching (faster but less detailed)
XML_LANGUAGE = 'de'  # Language for XML documents: 'de', 'fr', 'it', or 'rm'


@st.cache_resource
def load_all_models():
    print("Loading models...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"}
    )
    vector_db = Chroma(
        persist_directory=DB_FOLDER,
        embedding_function=embeddings
    )
    print("Database loaded.")
    return vector_db

@st.cache_resource
def build_rag_chain(
    _vector_db, 
    api_key, 
    k=4, 
    model=LLM_MODEL,
    enable_fedlex=ENABLE_FEDLEX,
    fetch_xml=FETCH_XML,
    xml_language=XML_LANGUAGE
):
    """Build enhanced RAG chain with optional Fedlex integration"""
    return build_enhanced_rag_chain(
        vector_db=_vector_db,
        api_key=api_key,
        k=k,
        model=model,
        fetch_xml=fetch_xml,
        xml_language=xml_language,
        enable_fedlex=enable_fedlex
    )


st.set_page_config(
    page_title="UNHCR Pro Bono Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ UNHCR Pro Bono Legal Assistant")
st.markdown("""
This assistant helps pro bono lawyers working with refugees by providing:
- **General Legal Documents**: European and international legal documents
- **Swiss Federal Legislation**: Official Swiss laws from Fedlex with exact legal citations

Ask any legal question and the system will intelligently route to the appropriate source(s).
""")

try:
    # Load models and build chain
    vector_db = load_all_models()
    chain = build_rag_chain(
        vector_db, 
        YOUR_OPENAI_API_KEY, 
        k=4, 
        model=LLM_MODEL,
        enable_fedlex=ENABLE_FEDLEX,
        fetch_xml=FETCH_XML,
        xml_language=XML_LANGUAGE
    )

    # Sidebar with configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"""
        **Current Settings:**
        - Model: {LLM_MODEL}
        - Fedlex: {'✓ Enabled' if ENABLE_FEDLEX else '✗ Disabled'}
        - XML Fetching: {'✓ Enabled' if FETCH_XML else '✗ Disabled'}
        - XML Language: {XML_LANGUAGE.upper()}
        """)
        
        if ENABLE_FEDLEX:
            st.success("Swiss legislation queries are enabled")
        else:
            st.warning("Swiss legislation queries are disabled")

    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_area(
            "Your Legal Question:",
            height=150,
            placeholder="e.g., What are the rights of unaccompanied minors seeking asylum in Switzerland?"
        )
    
    with col2:
        st.markdown("### Quick Tips")
        st.markdown("""
        - Be specific in your questions
        - Mention Switzerland for Swiss law
        - Ask about specific refugee situations
        - Request exact citations if needed
        """)

    if user_question:
        # Show a loading spinner while processing
        with st.spinner("🔍 Analyzing question and searching legal databases..."):
            response = chain(user_question)

        # Display the answer in a nice format
        st.markdown("---")
        st.subheader("📋 Legal Analysis")
        st.markdown(response.get("answer", "No answer found."))

        # Show metadata
        with st.expander("📊 Query Details", expanded=False):
            source = response.get("source", "UNKNOWN")
            st.write(f"**Data Source Used:** {source}")
            st.write(f"**Route Decision:** {response.get('route_decision', 'N/A')}")
            
            # Show fallback information
            if response.get("fallback_used"):
                st.warning("⚠️ Fedlex Fallback: No Swiss legislation found, used general documents instead")
            
            if "BOTH" in source or "Fedlex" in source:
                st.success("✓ Includes General Legal Documents (RAG)")
                if response.get("fedlex_results_found", True):
                    st.success("✓ Includes Swiss Federal Legislation (Fedlex)")
                    st.info("ℹ️ RAG context used to guide Fedlex searches")
                else:
                    st.warning("ℹ️ No Swiss Federal Legislation found in Fedlex")
            elif source == "RAG":
                st.success("✓ Includes General Legal Documents only")

        # Display RAG sources if available
        if response.get("context"):
            with st.expander("📚 Referenced Documents", expanded=False):
                docs = response.get("context", [])
                for i, doc in enumerate(docs, 1):
                    meta = getattr(doc, "metadata", {}) or {}
                    source = meta.get("source", "Unknown")
                    st.write(f"**{i}. {os.path.basename(source)}**")
                    st.write(f"   Path: `{source}`")
                    with st.container():
                        st.text(doc.page_content[:300] + "...")
                    st.divider()

        # Display SPARQL details if available
        if response.get("sparql_results"):
            with st.expander("🇨🇭 Swiss Legislation Details (Fedlex)", expanded=False):
                sparql_results = response.get("sparql_results", "")
                # Only show first 2000 characters to avoid overwhelming the UI
                if len(sparql_results) > 2000:
                    st.markdown(sparql_results[:2000])
                    st.info(f"... (showing first 2000 of {len(sparql_results)} characters)")
                    if st.button("Show Full Details"):
                        st.markdown(sparql_results)
                else:
                    st.markdown(sparql_results)

except Exception as e:
    st.error(f"An error occurred: {e}")
    with st.expander("Error Details"):
        st.exception(e)