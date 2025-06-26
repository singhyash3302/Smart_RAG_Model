import io
import requests
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Function: Extract all text from uploaded PDFs
def extract_text_from_pdfs(pdf_files):
    all_text = ""
    for pdf in pdf_files:
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf.read()))
            text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            all_text += text
        except Exception as e:
            st.error(f"Error reading PDF {pdf.name}: {e}")
    return all_text

# Function: Split large text into chunks
def split_text_into_chunks(text, chunk_size=1000, overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

# Function: Create FAISS vector store
def create_vector_store(chunks, embedding_model):
    try:
        store = FAISS.from_texts(chunks, embedding=embedding_model)
        store.save_local("faiss_index")
        return store
    except Exception as e:
        st.error(f"FAISS creation failed: {e}")
        return None

# Function: Query your FastAPI app
def query_answering(query, endpoint, context):
    payload = {"query": query, "context": context}
    try:
        response = requests.post(f"http://127.0.0.1:8000/{endpoint}/", json=payload)
        response.raise_for_status()
        return response.json().get("message", "No response received.")
    except requests.RequestException as e:
        st.error(f"API call failed: {e}")
        return None


# Streamlit app
def main():
    st.title("📄 PDF Question Answering App")

    uploaded_pdfs = st.file_uploader("Upload PDF Files", type="pdf", accept_multiple_files=True)

    if uploaded_pdfs and st.button("🔄 Process PDFs"):
        raw_text = extract_text_from_pdfs(uploaded_pdfs)
        if not raw_text:
            st.error("No text could be extracted.")
            return

        text_chunks = split_text_into_chunks(raw_text)
        embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")
        vector_store = create_vector_store(text_chunks, embeddings_model)

        if vector_store:
            st.session_state['vector_store'] = vector_store
            st.session_state['raw_chunks'] = text_chunks
            st.success("✅ Vector store created successfully!")

    if 'vector_store' in st.session_state:
        query = st.text_input("💬 Ask a question about your PDF")

        if query:
            docs = st.session_state['vector_store'].similarity_search(query, k=5)
            context = "\n".join([doc.page_content for doc in docs])

            if st.button("🤖 AI Answer"):
                result = query_answering(query, "AI_Answer", context)
                if result:
                    st.write("🧠 Answer:", result)

            if st.button("🧠 Smart AI Agent"):
                result = query_answering(query, "Smart_AI_Answer", context)
                if result:
                    st.write("🧠 Answer:", result)

if __name__ == "__main__":
    main()
