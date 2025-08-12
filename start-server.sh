#!/bin/bash
# Start the Article to Audio local server

echo "🎧 Starting Article to Audio Server..."
echo "📋 Make sure the CLI is available at: /Users/aettefagh/model-finetuning-project/article2audio-enhanced"
echo ""

# Check if CLI exists
if [ ! -f "/Users/aettefagh/model-finetuning-project/article2audio-enhanced" ]; then
    echo "❌ CLI not found at expected location!"
    echo "   Please make sure article2audio-enhanced is installed"
    exit 1
fi

echo "✅ CLI found"
echo "🚀 Starting server on http://localhost:8888"
echo "🔄 Press Ctrl+C to stop"
echo ""

python3 server.py 8888