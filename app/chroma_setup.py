import os

# ✅ Set HuggingFace model cache directory before any imports
os.environ["HF_HOME"] = os.path.abspath("./transformer_model")

import nltk
from typing import List
import chromadb
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from sentence_transformers import SentenceTransformer

# ✅ Custom nltk_data path
nltk_data_path = os.path.abspath("./nltk_data")
nltk.data.path.insert(0, nltk_data_path)

# ✅ Ensure punkt is downloaded locally
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)

# ✅ Manual Punkt tokenizer
punkt_params = PunktParameters()
punkt_tokenizer = PunktSentenceTokenizer(punkt_params)

# ✅ Persistent ChromaDB client
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=chromadb.Settings(
        chroma_db_impl="duckdb+parquet",
        anonymized_telemetry=False,
        is_persistent=True,
        allow_reset=True,
        index_type="faiss"  #  Enables FAISS indexing
    )
)

collection = client.get_or_create_collection(name="devops-rag")

# ✅ SentenceTransformer embedder
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ✅ Sentence-aware chunking with token overlap
def sentence_token_chunks(text: str, max_tokens=100, overlap_tokens=20) -> List[str]:
    sentences = punkt_tokenizer.tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        token_count = len(sentence.split())
        if current_length + token_count <= max_tokens:
            current_chunk.append(sentence)
            current_length += token_count
        else:
            chunks.append(" ".join(current_chunk))
            overlap = " ".join(current_chunk).split()[-overlap_tokens:] if overlap_tokens > 0 else []
            current_chunk = [" ".join(overlap), sentence] if overlap else [sentence]
            current_length = sum(len(s.split()) for s in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# ✅ Add a single document to ChromaDB with proper filename-based chunk IDs
def add_doc_to_chroma(text: str, filename: str = "uploaded.txt") -> dict:
    chunks = sentence_token_chunks(text)
    if not chunks:
        return {"status": "skipped", "reason": "No valid chunks found in file."}

    base_name = os.path.splitext(os.path.basename(filename))[0]

    # Get existing docs for deduplication
    existing_docs = set(collection.get()["documents"])

    # Deduplicate by string match
    unique_chunks = [chunk for chunk in chunks if chunk not in existing_docs]
    added_count = len(unique_chunks)

    if added_count == 0:
        return {
            "status": "skipped",
            "reason": "All chunks already exist in the DataBase.",
            "total_chunks": len(chunks),
            "added_chunks": 0
        }

    existing_ids = collection.get()["ids"]
    start_idx = len(existing_ids)
    chunk_ids = [f"{base_name}_chunk_{i}" for i in range(start_idx, start_idx + added_count)]

    embeddings = embedder.encode(unique_chunks).tolist()
    collection.add(documents=unique_chunks, ids=chunk_ids, embeddings=embeddings)

    return {
        "status": "added",
        "filename": filename,
        "total_chunks": len(chunks),
        "added_chunks": added_count
    }


# ✅ Load all .txt files in ./data into ChromaDB
def setup_chroma():
    os.makedirs("./data", exist_ok=True)
    docs, ids = [], []

    for fname in os.listdir("./data"):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join("./data", fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            chunks = sentence_token_chunks(content)
            base_name = os.path.splitext(fname)[0]
            docs.extend(chunks)
            ids.extend([f"{base_name}_chunk_{i}" for i in range(len(chunks))])

    if docs:
        embeddings = embedder.encode(docs).tolist()
        collection.add(documents=docs, ids=ids, embeddings=embeddings)
