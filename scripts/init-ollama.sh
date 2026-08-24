#!/bin/bash

set -e

echo "📥 Initializing Ollama models..."

# Wait for Ollama to be ready
until curl -f http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Waiting for Ollama..."
    sleep 2
done

echo "✅ Ollama is ready"

# Pull model
docker-compose exec -T ollama ollama pull mistral:7b

echo "✨ Models ready!"