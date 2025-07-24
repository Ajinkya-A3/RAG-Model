import requests
import chromadb
from sentence_transformers import SentenceTransformer
from config import OLLAMA_HOST

# ✅ Updated Chroma client (new API, no Settings)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="devops-rag")

# ✅ Load embedding model
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ✅ Query ChromaDB with vector and return top-K sentences
def query_chroma(prompt: str, top_k: int = 3):
    try:
        embedding = embedder.encode([prompt])[0].tolist()
        results = collection.query(query_embeddings=[embedding], n_results=top_k)
        documents = results.get("documents", [[]])[0]
        return documents if documents else []
    except Exception as e:
        raise RuntimeError(f"Chroma query failed: {str(e)}")

# ✅ Send query with context to Ollama
def call_ollama(prompt: str, context: str, model: str = "gemma:2b"):
    full_prompt = f"""
You are a helpful DevOps assistant. Use the following context to answer the question.

Context:
{context}

User: {prompt}

Answer:
""".strip()

    try:
        res = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": model,
            "prompt": full_prompt,
            "stream": False
        })
        res.raise_for_status()
        return res.json().get("response", "⚠️ No response received.")
    except Exception as e:
        raise RuntimeError(f"Ollama call failed: {str(e)}")
