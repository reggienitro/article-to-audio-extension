#!/bin/bash

# Simple mobile test server
echo "🚀 Starting mobile test server..."
echo "📱 Access from iPhone at: http://$(ipconfig getifaddr en0):8888"
echo "🌐 Files available:"
echo "   - http://$(ipconfig getifaddr en0):8888/chrome-mobile-demo.html"
echo "   - http://$(ipconfig getifaddr en0):8888/mobile-player.html"
echo ""
echo "🛑 Press Ctrl+C to stop"

# Copy the Chrome demo to local directory
cp "/Users/aettefagh/Library/Mobile Documents/com~apple~CloudDocs/Mobile-Demos/chrome-mobile-demo.html" ./

# Start simple HTTP server
python3 -m http.server 8888 --bind 0.0.0.0