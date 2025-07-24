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

# ✅ Manual Punkt tokenizer (bypasses broken `punkt_tab`)
punkt_params = PunktParameters()
punkt_tokenizer = PunktSentenceTokenizer(punkt_params)

# ✅ Persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="devops-rag")

# ✅ Embedder
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ✅ Sentence-aware chunking with overlap
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
            # Finalize current chunk
            chunks.append(" ".join(current_chunk))
            # Prepare overlap + new sentence
            overlap = " ".join(current_chunk).split()[-overlap_tokens:] if overlap_tokens > 0 else []
            current_chunk = [" ".join(overlap), sentence] if overlap else [sentence]
            current_length = sum(len(s.split()) for s in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# ✅ Add single doc to ChromaDB
def add_doc_to_chroma(text: str):
    chunks = sentence_token_chunks(text)
    if not chunks:
        return
    existing_ids = collection.get()["ids"]
    chunk_ids = [f"chunk_{len(existing_ids) + i}" for i in range(len(chunks))]
    embeddings = embedder.encode(chunks).tolist()
    collection.add(documents=chunks, ids=chunk_ids, embeddings=embeddings)

# ✅ Setup ChromaDB with all files in /data
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
            docs.extend(chunks)
            ids.extend([f"{fname}_chunk_{i}" for i in range(len(chunks))])

    if docs:
        embeddings = embedder.encode(docs).tolist()
        collection.add(documents=docs, ids=ids, embeddings=embeddings)
