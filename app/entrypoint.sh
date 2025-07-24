#!/bin/bash

# Download nltk data to local directory (once)
if [ ! -d "./nltk_data/tokenizers/punkt" ]; then
  echo "📥 Downloading NLTK 'punkt'..."
  python3 -m nltk.downloader punkt -d ./nltk_data
fi

# Start FastAPI app
echo "🚀 Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
