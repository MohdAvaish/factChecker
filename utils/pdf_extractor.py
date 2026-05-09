"""
pdf_extractor.py – Extract raw text from uploaded PDF files using PyMuPDF.
"""

import fitz  # PyMuPDF
from typing import Union
import io


def extract_text_from_pdf(uploaded_file: Union[bytes, "streamlit.runtime.uploaded_file_manager.UploadedFile"]) -> str:
    """
    Extract all text from a PDF file object.

    Args:
        uploaded_file: A Streamlit UploadedFile or raw bytes object.

    Returns:
        A single string containing all extracted text from the PDF.

    Raises:
        ValueError: If the file cannot be opened or read.
        RuntimeError: If PyMuPDF encounters an error.
    """
    try:
        file_bytes = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        pages_text: list[str] = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text.strip():
                pages_text.append(text.strip())

        doc.close()
        return "\n\n".join(pages_text)

    except fitz.FileDataError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}") from e
