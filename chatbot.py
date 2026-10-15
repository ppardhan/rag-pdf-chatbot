from retriever import retrieve_context, retrieve_context_with_metadata
from llm import generate_answer

def chat(query: str) -> str:
    print(f"\n[?] Query: {query}")
    
    # Retrieve relevant chunks
    context_chunks = retrieve_context(query, n_results=5)
    
    # Generate answer
    answer = generate_answer(query, context_chunks)
    
    return answer

def chat_with_sources(query: str, n_results: int = 5) -> dict:
    docs, sources = retrieve_context_with_metadata(query, n_results=n_results)
    answer = generate_answer(query, docs)
    return {
        "answer": answer,
        "sources": sources
    }

# Simple CLI loop
if __name__ == "__main__":
    print("🤖 PDF Chatbot ready! Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        if not user_input:
            continue
        response = chat(user_input)
        print(f"\nBot: {response}\n")