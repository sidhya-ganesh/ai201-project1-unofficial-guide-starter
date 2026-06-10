"""
query.py — Retrieve relevant chunks and generate grounded answers using Groq.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "upenn_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 4

_embedding_model = None
_collection = None
_groq_client = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(MODEL_NAME)
    return _embedding_model


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path="./chroma_db")
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """Embed the query and retrieve top-k most similar chunks."""
    model = get_embedding_model()
    collection = get_collection()

    query_embedding = model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })

    return chunks


def generate(query: str, chunks: list[dict]) -> str:
    """Generate a grounded answer using only the retrieved chunks."""
    client = get_groq_client()

    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[Document {i+1}: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    system_prompt = """You are the Unofficial Penn Guide — a helpful assistant that answers questions about UPenn courses and professors using only the student reviews provided to you.

RULES:
1. Answer ONLY using information from the provided documents. Do not use any outside knowledge.
2. If the documents do not contain enough information to answer the question, say exactly: "I don't have enough information on that in my documents."
3. Always cite which document(s) your answer comes from, using the format: (Source: filename).
4. Be specific and direct. Quote or closely paraphrase student reviews when relevant.
5. Never make up information or fill gaps with general knowledge."""

    user_message = f"""Student question: {query}

Retrieved documents:
{context}

Answer the question using only the information above. Cite your sources."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=600,
        temperature=0.2
    )

    return response.choices[0].message.content


def ask(query: str) -> dict:
    """Full pipeline: retrieve chunks → generate grounded answer."""
    chunks = retrieve(query)
    answer = generate(query, chunks)
    sources = list(set(c["source"] for c in chunks))
    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


if __name__ == "__main__":
    test_queries = [
        "What do students say about Professor Ghrist's exams?",
        "Is there a curve in CIS 1200?",
        "How useful are office hours at Penn?"
    ]
    for q in test_queries:
        print(f"\nQ: {q}")
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print(f"Top chunk distance: {result['chunks'][0]['distance']:.3f}")
        print("=" * 60)