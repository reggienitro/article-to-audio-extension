#!/usr/bin/env python3
"""
Enhanced Article-to-Audio Server for Personal Data Lake
Single-user system integrated with Supabase for AI agent access
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Import dependencies
try:
    import edge_tts
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install fastapi uvicorn edge-tts supabase python-dotenv")
    exit(1)

load_dotenv()

app = FastAPI(
    title="Article-to-Audio Personal Data Lake", 
    version="2.0.2",
    description="🔥 ENHANCED Personal article-to-audio converter with Supabase data lake integration 🔥"
)

# CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Chrome extension
    allow_credentials=False,  # Set to False for wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Supabase setup - Using consistent naming
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Using SUPABASE_KEY for consistency
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test connection with our simple table
        test = supabase.table('article_audio').select('id').limit(1).execute()
        print(f"✅ Supabase connected to personal data lake")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
        print("Creating table if not exists...")
        supabase = None
else:
    print("⚠️ Supabase not configured - local mode only")

# Output directory for local storage fallback
OUTPUT_DIR = Path("/app/output") if os.path.exists("/app") else Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Data models
class ConversionRequest(BaseModel):
    """Request to convert article to audio"""
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    url: Optional[str] = Field(None, description="Source URL")
    voice: str = Field("en-US-BrianNeural", description="TTS voice")
    is_favorite: bool = Field(False, description="Mark as favorite")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata for AI agents")

class ArticleAudio(BaseModel):
    """Article with audio in data lake"""
    id: str
    title: str
    content: str
    audio_url: Optional[str]
    audio_filename: Optional[str]
    source_url: Optional[str]
    voice: str
    is_favorite: bool
    word_count: int
    created_at: str
    metadata: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve responsive UI - mobile for mobile devices, web for desktop"""
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Detect mobile devices
    is_mobile = any(device in user_agent for device in [
        'mobile', 'iphone', 'android', 'blackberry', 'windows phone'
    ])
    
    # Embedded HTML UI (works in Render deployment)
    if is_mobile:
        html_content = get_mobile_html()
    else:
        html_content = get_web_html()
        
    return HTMLResponse(content=html_content)

def get_web_html():
    """Embedded web interface HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article-to-Audio Personal Data Lake</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .convert-form { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input, textarea, select { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; }
        textarea { min-height: 120px; resize: vertical; }
        .btn { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #45a049; }
        .btn:disabled { background: #cccccc; cursor: not-allowed; }
        .status { margin-top: 20px; padding: 15px; border-radius: 8px; }
        .status.success { background: rgba(76, 175, 80, 0.2); border: 1px solid #4CAF50; }
        .status.error { background: rgba(244, 67, 54, 0.2); border: 1px solid #f44336; }
        .audio-player { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎧 Article-to-Audio</h1>
            <p>Personal Data Lake v2.0.2</p>
        </div>
        
        <form class="convert-form" id="convertForm">
            <div class="form-group">
                <label for="url">Article URL (optional):</label>
                <input type="url" id="url" placeholder="https://example.com/article">
            </div>
            
            <div class="form-group">
                <label for="title">Title:</label>
                <input type="text" id="title" placeholder="Article title" required>
            </div>
            
            <div class="form-group">
                <label for="content">Content:</label>
                <textarea id="content" placeholder="Paste article content here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label for="voice">Voice:</label>
                <select id="voice">
                    <option value="en-US-BrianNeural">Brian (US Male)</option>
                    <option value="en-US-JennyNeural">Jenny (US Female)</option>
                    <option value="en-GB-SoniaNeural">Sonia (UK Female)</option>
                    <option value="en-AU-WilliamNeural">William (AU Male)</option>
                </select>
            </div>
            
            <button type="submit" class="btn" id="convertBtn">Convert to Audio</button>
            
            <div id="status"></div>
            <div id="audioPlayer"></div>
        </form>
    </div>

    <script>
        document.getElementById('convertForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('convertBtn');
            const status = document.getElementById('status');
            const audioPlayer = document.getElementById('audioPlayer');
            
            btn.disabled = true;
            btn.textContent = 'Converting...';
            status.innerHTML = '';
            audioPlayer.innerHTML = '';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: document.getElementById('title').value,
                        content: document.getElementById('content').value,
                        voice: document.getElementById('voice').value,
                        source_url: document.getElementById('url').value || null
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.id) {
                    status.innerHTML = '<div class="status success">✅ Conversion successful!</div>';
                    
                    if (result.audio_url) {
                        audioPlayer.innerHTML = `
                            <div class="audio-player">
                                <h3>🎵 ${result.title}</h3>
                                <audio controls style="width: 100%; margin-top: 10px;">
                                    <source src="${result.audio_url}" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                                <p style="margin-top: 10px; opacity: 0.8;">
                                    ${result.word_count} words • Generated: ${new Date(result.created_at).toLocaleString()}
                                </p>
                            </div>
                        `;
                    }
                } else {
                    throw new Error(result.detail || 'Conversion failed');
                }
            } catch (error) {
                status.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Convert to Audio';
            }
        });
    </script>
</body>
</html>
"""

def get_mobile_html():
    """Embedded mobile interface HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article-to-Audio Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 15px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2rem; margin-bottom: 5px; }
        .convert-form { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; font-size: 14px; }
        input, textarea, select { width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 16px; }
        textarea { min-height: 100px; }
        .btn { width: 100%; background: #4CAF50; color: white; padding: 15px; border: none; border-radius: 8px; font-size: 18px; margin-top: 10px; }
        .btn:disabled { background: #cccccc; }
        .status { margin-top: 15px; padding: 10px; border-radius: 8px; font-size: 14px; }
        .status.success { background: rgba(76, 175, 80, 0.3); }
        .status.error { background: rgba(244, 67, 54, 0.3); }
        .audio-player { margin-top: 15px; }
        audio { width: 100%; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎧 Audio Convert</h1>
        <p>Mobile Interface</p>
    </div>
    
    <form class="convert-form" id="convertForm">
        <div class="form-group">
            <label for="title">Title:</label>
            <input type="text" id="title" placeholder="Article title" required>
        </div>
        
        <div class="form-group">
            <label for="content">Content:</label>
            <textarea id="content" placeholder="Paste content here..." required></textarea>
        </div>
        
        <div class="form-group">
            <label for="voice">Voice:</label>
            <select id="voice">
                <option value="en-US-BrianNeural">Brian (US)</option>
                <option value="en-US-JennyNeural">Jenny (US)</option>
            </select>
        </div>
        
        <button type="submit" class="btn" id="convertBtn">Convert to Audio</button>
        
        <div id="status"></div>
        <div id="audioPlayer"></div>
    </form>

    <script>
        document.getElementById('convertForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('convertBtn');
            const status = document.getElementById('status');
            const audioPlayer = document.getElementById('audioPlayer');
            
            btn.disabled = true;
            btn.textContent = 'Converting...';
            status.innerHTML = '';
            audioPlayer.innerHTML = '';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: document.getElementById('title').value,
                        content: document.getElementById('content').value,
                        voice: document.getElementById('voice').value
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.id) {
                    status.innerHTML = '<div class="status success">✅ Success!</div>';
                    
                    if (result.audio_url) {
                        audioPlayer.innerHTML = `
                            <div class="audio-player">
                                <h3>🎵 Ready to Play</h3>
                                <audio controls>
                                    <source src="${result.audio_url}" type="audio/mpeg">
                                </audio>
                                <p style="margin-top: 8px; font-size: 12px; opacity: 0.8;">
                                    ${result.word_count} words
                                </p>
                            </div>
                        `;
                    }
                } else {
                    throw new Error(result.detail || 'Failed');
                }
            } catch (error) {
                status.innerHTML = `<div class="status error">❌ ${error.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Convert to Audio';
            }
        });
    </script>
</body>
</html>
"""

@app.get("/debug")
async def debug_info():
    """Debug endpoint to verify deployment"""
    return {
        "🔥": "ENHANCED SERVER DEBUG",
        "app_title": app.title,
        "app_version": app.version,
        "app_description": app.description,
        "server_file": __file__,
        "supabase_url": SUPABASE_URL,
        "supabase_connected": supabase is not None,
        "routes": [route.path for route in app.routes if hasattr(route, 'path')],
        "enhanced_endpoints": ["/library", "/stats", "/search", "/article/{id}"],
        "deployment_timestamp": datetime.now().isoformat(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
        "environment_check": {
            "SUPABASE_URL": bool(SUPABASE_URL),
            "SUPABASE_KEY": bool(SUPABASE_KEY),
            "PORT": os.getenv("PORT", "default")
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supabase_connected": supabase is not None,
        "data_lake": "operational",
        "storage": "supabase" if supabase else "local"
    }


@app.post("/convert", response_model=ArticleAudio)
async def convert_article(request: ConversionRequest):
    """Convert article to audio and store in data lake"""
    
    # Calculate word count
    word_count = len(request.content.split())
    
    # Generate audio in memory first
    audio_filename = f"{uuid.uuid4().hex[:8]}_{request.title[:30].replace(' ', '_')}.mp3"
    
    try:
        # Generate audio directly to file first
        audio_path = OUTPUT_DIR / audio_filename
        communicate = edge_tts.Communicate(request.content, request.voice)
        
        # Save directly to file
        await communicate.save(str(audio_path))
        
        # Read the file for base64 encoding and potential Supabase upload
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        print(f"✅ Audio generated: {audio_filename} ({len(audio_data)} bytes)")
        
        # Store in Supabase if available
        if supabase:
            try:
                # Upload to Supabase storage
                storage_path = f"audio/{audio_filename}"
                supabase.storage.from_('audio-files').upload(
                    storage_path, 
                    audio_data,
                    {"content-type": "audio/mpeg"}
                )
                
                # Get public URL
                audio_url = supabase.storage.from_('audio-files').get_public_url(storage_path)
                
                # Store metadata in database
                article_data = {
                    'title': request.title,
                    'content': request.content,
                    'audio_url': audio_url,
                    'audio_filename': audio_filename,
                    'source_url': request.url,
                    'voice': request.voice,
                    'is_favorite': request.is_favorite,
                    'word_count': word_count,
                    'metadata': request.metadata
                }
                
                result = supabase.table('article_audio').insert(article_data).execute()
                
                if result.data:
                    article = result.data[0]
                    print(f"✅ Stored in data lake: {article['id']}")
                    
                    return ArticleAudio(
                        id=article['id'],
                        title=article['title'],
                        content=article['content'],
                        audio_url=article['audio_url'],
                        audio_filename=article['audio_filename'],
                        source_url=article.get('source_url'),
                        voice=article['voice'],
                        is_favorite=article['is_favorite'],
                        word_count=article['word_count'],
                        created_at=article['created_at'],
                        metadata=article.get('metadata', {})
                    )
                    
            except Exception as e:
                print(f"⚠️ Supabase storage failed: {e}")
        
        # Local storage fallback - return base64 encoded audio for immediate access
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return ArticleAudio(
            id=str(uuid.uuid4()),
            title=request.title,
            content=request.content,
            audio_url=f"data:audio/mpeg;base64,{audio_base64}",  # Embed audio directly
            audio_filename=audio_filename,
            source_url=request.url,
            voice=request.voice,
            is_favorite=request.is_favorite,
            word_count=word_count,
            created_at=datetime.now().isoformat(),
            metadata=request.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/library", response_model=List[ArticleAudio])
async def get_library(
    limit: int = Query(50, description="Max articles to return"),
    favorites_only: bool = Query(False, description="Only return favorites")
):
    """Get all articles from personal data lake"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        query = supabase.table('article_audio').select('*')
        
        if favorites_only:
            query = query.eq('is_favorite', True)
        
        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        
        if result.data:
            return [
                ArticleAudio(
                    id=item['id'],
                    title=item['title'],
                    content=item['content'],
                    audio_url=item.get('audio_url'),
                    audio_filename=item.get('audio_filename'),
                    source_url=item.get('source_url'),
                    voice=item['voice'],
                    is_favorite=item['is_favorite'],
                    word_count=item['word_count'],
                    created_at=item['created_at'],
                    metadata=item.get('metadata', {})
                )
                for item in result.data
            ]
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch library: {str(e)}")

@app.get("/article/{article_id}", response_model=ArticleAudio)
async def get_article(article_id: str):
    """Get specific article from data lake"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        result = supabase.table('article_audio').select('*').eq('id', article_id).execute()
        
        if result.data:
            item = result.data[0]
            return ArticleAudio(
                id=item['id'],
                title=item['title'],
                content=item['content'],
                audio_url=item.get('audio_url'),
                audio_filename=item.get('audio_filename'),
                source_url=item.get('source_url'),
                voice=item['voice'],
                is_favorite=item['is_favorite'],
                word_count=item['word_count'],
                created_at=item['created_at'],
                metadata=item.get('metadata', {})
            )
        else:
            raise HTTPException(status_code=404, detail="Article not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")

@app.put("/article/{article_id}/favorite")
async def toggle_favorite(article_id: str):
    """Toggle favorite status for article"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        # Get current status
        result = supabase.table('article_audio').select('is_favorite').eq('id', article_id).execute()
        
        if result.data:
            current_status = result.data[0]['is_favorite']
            new_status = not current_status
            
            # Update status
            update_result = supabase.table('article_audio').update({
                'is_favorite': new_status
            }).eq('id', article_id).execute()
            
            if update_result.data:
                return {"id": article_id, "is_favorite": new_status}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update favorite: {str(e)}")

@app.delete("/article/{article_id}")
async def delete_article(article_id: str):
    """Delete article from data lake"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        # Get article info first
        result = supabase.table('article_audio').select('audio_filename').eq('id', article_id).execute()
        
        if result.data:
            audio_filename = result.data[0].get('audio_filename')
            
            # Delete from storage if exists
            if audio_filename:
                try:
                    supabase.storage.from_('audio-files').remove([f"audio/{audio_filename}"])
                except Exception as e:
                    print(f"⚠️ Failed to delete audio file: {e}")
            
            # Delete from database
            delete_result = supabase.table('article_audio').delete().eq('id', article_id).execute()
            
            return {"message": "Article deleted", "id": article_id}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")

@app.get("/search")
async def search_articles(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Max results")
):
    """Search articles in data lake for AI agent access"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        # Search in title and content
        result = supabase.table('article_audio').select('*')\
            .or_(f"title.ilike.%{q}%,content.ilike.%{q}%")\
            .limit(limit)\
            .execute()
        
        if result.data:
            return {
                "query": q,
                "count": len(result.data),
                "results": result.data
            }
        return {"query": q, "count": 0, "results": []}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get statistics about your data lake"""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Data lake not available")
    
    try:
        # Get total count
        all_articles = supabase.table('article_audio').select('id', count='exact').execute()
        favorites = supabase.table('article_audio').select('id', count='exact').eq('is_favorite', True).execute()
        
        # Get total words
        word_count_result = supabase.table('article_audio').select('word_count').execute()
        total_words = sum(item['word_count'] for item in word_count_result.data) if word_count_result.data else 0
        
        return {
            "total_articles": all_articles.count if hasattr(all_articles, 'count') else len(all_articles.data),
            "total_favorites": favorites.count if hasattr(favorites, 'count') else len(favorites.data),
            "total_words": total_words,
            "average_words": total_words // len(all_articles.data) if all_articles.data else 0,
            "data_lake_status": "operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Serve local audio files if in local mode
@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve audio file from local storage"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print("🔥 AGGRESSIVE DEBUG INFO:")
    print(f"📄 Server File: {__file__}")
    print(f"🚀 FastAPI App Title: {app.title}")
    print(f"🔢 FastAPI App Version: {app.version}")
    print(f"📝 Server Description: {app.description}")
    print(f"🌐 Port: {port}")
    print(f"📊 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Supabase Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "None")
    print(f"💾 Supabase Connected: {'YES' if supabase else 'NO'}")
    print(f"📁 Output Dir: {OUTPUT_DIR}")
    print(f"🐍 Python Path: {os.path.abspath(__file__)}")
    
    # List all routes
    print("📋 Available Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"   {route.path}")
    
    print("🚀 Starting Article-to-Audio Data Lake Server...")
    uvicorn.run(app, host="0.0.0.0", port=port)