from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chroma_setup import add_doc_to_chroma, setup_chroma, collection, embedder
from rag import query_chroma, call_ollama
import os

app = FastAPI()

# ✅ Allow all or specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" for development or specify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    setup_chroma()
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize ChromaDB: {str(e)}")

class Query(BaseModel):
    prompt: str

@app.get("/")
def liveness_probe():
    return {"status": "alive"}

@app.get("/ready")
def readiness_probe():
    try:
        _ = collection.count()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ChromaDB not ready: {str(e)}")

@app.post("/upload")
async def upload_txt(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        text = content.decode("utf-8")

        os.makedirs("./data", exist_ok=True)
        file_path = os.path.join("./data", file.filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        result = add_doc_to_chroma(text, file.filename)
        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Upload failed: {str(e)}"})


@app.post("/rag")
def rag(query: Query):
    try:
        if not query.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is empty.")
        context_sentences = query_chroma(query.prompt)
        if not context_sentences:
            return JSONResponse(status_code=404, content={"error": "No context found."})
        context = "\n".join(context_sentences)
        answer = call_ollama(query.prompt, context)
        return {"context": context, "answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"RAG failed: {str(e)}"})

@app.get("/records")
def list_all_records():
    try:
        data = collection.get()
        return {
            "count": len(data["documents"]),
            "ids": data["ids"],
            "documents": data["documents"]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to fetch records: {str(e)}"})

@app.post("/search")
def semantic_search(query: Query):
    try:
        if not query.prompt.strip():
            raise HTTPException(status_code=400, detail="Query is empty.")
        embedding = embedder.encode([query.prompt])[0].tolist()
        results = collection.query(query_embeddings=[embedding], n_results=5)
        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        matches = [
            {"document": doc, "id": doc_id, "distance": dist}
            for doc, doc_id, dist in zip(documents, ids, distances)
        ]
        return {"query": query.prompt, "matches": matches}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Search failed: {str(e)}"})
