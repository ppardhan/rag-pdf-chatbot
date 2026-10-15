# vector_store.py
import chromadb
from chromadb.utils import embedding_functions

# Use a local embedding model (free) or OpenAI
EMBED_MODEL = "all-MiniLM-L6-v2"  # fast & free via sentence-transformers

def get_chroma_collection(collection_name="pdf_rag"):
    client = chromadb.PersistentClient(path="./chroma_db")  # persists to disk
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def add_chunks_to_db(collection, chunks: list[str], pdf_name: str):
    ids = [f"{pdf_name}chunk{i}" for i in range(len(chunks))]
    metadatas = [{"source": pdf_name, "chunk_index": i} for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Added {len(chunks)} chunks from '{pdf_name}' to ChromaDB")