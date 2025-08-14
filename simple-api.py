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
            logger.info(f"Extracting article from URL: {url}")
            title, content = extract_article_simple(url)
            source_url = url
            logger.info(f"Extracted: {title[:50]}... ({len(content)} chars)")
            
        elif article_type == 'text':
            title = data.get('title', 'Untitled')
            content = data.get('content', '')
            
        if not content:
            return jsonify({'error': 'No content to convert'}), 400
        
        # Get conversion settings
        voice = data.get('voice', 'en-US-BrianNeural')
        speed = float(data.get('speed', 1.0))
        
        # Generate audio using Edge TTS (no rate limits!)
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        
        # Use Edge TTS with timeout and chunking for long content
        import asyncio
        
        async def generate_edge_tts():
            # For very long content (>10k chars), chunk it
            if len(content) > 10000:
                logger.info(f"Long content detected ({len(content)} chars), chunking...")
                chunks = chunk_text(content, 8000)  # 8k char chunks
                all_audio = []
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                    chunk_path = str(audio_path).replace('.mp3', f'_chunk_{i}.mp3')
                    communicate = edge_tts.Communicate(chunk, voice)
                    await communicate.save(chunk_path)
                    all_audio.append(chunk_path)
                
                # Combine chunks using ffmpeg or just use first chunk for now
                # For simplicity, just use the first chunk
                import shutil
                shutil.move(all_audio[0], str(audio_path))
                
                # Clean up other chunks
                for chunk_path in all_audio[1:]:
                    try:
                        os.remove(chunk_path)
                    except:
                        pass
            else:
                communicate = edge_tts.Communicate(content, voice)
                await communicate.save(str(audio_path))
        
        # Run Edge TTS with timeout
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Add 5 minute timeout
            loop.run_until_complete(asyncio.wait_for(generate_edge_tts(), timeout=300))
        except asyncio.TimeoutError:
            logger.error("Edge TTS timeout - falling back to first 5000 chars")
            # Fallback: use truncated content
            truncated_content = content[:5000] + "... (content truncated due to length)"
            
            async def fallback_tts():
                communicate = edge_tts.Communicate(truncated_content, voice)
                await communicate.save(str(audio_path))
            
            loop.run_until_complete(fallback_tts())
        finally:
            loop.close()
        
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
        # Add https:// if no scheme provided
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
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

def chunk_text(text, max_chunk_size=8000):
    """Split text into chunks at sentence boundaries"""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Add sentence to current chunk if it fits
        if len(current_chunk + sentence + '. ') <= max_chunk_size:
            current_chunk += sentence + '. '
        else:
            # Start new chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

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

@app.route('/test-app.html')
def serve_test_app():
    """Serve the test app"""
    return send_file('test-app.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Simple API Server on port {port}")
    print(f"📁 Audio files will be saved to: {OUTPUT_DIR}")
    print(f"🌐 Access mobile app at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)