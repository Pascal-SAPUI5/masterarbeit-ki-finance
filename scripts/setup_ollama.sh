#!/bin/bash
# Setup script for Ollama with phi3:mini model

set -e

echo "🚀 Setting up Ollama for Masterarbeit..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Ollama service
echo "📦 Starting Ollama container..."
docker compose up -d ollama

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if docker exec masterarbeit-ollama curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

# Pull phi3:mini model
echo "📥 Pulling phi3:mini model..."
docker exec masterarbeit-ollama ollama pull phi3:mini

# Verify model is loaded
echo "🔍 Verifying model..."
if docker exec masterarbeit-ollama ollama list | grep -q "phi3:mini"; then
    echo "✅ phi3:mini model successfully loaded!"
else
    echo "❌ Failed to load phi3:mini model"
    exit 1
fi

# Test the model
echo "🧪 Testing model..."
response=$(docker exec masterarbeit-ollama ollama run phi3:mini "Hello, are you working?" --verbose 2>&1)
if echo "$response" | grep -q "Hello"; then
    echo "✅ Model test successful!"
else
    echo "⚠️ Model test returned unexpected response"
fi

echo "
🎉 Ollama setup complete!

📋 Service Status:
- Ollama URL: http://localhost:11434
- Model: phi3:mini
- Container: masterarbeit-ollama
- Network: masterarbeit-net

💡 Next steps:
1. Run 'docker-compose up -d' to start all services
2. Test with: python test_ollama_integration.py
3. Check logs: docker logs masterarbeit-ollama
"