# server.py
"""
Lightweight RAG PDF Chatbot Web Server
Zero extra dependencies required (uses Python standard library http.server).
Serves index.html and provides REST API for chatting, document management, and PDF ingestion.
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import mimetypes

# Set stdout to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

print("=" * 60, flush=True)
print("⏳ Initializing PDF Chatbot RAG Server...", flush=True)
print("   Loading ChromaDB & embedding models (please wait a moment)...", flush=True)
print("=" * 60, flush=True)

from chatbot import chat_with_sources
from ingest import ingest_pdf
from vector_store import get_chroma_collection

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

class RAGChatbotHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local testing/Live Server
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            html_file = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(html_file):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "index.html not found")
                return

        elif path == "/api/status":
            try:
                collection = get_chroma_collection()
                chunk_count = collection.count()
            except Exception as e:
                chunk_count = 0

            pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
            self.send_json({
                "status": "online",
                "chroma_chunks": chunk_count,
                "document_count": len(pdf_files),
                "documents": pdf_files
            })
            return

        elif path == "/api/documents":
            pdf_files = []
            if os.path.exists(PDF_DIR):
                for f in os.listdir(PDF_DIR):
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(PDF_DIR, f)
                        size_kb = round(os.path.getsize(full_path) / 1024, 1)
                        pdf_files.append({
                            "name": f,
                            "size_kb": size_kb
                        })
            self.send_json({"documents": pdf_files})
            return

        # Fallback to default file serving (CSS, JS, assets if any)
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                query = payload.get("query", "").strip()
                n_results = int(payload.get("n_results", 5))

                if not query:
                    self.send_json({"error": "Query cannot be empty"}, status=400)
                    return

                print(f"[Server] Processing query: {query}")
                result = chat_with_sources(query, n_results=n_results)
                self.send_json({
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", [])
                })
            except Exception as e:
                print(f"[Server Error] {e}")
                self.send_json({"error": str(e)}, status=500)
            return

        elif path == "/api/upload":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self.send_json({"error": "Content-Type must be multipart/form-data"}, status=400)
                return

            try:
                content_length = int(self.headers.get("Content-Length", 0))
                boundary = content_type.split("boundary=")[1].encode()
                raw_data = self.rfile.read(content_length)

                # Parse multipart body
                parts = raw_data.split(b"--" + boundary)
                uploaded_filename = None

                for part in parts:
                    if b'filename="' in part:
                        headers_part, file_data = part.split(b"\r\n\r\n", 1)
                        file_data = file_data.rstrip(b"\r\n")
                        
                        header_lines = headers_part.decode("utf-8", errors="ignore").split("\r\n")
                        for line in header_lines:
                            if "filename=" in line:
                                fn = line.split('filename="')[1].split('"')[0]
                                uploaded_filename = os.path.basename(fn)
                                break
                                
                        if uploaded_filename and uploaded_filename.lower().endswith(".pdf"):
                            save_path = os.path.join(PDF_DIR, uploaded_filename)
                            with open(save_path, "wb") as f:
                                f.write(file_data)
                            
                            # Ingest into ChromaDB
                            print(f"[Server] Ingesting uploaded PDF: {uploaded_filename}")
                            ingest_pdf(save_path)
                            break

                if uploaded_filename:
                    collection = get_chroma_collection()
                    self.send_json({
                        "success": True,
                        "filename": uploaded_filename,
                        "total_chunks": collection.count()
                    })
                else:
                    self.send_json({"error": "No valid PDF file found in upload"}, status=400)
            except Exception as e:
                print(f"[Server Upload Error] {e}")
                self.send_json({"error": str(e)}, status=500)
            return

        elif path == "/api/reingest":
            try:
                count = 0
                for f in os.listdir(PDF_DIR):
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(PDF_DIR, f)
                        ingest_pdf(full_path)
                        count += 1
                collection = get_chroma_collection()
                self.send_json({
                    "success": True,
                    "ingested_files": count,
                    "total_chunks": collection.count()
                })
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        self.send_error(404, "Endpoint not found")

def run(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, RAGChatbotHandler)
    print("=" * 60, flush=True)
    print(f"🚀 PDF Chatbot Web Server running at: http://localhost:{port}", flush=True)
    print(f"📁 Serving index.html and connecting to RAG pipeline", flush=True)
    print("=" * 60, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...", flush=True)
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port)
