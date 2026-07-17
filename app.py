import streamlit as st

st.set_page_config(
    page_title="IntelliPDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 AI-PDF-Analyzer")
st.subheader("AI PDF Search & Extractive Question Answering")

st.markdown(
    """
    This application lets you upload a PDF, extract text, clean it, create chunks,
    generate embeddings, search semantically using FAISS, and get exact answers
    using an extractive QA model.

    ### Pipeline

    1. Upload PDF  
    2. Extract text  
    3. Clean text  
    4. Chunk with overlap  
    5. Generate embeddings  
    6. Store in FAISS  
    7. Search similar chunks  
    8. Extract exact answer  
    9. Download PDF report  
    """
)

st.info("Go to the Upload PDF page from the sidebar to start.")