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

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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

@app.get("/")
async def root():
    """API documentation"""
    return {
        "service": "Article-to-Audio Personal Data Lake",
        "version": "2.0.2",
        "docs": "/docs",
        "health": "/health",
        "purpose": "Personal data lake for AI agent access",
        "debug_info": {
            "server_file": __file__,
            "supabase_connected": supabase is not None,
            "routes_count": len(app.routes),
            "timestamp": datetime.now().isoformat()
        }
    }

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