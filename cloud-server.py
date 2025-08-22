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
    version="2.0.3",
    description="🔥 MOBILE AUDIO LIBRARY - Personal article-to-audio converter with phone access 🔥"
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
        test = supabase.table('articles').select('id').limit(1).execute()
        print(f"✅ Supabase connected to personal data lake (v2)")
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
    save: bool = Field(True, description="Save to database")
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
    
    # Always use the enhanced mobile interface for all devices
    # It's responsive and works great on desktop too
    is_mobile = True
    
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
        
        <div style="text-align: center; margin-bottom: 20px;">
            <button type="button" class="btn" id="autoFillBtn" style="background: #2196F3;">📄 Auto-Fill from Current Page</button>
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
        // Auto-fill functionality
        document.getElementById('autoFillBtn').addEventListener('click', () => {
            // Get current page info
            document.getElementById('url').value = window.location.href;
            document.getElementById('title').value = document.title;
            
            // Try to extract main content
            const content = extractPageContent();
            if (content) {
                document.getElementById('content').value = content;
            } else {
                alert('Could not auto-extract content. Please paste manually.');
            }
        });
        
        function extractPageContent() {
            // Try common content selectors
            const selectors = [
                'article', '[role="main"]', '.article-content', '.post-content',
                '.entry-content', '.content', 'main', '.article-body'
            ];
            
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    return element.innerText.trim();
                }
            }
            
            // Fallback: get all paragraph text
            const paragraphs = Array.from(document.querySelectorAll('p'));
            if (paragraphs.length > 0) {
                return paragraphs.map(p => p.innerText).join('\\n\\n').trim();
            }
            
            return null;
        }
        
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
                                <audio controls style="width: 100%; margin-top: 10px;" preload="metadata">
                                    <source src="${result.audio_url}" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                                <p style="margin-top: 10px; opacity: 0.8;">
                                    ${result.word_count} words • Generated: ${new Date(result.created_at).toLocaleString()}
                                </p>
                                <div style="margin-top: 10px;">
                                    <button onclick="this.previousElementSibling.previousElementSibling.play()" style="padding: 5px 10px; background: #4CAF50; color: white; border: none; border-radius: 4px;">▶️ Play</button>
                                    <button onclick="this.previousElementSibling.previousElementSibling.pause()" style="padding: 5px 10px; background: #f44336; color: white; border: none; border-radius: 4px; margin-left: 5px;">⏸️ Pause</button>
                                </div>
                            </div>
                        `;
                        
                        // Test audio loading
                        const audio = audioPlayer.querySelector('audio');
                        audio.addEventListener('loadstart', () => console.log('Audio loading started'));
                        audio.addEventListener('canplay', () => console.log('Audio can play'));
                        audio.addEventListener('error', (e) => console.error('Audio error:', e));
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
    """Enhanced mobile interface with modern UI"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Audio Library</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            width: 100%;
            overflow-x: hidden;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header h1 {
            font-size: 24px;
            color: #333;
            text-align: center;
        }

        .container {
            padding: 15px;
            max-width: 100%;
        }

        .load-btn {
            width: 100%;
            padding: 15px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #6366f1;
        }

        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }

        .article-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .article-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.3;
        }

        .article-meta {
            display: flex;
            gap: 15px;
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
        }

        audio {
            width: 100%;
            margin-bottom: 10px;
        }

        .speed-controls {
            display: flex;
            gap: 5px;
            margin-bottom: 10px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        .speed-btn {
            padding: 8px 12px;
            background: #f0f0f0;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .speed-btn.active {
            background: #6366f1;
            color: white;
        }

        .actions {
            display: flex;
            gap: 10px;
        }

        .action-btn {
            flex: 1;
            padding: 10px;
            background: #f0f0f0;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }

        .action-btn.favorite.active {
            background: #ffebee;
            color: #f44336;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: white;
        }

        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .empty {
            text-align: center;
            padding: 40px;
            color: white;
        }

        .empty-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.7;
        }

        /* iOS specific fixes */
        @supports (-webkit-touch-callout: none) {
            body {
                -webkit-text-size-adjust: 100%;
            }
            
            .container {
                padding-bottom: env(safe-area-inset-bottom);
            }
        }

        /* Small phones */
        @media (max-width: 375px) {
            .header h1 {
                font-size: 20px;
            }
            
            .article-title {
                font-size: 16px;
            }
            
            .speed-btn {
                padding: 6px 10px;
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎧 Audio Library</h1>
    </div>

    <div class="container">
        <button class="load-btn" onclick="loadArticles()">
            <span>🔄</span>
            <span>Load Articles</span>
        </button>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-articles">0</div>
                <div class="stat-label">Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-time">0</div>
                <div class="stat-label">Minutes</div>
            </div>
        </div>

        <div id="articles-container">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading articles...</p>
            </div>
        </div>
    </div>

    <script>
        let articles = [];
        let activeAudio = null;

        // Auto-load on page load
        window.addEventListener('DOMContentLoaded', loadArticles);

        async function loadArticles() {
            const container = document.getElementById('articles-container');
            container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading articles...</p></div>';

            try {
                const response = await fetch('/library');
                if (!response.ok) throw new Error('Failed to load');
                
                articles = await response.json();
                
                if (articles.length === 0) {
                    container.innerHTML = `
                        <div class="empty">
                            <div class="empty-icon">📚</div>
                            <h2>No articles yet</h2>
                            <p>Convert articles with the Chrome extension</p>
                        </div>
                    `;
                } else {
                    displayArticles();
                    updateStats();
                }
            } catch (error) {
                console.error('Error:', error);
                container.innerHTML = `
                    <div class="empty">
                        <div class="empty-icon">❌</div>
                        <h2>Error loading articles</h2>
                        <p>Please try again</p>
                    </div>
                `;
            }
        }

        function displayArticles() {
            const container = document.getElementById('articles-container');
            container.innerHTML = articles.map(article => createArticleCard(article)).join('');
        }

        function createArticleCard(article) {
            const voiceName = article.voice.replace('en-US-', '').replace('Neural', '');
            const minutes = Math.ceil(article.word_count / 150);
            
            return `
                <div class="article-card">
                    <h3 class="article-title">${article.title}</h3>
                    <div class="article-meta">
                        <span>📝 ${article.word_count} words</span>
                        <span>⏱️ ${minutes} min</span>
                        <span>🎤 ${voiceName}</span>
                    </div>
                    
                    <audio controls id="audio-${article.id}" src="${article.audio_url}"></audio>
                    
                    <div class="speed-controls">
                        <button class="speed-btn" onclick="setSpeed('${article.id}', 0.75)">0.75x</button>
                        <button class="speed-btn active" onclick="setSpeed('${article.id}', 1)">1x</button>
                        <button class="speed-btn" onclick="setSpeed('${article.id}', 1.25)">1.25x</button>
                        <button class="speed-btn" onclick="setSpeed('${article.id}', 1.5)">1.5x</button>
                        <button class="speed-btn" onclick="setSpeed('${article.id}', 2)">2x</button>
                    </div>
                    
                    <div class="actions">
                        <button class="action-btn favorite ${article.is_favorite ? 'active' : ''}" onclick="toggleFavorite('${article.id}', this)">
                            <span>${article.is_favorite ? '❤️' : '🤍'}</span>
                            <span>Favorite</span>
                        </button>
                        <button class="action-btn" onclick="deleteArticle('${article.id}')">
                            <span>🗑️</span>
                            <span>Delete</span>
                        </button>
                    </div>
                </div>
            `;
        }

        function setSpeed(articleId, speed) {
            const audio = document.getElementById(`audio-${articleId}`);
            if (audio) {
                audio.playbackRate = speed;
                
                // Update button states
                const card = audio.closest('.article-card');
                const buttons = card.querySelectorAll('.speed-btn');
                buttons.forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.textContent === `${speed}x`) {
                        btn.classList.add('active');
                    }
                });
            }
        }

        async function toggleFavorite(articleId, btn) {
            try {
                const response = await fetch(`/article/${articleId}/favorite`, {
                    method: 'PUT'
                });
                
                if (response.ok) {
                    const article = articles.find(a => a.id === articleId);
                    article.is_favorite = !article.is_favorite;
                    
                    btn.classList.toggle('active');
                    btn.querySelector('span:first-child').textContent = article.is_favorite ? '❤️' : '🤍';
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function deleteArticle(articleId) {
            if (!confirm('Delete this article?')) return;
            
            try {
                const response = await fetch(`/article/${articleId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    articles = articles.filter(a => a.id !== articleId);
                    displayArticles();
                    updateStats();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function updateStats() {
            document.getElementById('total-articles').textContent = articles.length;
            document.getElementById('total-time').textContent = Math.ceil(
                articles.reduce((sum, a) => sum + (a.word_count / 150), 0)
            );
        }
    </script>
</body>
</html>"""

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

@app.post("/refresh-db")
async def refresh_database():
    """Force refresh database connection"""
    global supabase
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            test = supabase.table('articles').select('id').limit(1).execute()
            return {"status": "refreshed", "connected": True}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "no_config"}

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
        # Prepare base64 audio for storage (works even without storage bucket)
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_url = f"data:audio/mpeg;base64,{audio_base64}"
        
        if supabase and request.save:
            try:
                # Try to use Supabase storage if available
                try:
                    storage_path = f"audio/{audio_filename}"
                    supabase.storage.from_('audio-files').upload(
                        storage_path, 
                        audio_data,
                        {"content-type": "audio/mpeg"}
                    )
                    # If storage works, use the public URL
                    audio_url = supabase.storage.from_('audio-files').get_public_url(storage_path)
                    print(f"✅ Uploaded to storage: {storage_path}")
                except Exception as storage_error:
                    print(f"⚠️ Storage upload failed (using base64): {storage_error}")
                    # Keep using base64 URL
                
                # Always store metadata in database (with base64 or storage URL)
                article_data = {
                    'title': request.title,
                    'content': request.content,
                    'audio_url': audio_url,  # Either storage URL or base64
                    'audio_filename': audio_filename,
                    'source_url': request.url,
                    'voice': request.voice,
                    'is_favorite': request.is_favorite,
                    'word_count': word_count,
                    'metadata': request.metadata
                }
                
                result = supabase.table('articles').insert(article_data).execute()
                
                if result.data:
                    article = result.data[0]
                    print(f"✅ Stored in database: {article['id']}")
                    
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
                print(f"⚠️ Database save failed: {e}")
        
        # Fallback - return audio without saving
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
        query = supabase.table('articles').select('*')
        
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
        result = supabase.table('articles').select('*').eq('id', article_id).execute()
        
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
        result = supabase.table('articles').select('is_favorite').eq('id', article_id).execute()
        
        if result.data:
            current_status = result.data[0]['is_favorite']
            new_status = not current_status
            
            # Update status
            update_result = supabase.table('articles').update({
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
        result = supabase.table('articles').select('audio_filename').eq('id', article_id).execute()
        
        if result.data:
            audio_filename = result.data[0].get('audio_filename')
            
            # Delete from storage if exists
            if audio_filename:
                try:
                    supabase.storage.from_('audio-files').remove([f"audio/{audio_filename}"])
                except Exception as e:
                    print(f"⚠️ Failed to delete audio file: {e}")
            
            # Delete from database
            delete_result = supabase.table('articles').delete().eq('id', article_id).execute()
            
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
        result = supabase.table('articles').select('*')\
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
        all_articles = supabase.table('articles').select('id', count='exact').execute()
        favorites = supabase.table('articles').select('id', count='exact').eq('is_favorite', True).execute()
        
        # Get total words
        word_count_result = supabase.table('articles').select('word_count').execute()
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