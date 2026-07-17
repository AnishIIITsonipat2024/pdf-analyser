# import pdfplumber


# def extract_pdf_text(pdf_path):
#     """
#     Extract text from a PDF.

#     Returns:
#         pages: Total page count
#         text: Complete document text
#         page_texts: List containing text for each page
#     """

#     full_text = ""
#     page_texts = []

#     with pdfplumber.open(pdf_path) as pdf:

#         total_pages = len(pdf.pages)

#         for page in pdf.pages:

#             text = page.extract_text() or ""

#             page_texts.append(text)

#             full_text += text + "\n"

#     return {
#         "pages": total_pages,
#         "text": full_text,
#         "page_texts": page_texts
#     }

import fitz  # PyMuPDF


def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)

    full_text = ""
    page_texts = []

    for page in doc:
        text = page.get_text("text")

        page_texts.append(text)
        full_text += text + "\n"

    return {
        "pages": len(doc),
        "text": full_text,
        "page_texts": page_texts
    }