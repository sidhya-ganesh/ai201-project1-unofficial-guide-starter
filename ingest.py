"""
ingest.py — Load and chunk UPenn course review documents.
Chunk size: 400 characters, overlap: 80 characters.
"""

import os
import re

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 100
CHUNK_OVERLAP = 20


def load_documents(directory: str) -> list[dict]:
    """Load all .txt files from the documents directory."""
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            cleaned = clean_text(raw_text)
            documents.append({
                "source": filename,
                "text": cleaned
            })
            print(f"Loaded: {filename} ({len(cleaned)} chars)")
    return documents


def clean_text(text: str) -> str:
    """Remove boilerplate and normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Split text into overlapping chunks of ~chunk_size characters."""
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            break_point = text.rfind(". ", start, end)
            if break_point != -1 and break_point > start + chunk_size // 2:
                end = break_point + 1
        else:
            end = len(text)

        chunk = text[start:end].strip()

        if len(chunk) > 20:
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": chunk_index
            })
            chunk_index += 1

        start = end - overlap

    return chunks


def build_chunks(directory: str = DOCUMENTS_DIR) -> list[dict]:
    """Full pipeline: load documents → clean → chunk."""
    documents = load_documents(directory)
    all_chunks = []

    for doc in documents:
        doc_chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(doc_chunks)
        print(f"  → {len(doc_chunks)} chunks from {doc['source']}")
        import gc
        gc.collect()

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print("\n--- 5 Sample Chunks ---")
    import random
    for chunk in random.sample(chunks, min(5, len(chunks))):
        print(f"\n[Source: {chunk['source']} | Chunk #{chunk['chunk_index']}]")
        print(chunk["text"])
        print("-" * 60)