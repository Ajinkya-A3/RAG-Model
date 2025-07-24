
# 🧠 RAG API with ChromaDB + Sentence Transformers + Ollama

A FastAPI backend for a lightweight Retrieval-Augmented Generation (RAG) system using:

- 🔎 `sentence-transformers/all-mpnet-base-v2` for semantic embeddings
- 💾 `ChromaDB` as the local vector store
- 🤖 `Ollama` for LLM-based response generation
- ⚡ FastAPI endpoints for upload, search, and RAG queries

---

## ✅ Features

- 📁 Upload `.txt` files to chunk and embed into ChromaDB
- 🔍 Perform fast semantic search over vectorized data
- 💬 Get contextual answers using a local LLM with top-matching chunks
- 🚫 Skips duplicate chunks on upload to avoid redundancy
- 🩺 Includes liveness and readiness probes

---

## 🚀 Quickstart

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Run FastAPI server
```bash
uvicorn main:app --reload
```

### 3. Interact with API via Swagger UI
Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ✅ API Endpoints

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

## 👨‍💻 Author

Made with ❤️ by [Ajinkya A3](https://github.com/Ajinkya-A3)  
GitHub Repo: [RAG-Model](https://github.com/Ajinkya-A3/RAG-Model/blob/main/app/main.py)

---

## 📜 License

Licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)
