# llm.py
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_answer(query: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""You are a helpful assistant. Answer the user's question 
based ONLY on the provided context. If the answer is not in the context, 
say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer:"""
    
    model = genai.GenerativeModel("gemini-3.7-flash")  # or gemini-1.5-pro
    response = model.generate_content(prompt)
    
    return response.text