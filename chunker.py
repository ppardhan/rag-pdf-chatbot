# chunker.py
def chunk_text(text: str, chunk_size=500, chunk_overlap=50) -> list[str]:
    # Clean and normalize text
    text = " ".join(text.split())
    text_len = len(text)
    
    # If text is smaller than chunk_size, return as single chunk
    if text_len <= chunk_size:
        return [text.strip()]
    
    chunks = []
    start = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < text_len:
            last_period = chunk.rfind(".")
            last_space = chunk.rfind(" ")
            break_point = last_period if last_period > chunk_size // 2 else last_space

            if break_point > 0:
                end = start + break_point + 1
                chunk = text[start:end]

        stripped = chunk.strip()
        if stripped:
            chunks.append(stripped)

        # Advance start — guaranteed forward progress
        next_start = end - chunk_overlap
        if next_start <= start:
            next_start = end  # ← skip overlap if it causes stall
        start = next_start

        # Safety break — should never hit this
        if len(chunks) > 10000:
            print("⚠️ Chunk limit reached, stopping early")
            break

    return chunks