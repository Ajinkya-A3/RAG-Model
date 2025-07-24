import os
from dotenv import load_dotenv

load_dotenv()

# Default URL for Ollama API (internal if in Docker, localhost otherwise)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
