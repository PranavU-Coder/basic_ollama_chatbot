#!/bin/bash

# start Ollama in background

ollama serve &

# waiting for Ollama to be ready

sleep 5

# pull required models

echo "Pulling nomic-embed-text..."
ollama pull nomic-embed-text

echo "Pulling llama3.2..."
ollama pull llama3.2

# start streamlit for website

streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0