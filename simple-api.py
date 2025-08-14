#!/usr/bin/env python3
"""
Simple API Server for Article-to-Audio Conversion
Minimal version for testing
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import uuid
import asyncio
import edge_tts
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv
import tempfile
from pathlib import Path
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Output directory for audio files
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

@app.route('/api/convert', methods=['POST'])
def convert_article():
    """Convert article to audio - simplified version"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        # Extract article content based on type
        article_type = data.get('type')
        title = ''
        content = ''
        source_url = ''
        
        if article_type == 'url':
            url = data.get('url')
            title, content = extract_article_simple(url)
            source_url = url
            
        elif article_type == 'text':
            title = data.get('title', 'Untitled')
            content = data.get('content', '')
            
        if not content:
            return jsonify({'error': 'No content to convert'}), 400
        
        # Get conversion settings
        voice = data.get('voice', 'en-US-BrianNeural')
        speed = float(data.get('speed', 1.0))
        
        # Generate audio using gTTS (simpler than Edge TTS for now)
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        
        # Use gTTS for quick testing
        tts = gTTS(text=content, lang='en', slow=False)
        tts.save(str(audio_path))
        
        # Calculate metadata
        word_count = len(content.split())
        estimated_read_time = word_count // 200
        
        # Prepare response
        result = {
            'success': True,
            'title': title,
            'content': content[:500] + '...' if len(content) > 500 else content,
            'sourceUrl': source_url,
            'audioUrl': f'/audio/{audio_filename}',
            'voice': voice,
            'speed': speed,
            'wordCount': word_count,
            'estimatedReadTime': estimated_read_time
        }
        
        logger.info(f"Converted article: {title} -> {audio_filename}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def extract_article_simple(url):
    """Simple article extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find title
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.text.strip() if title_elem else 'Untitled Article'
        
        # Try to find main content
        # Look for common article containers
        content_selectors = [
            'article', '.content', '.post-content', '.entry-content',
            '.article-content', 'main', '.main-content'
        ]
        
        content = ''
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text()
                break
        
        # Fallback to all paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
        
        # Clean up content
        content = ' '.join(content.split())  # Remove extra whitespace
        
        if len(content) < 50:  # Too short, might not be the right content
            raise Exception("Could not extract meaningful content from URL")
        
        return title, content
        
    except Exception as e:
        logger.error(f"Failed to extract article: {str(e)}")
        raise Exception(f"Failed to extract article from URL: {str(e)}")

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    audio_path = OUTPUT_DIR / filename
    if audio_path.exists():
        return send_file(str(audio_path), mimetype='audio/mpeg')
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'supabase': 'connected' if supabase else 'not configured',
        'output_dir': str(OUTPUT_DIR),
        'files_count': len(list(OUTPUT_DIR.glob('*.mp3')))
    })

@app.route('/')
def serve_app():
    """Serve the mobile app"""
    return send_file('mobile-app.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Simple API Server on port {port}")
    print(f"📁 Audio files will be saved to: {OUTPUT_DIR}")
    print(f"🌐 Access mobile app at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)