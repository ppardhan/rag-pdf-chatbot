# ingest.py
from pdf_loader import extract_text_from_pdf
from chunker import chunk_text
from vector_store import get_chroma_collection, add_chunks_to_db
import os

def ingest_pdf(pdf_path: str):
    pdf_name = os.path.basename(pdf_path)
    
    print(f"📄 Extracting text from {pdf_name}...")
    text = extract_text_from_pdf(pdf_path)
    
    print(f"✂️  Chunking text...")
    chunks = chunk_text(text)
    
    print(f"🔢 Storing {len(chunks)} chunks in ChromaDB...")
    collection = get_chroma_collection()
    add_chunks_to_db(collection, chunks, pdf_name)

if __name__ == "__main__":
    pdf_folder = "./pdfs"
    print(f"Looking in: {os.path.abspath(pdf_folder)}")
    print(f"Files found: {os.listdir(pdf_folder)}")
    for file in os.listdir(pdf_folder):
        if file.lower().endswith(".pdf"):
            ingest_pdf(os.path.join(pdf_folder, file))