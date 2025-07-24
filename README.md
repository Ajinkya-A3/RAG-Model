# 🔍 FastAPI Semantic Search & RAG Backend

This project provides a semantic search and Retrieval-Augmented Generation (RAG) backend using:

- **FastAPI** for APIs  
- **ChromaDB** as the vector store  
- **SentenceTransformers (all-mpnet-base-v2)** for embeddings  
- **Ollama** as the local LLM runtime  
- **Punkt sentence chunking** with token overlap  
- **Deduplication logic** to prevent redundant chunk storage

---

## 📦 Features

- ✅ Upload `.txt` files for semantic indexing
- ✅ Automatic sentence-aware chunking
- ✅ Duplicate chunk prevention
- ✅ Semantic vector search using sentence embeddings
- ✅ RAG-style response generation using local LLM (Ollama)
- ✅ FastAPI-based REST endpoints

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/Ajinkya-A3/RAG-Model.git
cd RAG-Model
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> Make sure you have `chromadb`, `fastapi`, `uvicorn`, `nltk`, and `sentence-transformers` installed.

### 4. Download Punkt tokenizer for NLTK

This is handled automatically by the app. You can also manually run:

```bash
python -m nltk.downloader punkt
```

---

## 🚀 Start the Backend

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

---

## 🧪 API Endpoints

### 🟢 `GET /`
Liveness probe.  
**Use:** Check if the app is running.  
**Response:** `{ "status": "alive" }`

---

### 🟢 `GET /ready`
Readiness probe.  
**Use:** Confirms ChromaDB is reachable and initialized.  
**Response:** `{ "status": "ready" }`

---

### 📄 `POST /upload`
Upload a `.txt` file. Automatically chunks the file by sentences and stores the vectors in ChromaDB, avoiding duplicates.

**Request:**  
Content-Type: `multipart/form-data`  
Field: `file` = `.txt` file

**Response (Example):**
```json
{
  "status": "uploaded",
  "filename": "devops.txt",
  "added_chunks": 17,
  "skipped_duplicates": 3
}
```

---

### 🔍 `POST /search`
Semantic search on uploaded data.

**Request Body:**
```json
{
  "prompt": "How do I set environment variables in Docker?"
}
```

**Response:**
```json
{
  "query": "How do I set environment variables in Docker?",
  "matches": [
    {
      "document": "...matched content...",
      "id": "docker_guide_chunk_2",
      "distance": 0.13
    }
  ]
}
```

---

### 💬 `POST /rag`
Retrieves relevant chunks and passes them to a local LLM (Ollama) for a natural language response.

**Request Body:**
```json
{
  "prompt": "Explain how Kubernetes probes work"
}
```

**Response:**
```json
{
  "context": "...top matching chunks...",
  "answer": "Kubernetes uses liveness and readiness probes to determine..."
}
```

---

### 📚 `GET /records`
Returns all stored ChromaDB records.

**Response:**
```json
{
  "count": 42,
  "ids": ["devops_chunk_0", "devops_chunk_1", "..."],
  "documents": ["First chunk", "Second chunk", "..."]
}
```

---

## 📁 Project Structure

```
.
├── main.py               # FastAPI app with all endpoints
├── chroma_setup.py       # Chunking, embedding, and ChromaDB logic
├── rag.py                # RAG + Ollama interaction
├── data/                 # Uploaded text files
├── chroma_db/            # Persistent ChromaDB storage
├── nltk_data/            # NLTK punkt tokenizer
├── transformer_model/    # HuggingFace model cache
```

---

## 🧪 Test with cURL

**Upload a file:**
```bash
curl -X POST "http://127.0.0.1:8000/upload" -F "file=@yourfile.txt"
```

**Query with search:**
```bash
curl -X POST "http://127.0.0.1:8000/search" -H "Content-Type: application/json" -d '{"prompt": "What is a Kubernetes probe?"}'
```

---

## 👤 Author

[Ajinkya A3](https://github.com/Ajinkya-A3)

GitHub Repo: [RAG-Model](https://github.com/Ajinkya-A3/RAG-Model/blob/main/app/main.py)

---

## ⚖️ License

```
Apache License 2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
```