import os
from dotenv import load_dotenv

# Load environment variables from `.env` file if it exists
load_dotenv()

# Ollama API configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ChromaDB HTTP Client configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))  # Default to port 8000
