import fitz

def extract_text_from_pdf(filepath):
    document = fitz.open(filepath)

    text = " "

    for page_number, page in enumerate(document, start=1):
        page_text = page.get_text()
        text += f"\n\n--- Page {page_number} ---\n\n"
        text += page_text
    document.close()
    return text