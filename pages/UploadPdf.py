import os
import streamlit as st

from backend.pdf_parser import extract_pdf_text
from backend.text_cleaner import clean_text
from backend.chunker import create_chunks
from backend.embedding import generate_embeddings, generate_query_embedding
from backend.vector_store import create_faiss_index, search_similar_chunks
from backend.ex_qa import get_best_answer
from backend.report_generator import generate_pdf_report

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="PDF-Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            color: #1E3A8A;
            margin-bottom: 0;
        }

        .subtitle {
            font-size: 18px;
            color: #475569;
            margin-bottom: 30px;
        }

        .info-card {
            padding: 20px;
            border-radius: 14px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            margin-bottom: 20px;
        }

        .answer-card {
            padding: 22px;
            border-radius: 14px;
            background-color: #ECFDF5;
            border: 1px solid #86EFAC;
            margin-top: 15px;
        }

        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #0F172A;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)



st.markdown('<p class="main-title">PDF-Analyzer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">AI PDF Search & Extractive Question Answering System</p>',
    unsafe_allow_html=True
)



uploaded_file = st.file_uploader(
    "📤 Upload your PDF",
    type=["pdf"],
    help="Only PDF files are supported"
)
if uploaded_file is None:
    for key in [
        "raw_text",
        "cleaned_text",
        "chunks",
        "index",
        "pages",
        "file_name",
        "last_question",
        "last_results",
        "last_answer"
    ]:
        st.session_state.pop(key, None)
if uploaded_file:
    st.success("✅ PDF uploaded successfully")

    file_col1, file_col2 = st.columns(2)

    with file_col1:
        st.metric("📄 File Name", uploaded_file.name)

    with file_col2:
        st.metric("📦 File Size", f"{round(uploaded_file.size / 1024, 2)} KB")

    process_btn = st.button(
        "Process PDF",
        use_container_width=True
    )

    if process_btn:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress = st.progress(0)

        with st.spinner("Extracting text from PDF..."):
            result = extract_pdf_text(file_path)
            progress.progress(20)

        raw_text = result["text"]

        with st.spinner("Cleaning extracted text..."):
            cleaned_text = clean_text(raw_text)
            progress.progress(40)

        with st.spinner("Creating chunks with overlap..."):
            chunks = create_chunks(
                cleaned_text,
                chunk_size=250,
                overlap=80
            )
            progress.progress(60)

        with st.spinner("Generating embeddings..."):
            chunks = generate_embeddings(chunks)
            progress.progress(80)

        with st.spinner("Creating FAISS vector index..."):
            index = create_faiss_index(chunks)
            progress.progress(100)

        st.session_state["raw_text"] = raw_text
        st.session_state["cleaned_text"] = cleaned_text
        st.session_state["chunks"] = chunks
        st.session_state["index"] = index
        st.session_state["pages"] = result["pages"]
        st.session_state["file_name"] = uploaded_file.name

        st.success("✅ PDF processed successfully!")

if "chunks" in st.session_state and "index" in st.session_state:
    cleaned_text = st.session_state["cleaned_text"]
    chunks = st.session_state["chunks"]
    index = st.session_state["index"]
    pages = st.session_state["pages"]
    file_name = st.session_state.get("file_name", "Uploaded PDF")

    words = len(cleaned_text.split())
    characters = len(cleaned_text)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Overview",
            "Chunks",
            "Ask Question",
            "Report"
        ]
    )

    with tab1:
        st.markdown('<p class="section-title">📊 Document Overview</p>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("📄 Pages", pages)

        with c2:
            st.metric("📝 Words", words)

        with c3:
            st.metric("🔤 Characters", characters)

        with c4:
            st.metric("📦 Chunks", len(chunks))

        st.subheader("✨ Cleaned Text Preview")

        st.text_area(
            "Preview",
            value=cleaned_text[:2500],
            height=300
        )

        st.subheader("🧠 Embedding Info")

        e1, e2, e3 = st.columns(3)

        with e1:
            st.metric("Model", "MiniLM-L6-v2")

        with e2:
            st.metric("Dimension", len(chunks[0]["embedding"]))

        with e3:
            st.metric("Total Vectors", len(chunks))

    with tab2:
        st.markdown('<p class="section-title">📦 Chunk Preview</p>', unsafe_allow_html=True)

        st.info("Showing first 5 chunks only.")

        for chunk in chunks[:5]:
            with st.expander(f"Chunk {chunk['id']} | {chunk['word_count']} words"):
                st.write(chunk["text"])

    with tab3:
        st.markdown('<p class="section-title">🔎 Ask a Question</p>', unsafe_allow_html=True)

        question = st.text_input(
            "Enter your question",
            placeholder="Example: What architecture does BERT use?"
        )

        search_btn = st.button(
            "🔍 Search Answer",
            use_container_width=True
        )

        if search_btn:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Searching similar chunks..."):
                    question_embedding = generate_query_embedding(question)

                    results = search_similar_chunks(
                        question_embedding,
                        index,
                        chunks,
                        top_k=10
                    )

                with st.spinner("Running extractive QA..."):
                    best_answer = get_best_answer(
                        question=question,
                        retrieved_chunks=results,
                        min_score=0.35
                    )

                st.session_state["last_question"] = question
                st.session_state["last_results"] = results
                st.session_state["last_answer"] = best_answer

                st.markdown(
                    f"""
                    <div class="answer-card">
                        <h3>✅ Extracted Answer</h3>
                        <h2>{best_answer["answer"]}</h2>
                        <p><b>Confidence:</b> {round(best_answer["score"] * 100, 2)}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if best_answer["chunk"]:
                    st.caption(f"Source Chunk ID: {best_answer['chunk']['id']}")

                    with st.expander("📖 Source Context"):
                        st.write(best_answer["chunk"]["text"])

                st.subheader("🔎 Top Retrieved Chunks")

                for i, item in enumerate(results, start=1):
                    chunk = item["chunk"]
                    distance = item["distance"]

                    with st.expander(f"Result {i} | Distance: {distance:.4f}"):
                        st.write(chunk["text"])
                        st.caption(
                            f"Chunk ID: {chunk['id']} | Words: {chunk['word_count']}"
                        )

    with tab4:
        st.markdown('<p class="section-title">📥 Download PDF Report</p>', unsafe_allow_html=True)

        if "last_answer" not in st.session_state:
            st.info("Ask a question first to generate a report.")
        else:
            best_answer = st.session_state["last_answer"]
            results = st.session_state["last_results"]
            question = st.session_state["last_question"]

            source_text = ""

            if best_answer["chunk"]:
                source_text = best_answer["chunk"]["text"]

            report_path = generate_pdf_report(
                file_name=file_name,
                pages=pages,
                words=words,
                characters=characters,
                question=question,
                answer=best_answer["answer"],
                confidence=best_answer["score"],
                source_chunk=source_text,
                top_chunks=results
            )

            with open(report_path, "rb") as pdf_file:
                st.download_button(
                    label="⬇️ Download QA Report",
                    data=pdf_file,
                    file_name="qa_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
else:
    st.info("Upload and process a PDF to start.")