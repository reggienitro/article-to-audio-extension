#!/usr/bin/env python3
"""
API Server for Article-to-Audio Conversion
Handles article conversion requests and integrates with Supabase
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import uuid
import asyncio
import edge_tts
from gtts import gTTS
from newspaper import Article
from readability.readability import Document
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

# Supported voices
EDGE_TTS_VOICES = {
    'en-US-BrianNeural': 'Brian (Male)',
    'en-US-AriaNeural': 'Aria (Female)', 
    'en-US-GuyNeural': 'Guy (Male)',
    'en-US-JennyNeural': 'Jenny (Female)',
    'en-GB-RyanNeural': 'Ryan (British Male)',
    'en-GB-SoniaNeural': 'Sonia (British Female)'
}

@app.route('/api/convert', methods=['POST'])
async def convert_article():
    """Convert article to audio"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header.replace('Bearer ', '')):
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Extract article content based on type
        article_type = data.get('type')
        title = ''
        content = ''
        source_url = ''
        
        if article_type == 'url':
            url = data.get('url')
            title, content = extract_article_from_url(url)
            source_url = url
            
        elif article_type == 'text':
            title = data.get('title', 'Untitled')
            content = data.get('content', '')
            
        elif article_type == 'file':
            # Handle file upload (implement file processing)
            return jsonify({'error': 'File upload not yet implemented'}), 400
        
        if not content:
            return jsonify({'error': 'No content to convert'}), 400
        
        # Get conversion settings
        voice = data.get('voice', 'en-US-BrianNeural')
        speed = float(data.get('speed', 1.0))
        storage_mode = data.get('storageMode', 'ask')
        
        # Generate audio
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        
        # Use Edge TTS for conversion
        await generate_audio_edge_tts(content, str(audio_path), voice, speed)
        
        # Calculate duration and other metadata
        word_count = len(content.split())
        estimated_read_time = word_count // 200  # Assuming 200 words per minute
        
        # Prepare response
        result = {
            'success': True,
            'title': title,
            'content': content[:500] + '...' if len(content) > 500 else content,
            'sourceUrl': source_url,
            'audioUrl': f'/audio/{audio_filename}',
            'audioPath': str(audio_path),
            'voice': voice,
            'speed': speed,
            'wordCount': word_count,
            'estimatedReadTime': estimated_read_time
        }
        
        # Save to Supabase if requested
        if supabase and storage_mode in ['always', 'favorites']:
            save_to_supabase(result, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def extract_article_from_url(url):
    """Extract article content from URL"""
    try:
        # Try newspaper3k first
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text:
            return article.title, article.text
        
        # Fallback to BeautifulSoup
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find article content
        title = soup.find('h1')
        title = title.text if title else 'Untitled Article'
        
        # Look for main content
        content_tags = soup.find_all(['p', 'article'])
        content = ' '.join([tag.text for tag in content_tags])
        
        return title, content
        
    except Exception as e:
        logger.error(f"Failed to extract article: {str(e)}")
        raise Exception(f"Failed to extract article from URL: {str(e)}")

async def generate_audio_edge_tts(text, output_path, voice, speed):
    """Generate audio using Edge TTS"""
    try:
        # Clean text
        text = text.strip()
        
        # Configure voice settings
        rate = f"{int((speed - 1) * 100):+d}%"
        
        # Create TTS object
        tts = edge_tts.Communicate(text, voice, rate=rate)
        
        # Generate and save audio
        await tts.save(output_path)
        
        logger.info(f"Audio generated: {output_path}")
        
    except Exception as e:
        logger.error(f"Edge TTS error: {str(e)}")
        # Fallback to gTTS
        generate_audio_gtts(text, output_path)

def generate_audio_gtts(text, output_path):
    """Fallback to gTTS if Edge TTS fails"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        logger.info(f"Audio generated with gTTS: {output_path}")
    except Exception as e:
        logger.error(f"gTTS error: {str(e)}")
        raise

def verify_token(token):
    """Verify Supabase JWT token"""
    if not supabase:
        return True  # Allow if Supabase not configured
    
    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(token)
        return user is not None
    except:
        return False

def save_to_supabase(article_data, user_id):
    """Save article to Supabase database"""
    if not supabase:
        return
    
    try:
        data = {
            'user_id': user_id,
            'title': article_data['title'],
            'content': article_data['content'],
            'source_url': article_data.get('sourceUrl', ''),
            'audio_url': article_data['audioUrl'],
            'word_count': article_data['wordCount'],
            'estimated_read_time': article_data['estimatedReadTime'],
            'voice_settings': {
                'voice': article_data['voice'],
                'speed': article_data['speed']
            }
        }
        
        result = supabase.table('articles').insert(data).execute()
        logger.info(f"Saved to Supabase: {result.data[0]['id']}")
        
    except Exception as e:
        logger.error(f"Supabase save error: {str(e)}")

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    audio_path = OUTPUT_DIR / filename
    if audio_path.exists():
        return send_file(audio_path, mimetype='audio/mpeg')
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'supabase': 'connected' if supabase else 'not configured',
        'voices': list(EDGE_TTS_VOICES.keys())
    })

@app.route('/')
def serve_app():
    """Serve the mobile app"""
    return send_file('mobile-app.html')

if __name__ == '__main__':
    # Create asyncio event loop for Edge TTS
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)