# retriever.py
from vector_store import get_chroma_collection

def retrieve_context_with_metadata(query: str, n_results=5):
    collection = get_chroma_collection()
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if "distances" in results and results["distances"] else []
    
    chunks = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        dist = distances[i] if i < len(distances) else None
        chunks.append({
            "text": doc,
            "source": meta.get("source", "Unknown PDF"),
            "chunk_index": meta.get("chunk_index", i),
            "distance": round(float(dist), 4) if dist is not None else None
        })
    
    try:
        print(f"\n[+] Top {n_results} relevant chunks retrieved:")
        for i, chunk in enumerate(chunks):
            print(f"  [{i+1}] Source: {chunk['source']} | Chunk #{chunk['chunk_index']}")
    except Exception:
        pass
        
    return docs, chunks

def retrieve_context(query: str, n_results=5) -> list[str]:
    docs, _ = retrieve_context_with_metadata(query, n_results=n_results)
    return docs