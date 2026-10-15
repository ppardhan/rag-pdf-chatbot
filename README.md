# 📚 PDFMind RAG Chatbot

An intelligent document retrieval-augmented generation (RAG) chatbot assistant powered by **ChromaDB**, **Sentence Transformers**, and **Google Gemini**.

---

## 🚀 Features

- **Modern Glassmorphic Web UI**: Curated dark interface with Plus Jakarta Sans typography, micro-animations, and responsive layout.
- **Context Citations Accordion**: View the exact chunks, source document, chunk index, and similarity scores retrieved from ChromaDB.
- **Drag-and-Drop PDF Ingestion**: Upload new PDFs directly from your browser; text is automatically extracted with `pypdf`, chunked, and embedded into ChromaDB.
- **Text-to-Speech (Voice Readout)**: Listen to answers directly in the browser via Web Speech API.
- **Conversation Export**: Export chat history to formatted Markdown.
- **Interactive Offline Mode**: If opened directly without a running backend, it switches to an interactive preview with helpful instructions.

---

## 🏃‍♂️ Quick Start

### 1. Configure API Key
Ensure your `.env` file has your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start the Server
Run the built-in server (uses Python's standard library, no extra web frameworks required):

```powershell
.\venv\Scripts\python.exe server.py
```

### 3. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** in any browser.

---

## 📁 Project Structure

| File | Description |
|---|---|
| [`index.html`](./index.html) | Modern frontend UI with document manager, chat stream, and citation drawer |
| [`server.py`](./server.py) | Python HTTP server serving the frontend and REST API (`/api/chat`, `/api/upload`, `/api/status`) |
| [`chatbot.py`](./chatbot.py) | RAG query orchestration calling `retriever.py` and `llm.py` |
| [`retriever.py`](./retriever.py) | ChromaDB vector search returning top context chunks with metadata |
| [`ingest.py`](./ingest.py) | PDF extraction, text chunking, and ChromaDB vector persistence |
| [`chunker.py`](./chunker.py) | Text chunker with sentence-boundary awareness and overlap |
| [`vector_store.py`](./vector_store.py) | ChromaDB persistent collection configuration (`all-MiniLM-L6-v2`) |
| [`llm.py`](./llm.py) | Gemini LLM integration for grounded answers based on context |
