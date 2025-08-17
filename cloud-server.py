#!/usr/bin/env python3
"""
Cloud-ready Article-to-Audio server
Handles TTS conversion and Supabase sync for cross-device access
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, model_validator
import uvicorn

# Import dependencies
try:
    import edge_tts
    from gtts import gTTS
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install fastapi uvicorn edge-tts gtts supabase python-dotenv")
    exit(1)

load_dotenv()

app = FastAPI(title="Article-to-Audio Cloud Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        # Test connection
        supabase.table('articles').select('id').limit(1).execute()
        print("Supabase connected")
    except Exception as e:
        print(f"Supabase connection failed: {e}")
        print("Falling back to local storage")
        supabase = None
else:
    print("Supabase not configured - using local storage")

# Data models
class ConversionRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    voice: str = "en-US-BrianNeural"
    storageMode: str = "ask"
    isFavorite: bool = False
    userId: Optional[str] = None
    
    @model_validator(mode='before')
    @classmethod 
    def validate_content_or_url(cls, values):
        if not values.get('url') and not (values.get('title') and values.get('content')):
            raise ValueError('Either URL or both title and content must be provided')
        return values

class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    audio_url: Optional[str]
    is_favorite: bool
    created_at: str
    word_count: int

@app.get("/")
async def root():
    """Serve mobile app by default"""
    return FileResponse('mobile-app.html')

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "supabase_connected": supabase is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/convert")
async def convert_article(request: ConversionRequest):
    """Convert article to audio and store in cloud"""
    try:
        # If URL is provided but no content, extract from URL
        if request.url and not request.content:
            try:
                import requests
                from bs4 import BeautifulSoup
                from readability import Document
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(request.url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Use readability to extract main content
                doc = Document(response.content)
                request.title = doc.title() or "Web Article"
                request.content = doc.summary()
                
                # Clean HTML tags
                soup = BeautifulSoup(request.content, 'html.parser')
                request.content = soup.get_text(separator=' ', strip=True)
                
                print(f"Extracted from URL: {request.title} ({len(request.content)} chars)")
                
            except Exception as e:
                print(f"URL extraction failed: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to extract content from URL: {str(e)}")
        
        # Check if we have content to convert
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(status_code=400, detail="Article content is too short or missing")
            
        print(f"Converting: {request.title} ({len(request.content)} chars)")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = "".join(c for c in request.title if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{timestamp}_{safe_title}.mp3"
        
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Convert to audio using Edge TTS
            if request.voice.startswith('en-'):
                await convert_with_edge_tts(request.content, request.voice, temp_path)
            else:
                convert_with_gtts(request.content, request.voice, temp_path)
            
            print(f"Audio generated: {temp_path}")
            
            # Upload to Supabase storage if available
            audio_url = None
            if supabase:
                audio_url = await upload_to_supabase_storage(temp_path, filename)
            
            # Save article to database
            article_id = None
            if supabase and request.storageMode != 'never':
                article_id = await save_article_to_db(request, audio_url)
            
            # Save locally as backup if Supabase failed or not available
            local_path = None
            local_url = None
            if not audio_url:  # Supabase upload failed or not available, save locally
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                local_path = output_dir / filename
                
                # Copy temp file to output directory
                import shutil
                shutil.copy2(temp_path, local_path)
                local_url = f"/audio/{filename}"
                print(f"Saved locally: {local_path}")
                
                # Also save article metadata locally if no Supabase
                if not supabase:
                    await save_article_locally(request, local_url, filename)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return {
                "success": True,
                "message": "Conversion completed successfully",
                "article_id": article_id,
                "audio_url": audio_url or local_url,
                "filename": filename
            }
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
            
    except Exception as e:
        print(f"Conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def convert_with_edge_tts(text: str, voice: str, output_path: str):
    """Convert text to speech using Edge TTS with chunking support"""
    # For very long texts, chunk them to avoid timeouts
    max_chunk_size = 10000  # characters
    
    if len(text) <= max_chunk_size:
        # Short text, convert directly
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    else:
        # Long text, chunk it
        print(f"Long text detected ({len(text)} chars), chunking into segments")
        chunks = chunk_text(text, max_chunk_size)
        
        # Convert each chunk and combine
        temp_files = []
        try:
            for i, chunk in enumerate(chunks):
                chunk_path = f"{output_path}.chunk_{i}.mp3"
                communicate = edge_tts.Communicate(chunk, voice)
                await communicate.save(chunk_path)
                temp_files.append(chunk_path)
                print(f"Converted chunk {i+1}/{len(chunks)}")
            
            # Combine chunks using ffmpeg if available, otherwise use first chunk
            try:
                import subprocess
                
                # Create concat file for ffmpeg
                concat_file = f"{output_path}.concat.txt"
                with open(concat_file, 'w') as f:
                    for temp_file in temp_files:
                        f.write(f"file '{temp_file}'\n")
                
                # Use ffmpeg to concatenate
                subprocess.run([
                    'ffmpeg', '-f', 'concat', '-safe', '0', 
                    '-i', concat_file, '-c', 'copy', output_path
                ], check=True, capture_output=True)
                
                print("Audio chunks combined successfully")
                os.unlink(concat_file)
                
            except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: just use the first chunk
                print("ffmpeg not available, using first chunk only")
                import shutil
                shutil.copy2(temp_files[0], output_path)
        
        finally:
            # Clean up temp chunk files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

def chunk_text(text: str, max_size: int) -> list:
    """Split text into chunks at sentence boundaries"""
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences (simple approach)
    sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_size:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def convert_with_gtts(text: str, lang: str, output_path: str):
    """Convert text to speech using Google TTS"""
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)

async def upload_to_supabase_storage(file_path: str, filename: str) -> Optional[str]:
    """Upload audio file to Supabase storage"""
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Upload to Supabase storage
        response = supabase.storage.from_('audio-files').upload(
            path=filename,
            file=file_data,
            file_options={"content-type": "audio/mpeg"}
        )
        
        if response.status_code == 200:
            # Get public URL  
            public_url_response = supabase.storage.from_('audio-files').get_public_url(filename)
            public_url = public_url_response.get('publicUrl') if isinstance(public_url_response, dict) else public_url_response
            print(f"File uploaded to Supabase: {filename}")
            print(f"Public URL: {public_url}")
            return public_url
        else:
            print(f"Upload failed: {response}")
            return None
            
    except Exception as e:
        print(f"Upload to Supabase failed: {e}")
        return None

async def save_article_to_db(request: ConversionRequest, audio_url: Optional[str]) -> Optional[str]:
    """Save article metadata to Supabase database"""
    try:
        # Article data matching your existing schema
        article_data = {
            "url": request.url,
            "title": request.title,
            "extracted_text": request.content,
            "audio_url": audio_url,
            "word_count": len(request.content.split()) if request.content else 0,
            "estimated_read_time": max(1, len(request.content.split()) // 200) if request.content else 1,
            "source_domain": extract_domain(request.url) if request.url else None,
            "content_hash": generate_content_hash(request.content) if request.content else None
        }
        
        response = supabase.table('articles').insert(article_data).execute()
        
        if response.data:
            article_id = response.data[0]['id']
            print(f"Article saved to DB: {article_id}")
            return article_id
        else:
            print(f"Failed to save article: {response}")
            return None
            
    except Exception as e:
        print(f"Database save failed: {e}")
        return None

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None

def generate_content_hash(content: str) -> Optional[str]:
    """Generate hash for content deduplication"""
    try:
        import hashlib
        return hashlib.md5(content.encode()).hexdigest() if content else None
    except:
        return None

async def save_article_locally(request: ConversionRequest, audio_url: str, filename: str):
    """Save article metadata to local JSON file when Supabase unavailable"""
    try:
        articles_file = Path("articles.json")
        articles = []
        
        # Load existing articles
        if articles_file.exists():
            with open(articles_file, 'r') as f:
                articles = json.load(f)
        
        # Add new article
        article_data = {
            "id": str(uuid.uuid4()),
            "url": request.url,
            "title": request.title,
            "extracted_text": request.content,
            "audio_url": audio_url,
            "word_count": len(request.content.split()) if request.content else 0,
            "estimated_read_time": max(1, len(request.content.split()) // 200) if request.content else 1,
            "created_at": datetime.now().isoformat(),
            "filename": filename
        }
        
        articles.append(article_data)
        
        # Save back to file
        with open(articles_file, 'w') as f:
            json.dump(articles, f, indent=2)
        
        print(f"Article saved locally: {article_data['id']}")
        
    except Exception as e:
        print(f"Failed to save article locally: {e}")

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve audio files from local storage"""
    try:
        audio_path = Path("output") / filename
        if audio_path.exists():
            return FileResponse(
                path=str(audio_path),
                media_type="audio/mpeg",
                filename=filename
            )
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles")
async def get_articles(user_id: Optional[str] = None):
    """Get all articles for a user - works with both Supabase and local storage"""
    try:
        if supabase:
            # Use Supabase
            query = supabase.table('articles').select('*').order('created_at', desc=True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            
            articles = []
            for article in response.data:
                content = article.get('extracted_text', '')
                articles.append(ArticleResponse(
                    id=article['id'],
                    title=article['title'],
                    content=content[:200] + "..." if len(content) > 200 else content,
                    audio_url=article.get('audio_url'),
                    is_favorite=False,  # Not in your schema
                    created_at=article['created_at'],
                    word_count=article.get('word_count', 0)
                ))
            
            return {"articles": articles}
        else:
            # Use local storage
            articles_file = Path("articles.json")
            if not articles_file.exists():
                return {"articles": []}
            
            with open(articles_file, 'r') as f:
                local_articles = json.load(f)
            
            # Sort by created_at descending
            local_articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            articles = []
            for article in local_articles:
                content = article.get('extracted_text', '')
                articles.append(ArticleResponse(
                    id=article['id'],
                    title=article['title'],
                    content=content[:200] + "..." if len(content) > 200 else content,
                    audio_url=article.get('audio_url'),
                    is_favorite=False,
                    created_at=article['created_at'],
                    word_count=article.get('word_count', 0)
                ))
            
            return {"articles": articles}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/articles/{article_id}/favorite")
async def toggle_favorite(article_id: str):
    """Toggle favorite status of an article"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get current status
        response = supabase.table('articles').select('is_favorite').eq('id', article_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Article not found")
        
        current_favorite = response.data[0].get('is_favorite', False)
        new_favorite = not current_favorite
        
        # Update favorite status
        update_response = supabase.table('articles').update({
            'is_favorite': new_favorite
        }).eq('id', article_id).execute()
        
        return {"success": True, "is_favorite": new_favorite}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mobile")
async def serve_mobile_player():
    """Serve enhanced mobile player interface"""
    return FileResponse('mobile-app.html')

# Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)