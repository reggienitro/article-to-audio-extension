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
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    print("Supabase connected")
else:
    print("Supabase not configured")

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
    return {"message": "Article-to-Audio Cloud Server", "status": "running"}

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
            
            # Save locally as backup if Supabase failed
            local_path = None
            if not audio_url:  # Supabase upload failed, save locally
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                local_path = output_dir / filename
                
                # Copy temp file to output directory
                import shutil
                shutil.copy2(temp_path, local_path)
                print(f"Saved locally: {local_path}")
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return {
                "success": True,
                "message": "Conversion completed successfully",
                "article_id": article_id,
                "audio_url": audio_url,
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
    """Convert text to speech using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

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
            url_response = supabase.storage.from_('audio-files').get_public_url(filename)
            print(f"File uploaded to Supabase: {filename}")
            return url_response
        else:
            print(f"Upload failed: {response}")
            return None
            
    except Exception as e:
        print(f"Upload to Supabase failed: {e}")
        return None

async def save_article_to_db(request: ConversionRequest, audio_url: Optional[str]) -> Optional[str]:
    """Save article metadata to Supabase database"""
    try:
        # Simple article data matching existing schema
        article_data = {
            "title": request.title,
            "audio_url": audio_url,
            "is_favorite": request.isFavorite,
            "word_count": len(request.content.split()),
            "estimated_read_time": max(1, len(request.content.split()) // 200)
        }
        
        if request.userId:
            article_data["user_id"] = request.userId
        
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

@app.get("/articles")
async def get_articles(user_id: Optional[str] = None):
    """Get all articles for a user"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table('articles').select('*').order('created_at', desc=True)
        
        if user_id:
            query = query.eq('user_id', user_id)
        
        response = query.execute()
        
        articles = []
        for article in response.data:
            articles.append(ArticleResponse(
                id=article['id'],
                title=article['title'],
                content=article['content'][:200] + "..." if len(article['content']) > 200 else article['content'],
                audio_url=article.get('audio_url'),
                is_favorite=article.get('is_favorite', False),
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
    """Serve mobile player interface"""
    mobile_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Article-to-Audio Mobile</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            h1 { color: #333; text-align: center; margin-bottom: 10px; }
            .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
            .article { background: white; margin: 15px 0; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .article h3 { margin: 0 0 10px 0; color: #333; font-size: 18px; }
            .article p { color: #666; font-size: 14px; line-height: 1.4; margin: 10px 0; }
            audio { width: 100%; margin-top: 15px; }
            .no-articles { text-align: center; color: #999; padding: 40px; }
            .loading { text-align: center; color: #666; padding: 20px; }
        </style>
    </head>
    <body>
        <h1>🎧 Article-to-Audio</h1>
        <p class="subtitle">Your converted articles</p>
        <div id="articles" class="loading">Loading articles...</div>
        
        <script>
            fetch('/articles')
                .then(r => r.json())
                .then(data => {
                    const articles = data.articles || [];
                    const container = document.getElementById('articles');
                    
                    if (articles.length === 0) {
                        container.innerHTML = '<div class="no-articles">No articles yet. Convert some articles using the Chrome extension!</div>';
                        return;
                    }
                    
                    container.innerHTML = articles.map(a => `
                        <div class="article">
                            <h3>${a.title}</h3>
                            <p>${a.content}</p>
                            ${a.audio_url ? `<audio controls preload="metadata">
                                <source src="${a.audio_url}" type="audio/mpeg">
                                Your browser does not support the audio element.
                            </audio>` : '<p style="color: #999;">Audio processing...</p>'}
                        </div>
                    `).join('');
                })
                .catch(err => {
                    document.getElementById('articles').innerHTML = '<div class="no-articles">Error loading articles. Please try again.</div>';
                });
        </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=mobile_html)

# Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)