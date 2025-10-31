import os
import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

YOUR_OPENAI_API_KEY = ["OPEN_API_KEY"]

if not YOUR_OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set it as an environment variable or Streamlit secret.")
    st.stop()

DB_FOLDER = "vector_db_data"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

LLM_MODEL = "gpt-5"


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
def build_rag_chain(_vector_db, api_key, k=4, model=LLM_MODEL):
    llm = ChatOpenAI(model=model, openai_api_key=api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template("""You are an assistant for pro bono lawyers at UNHCR. Your job is to 
    assist the pro bono lawyer on giving legal advices to refugees by looking at what immediate rights are possible 
    for the refugee case based on the documents you have, what are the laws/regulations that could complicate the situation 
    and try to find a solution to it, and also search restrictions or procedures that could delay or streamline the process of the case.
    Answer the lawyer's question *only* using the provided legal documents. 

        - Be clear, accurate, concise; use bullet points when helpful. - If the answer is not in the documents, 
        first look at the documents from all the other countries and redirect them to another country if such a case 
        is possible. - Do NOT use outside knowledge.

        Lasty, format your answer in a conversational way that sounds human-generated as if you're a lawyer as well. 
        Be precise and structure your response in a clear manner.

        PROVIDED DOCUMENTS (CONTEXT):
        <context>
        {context}
        </context>

        LAWYER'S QUESTION:
        {input}

        YOUR ANSWER:
        """)

    retriever = _vector_db.as_retriever(search_kwargs={"k": k})

    def format_docs(docs):
        return "\n\n---\n\n".join(d.page_content for d in docs)

    retrieve_stage = RunnableParallel(
        docs=retriever,
        question=RunnablePassthrough()
    )

    llm_chain = (
            {"input": lambda x: x["question"], "context": lambda x: format_docs(x["docs"])}
            | prompt
            | llm
            | StrOutputParser()
    )

    final_chain = retrieve_stage | {
        "answer": llm_chain
        # "context": lambda x: x["docs"],
    }
    return final_chain


st.title("⚖️ UNHCR Pro Bono Legal Assistant")
st.write("Ask me anything!")

try:
    # Load models and build chain
    vector_db = load_all_models()
    chain = build_rag_chain(vector_db, YOUR_OPENAI_API_KEY, k=4, model=LLM_MODEL)

    # Get user input
    user_question = st.text_area("Your Question:", height=150)

    if user_question:
        # Show a loading spinner while processing
        with st.spinner("Searching documents and generating answer..."):
            response = chain.invoke(user_question)

            # Display the answer
            st.subheader("Answer")
            st.write(response.get("answer", "No answer found."))

            # # Display the sources
            # st.subheader("Sources Used")
            # docs = response.get("context", [])
            # if not docs:
            #     st.write("No sources returned by the retriever.")
            # else:
            #     for i, doc in enumerate(docs, start=1):
            #         meta = getattr(doc, "metadata", {}) or {}
            #         source = meta.get("source") or "Unknown"
            #         with st.expander(f"Source {i}: {os.path.basename(source)}"):
            #             st.write(f"**Path:** {source}")
            #             # Display a snippet of the content
            #             st.write(f"**Content Snippet:**\n{doc.page_content[:300]}...")

except Exception as e:
    st.error(f"An error occurred: {e}")
    print(f"\n--- AN ERROR OCCURRED ---")
    print(e)