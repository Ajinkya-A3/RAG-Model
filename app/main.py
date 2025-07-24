from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from chroma_setup import add_doc_to_chroma, setup_chroma, collection
from rag import query_chroma, call_ollama
import os

app = FastAPI()

try:
    setup_chroma()
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize ChromaDB: {str(e)}")

class Query(BaseModel):
    prompt: str

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
        add_doc_to_chroma(text)
        return {"status": "uploaded", "filename": file.filename}
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
