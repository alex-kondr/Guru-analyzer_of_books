from src.model.model import load_pdf_file, qa_generate


async def load_file(file):
    return load_pdf_file(file)
