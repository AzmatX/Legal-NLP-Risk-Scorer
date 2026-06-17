from pdf2image import convert_from_path
import pytesseract
import os


def extract_text_from_pdf(pdf_path):
    """
    Convert PDF pages into images and extract text using OCR
    """

    pages = convert_from_path(pdf_path)

    full_text = ""

    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page)

        full_text += f"\n--- Page {i+1} ---\n"
        full_text += text

    return full_text


if __name__ == "__main__":

    pdf_path = "data/sample_pdfs/contract.pdf"

    extracted_text = extract_text_from_pdf(pdf_path)

    print("OCR OUTPUT:")
    print("-" * 50)
    print(extracted_text)