from fpdf import FPDF
import os
from datetime import datetime

REPORT_FOLDER = "data/reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)


def clean_for_pdf(text):
    if text is None:
        return ""

    replacements = {
        "•": "-",
        "●": "-",
        "▪": "-",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "→": "->",
        "✓": "OK",
        "✅": "OK",
        "\u00a0": " "
    }

    text = str(text)

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining unsupported characters
    text = text.encode("latin-1", errors="ignore").decode("latin-1")

    return text


def generate_pdf_report(
    file_name,
    pages,
    words,
    characters,
    question,
    answer,
    confidence,
    source_chunk,
    top_chunks
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI PDF Search & Extractive QA Report", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"File Name: {clean_for_pdf(file_name)}", ln=True)
    pdf.cell(0, 8, f"Pages: {pages}", ln=True)
    pdf.cell(0, 8, f"Words: {words}", ln=True)
    pdf.cell(0, 8, f"Characters: {characters}", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Question", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, clean_for_pdf(question))

    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Extracted Answer", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, clean_for_pdf(answer))
    pdf.cell(0, 8, f"Confidence Score: {round(confidence * 100, 2)}%", ln=True)

    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Source Context", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, clean_for_pdf(source_chunk[:2000]))

    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Top Retrieved Chunks", ln=True)

    pdf.set_font("Arial", "", 10)

    for i, item in enumerate(top_chunks, start=1):
        chunk = item["chunk"]
        distance = item["distance"]

        pdf.ln(3)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, f"Chunk {i} | Distance: {round(distance, 4)}", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, clean_for_pdf(chunk["text"][:1000]))

    report_path = os.path.join(REPORT_FOLDER, "qa_report.pdf")
    pdf.output(report_path)

    return report_path