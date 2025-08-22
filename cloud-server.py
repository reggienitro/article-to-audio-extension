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
    
    # Force mobile interface for testing
    is_mobile = True  # Temporarily force mobile interface
    
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
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Audio Library - Listen Anywhere</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --light: #f9fafb;
            --gray: #6b7280;
            --radius: 12px;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding-bottom: 80px;
        }

        /* Dark mode */
        body.dark-mode {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }

        body.dark-mode .container {
            background: #1f2937;
            color: #f9fafb;
        }

        body.dark-mode .article-card {
            background: #374151;
            border-color: #4b5563;
        }

        body.dark-mode .btn-secondary {
            background: #4b5563;
        }

        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        body.dark-mode .header {
            background: rgba(31, 41, 55, 0.95);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.25rem;
            font-weight: bold;
            color: var(--primary);
        }

        .header-actions {
            display: flex;
            gap: 0.5rem;
        }

        /* Container */
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 1rem;
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
        }

        /* Stats Bar */
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: var(--light);
            border-radius: var(--radius);
        }

        body.dark-mode .stats-bar {
            background: #374151;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--gray);
            margin-top: 0.25rem;
        }

        /* Search and Filter */
        .controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }

        .search-box {
            flex: 1;
            min-width: 200px;
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.5rem;
            border: 2px solid #e5e7eb;
            border-radius: var(--radius);
            font-size: 1rem;
            transition: all 0.3s;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray);
        }

        /* Buttons */
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: var(--radius);
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .btn-secondary {
            background: var(--light);
            color: var(--dark);
        }

        .btn-secondary:hover {
            background: #e5e7eb;
        }

        .btn-icon {
            width: 2.5rem;
            height: 2.5rem;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }

        /* Article Cards */
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }

        .article-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: var(--radius);
            padding: 1.5rem;
            transition: all 0.3s;
            position: relative;
        }

        .article-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }

        .article-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
        }

        .article-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }

        body.dark-mode .article-title {
            color: var(--light);
        }

        .article-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--gray);
            margin-bottom: 1rem;
        }

        .meta-item {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        /* Audio Player */
        .audio-player {
            background: var(--light);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
        }

        body.dark-mode .audio-player {
            background: #1f2937;
        }

        .audio-element {
            width: 100%;
            margin-bottom: 1rem;
        }

        .player-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .speed-controls {
            display: flex;
            gap: 0.25rem;
        }

        .speed-btn {
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            border: 1px solid #e5e7eb;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .speed-btn:hover {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        .speed-btn.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        body.dark-mode .speed-btn {
            background: #374151;
            border-color: #4b5563;
            color: var(--light);
        }

        body.dark-mode .speed-btn.active {
            background: var(--primary);
            border-color: var(--primary);
        }

        /* Voice Selector */
        .voice-selector {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .voice-dropdown {
            padding: 0.5rem;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: white;
            cursor: pointer;
        }

        body.dark-mode .voice-dropdown {
            background: #374151;
            border-color: #4b5563;
            color: var(--light);
        }

        /* Article Actions */
        .article-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: space-between;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
        }

        .action-btn {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #e5e7eb;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.25rem;
            font-size: 0.875rem;
        }

        body.dark-mode .action-btn {
            background: #374151;
            border-color: #4b5563;
            color: var(--light);
        }

        .action-btn:hover {
            background: var(--light);
        }

        .action-btn.active {
            color: var(--danger);
        }

        /* Loading State */
        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--gray);
        }

        .spinner {
            border: 3px solid var(--light);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--gray);
        }

        .empty-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }

        /* Floating Action Button */
        .fab {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            border: none;
            box-shadow: var(--shadow-lg);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            transition: all 0.3s;
            z-index: 1000;
        }

        .fab:hover {
            transform: scale(1.1);
            background: var(--primary-dark);
        }

        /* Toast Notifications */
        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: var(--dark);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 2000;
        }

        .toast.show {
            opacity: 1;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                margin: 1rem;
                padding: 0.75rem;
            }

            .articles-grid {
                grid-template-columns: 1fr;
            }

            .controls {
                flex-direction: column;
            }

            .search-box {
                width: 100%;
            }

            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <span>🎧</span>
                <span>Audio Library</span>
            </div>
            <div class="header-actions">
                <button class="btn btn-icon btn-secondary" onclick="toggleDarkMode()" title="Toggle Dark Mode">
                    <span id="theme-icon">🌙</span>
                </button>
                <button class="btn btn-primary" onclick="loadArticles()">
                    <span>🔄</span>
                    <span>Refresh</span>
                </button>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value" id="total-articles">0</div>
                <div class="stat-label">Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="total-time">0</div>
                <div class="stat-label">Minutes</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="favorites-count">0</div>
                <div class="stat-label">Favorites</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="listened-count">0</div>
                <div class="stat-label">Listened</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-input" placeholder="Search articles..." id="search-input" onkeyup="filterArticles()">
            </div>
            <select class="btn btn-secondary" id="sort-select" onchange="sortArticles()">
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="longest">Longest First</option>
                <option value="shortest">Shortest First</option>
                <option value="favorites">Favorites First</option>
            </select>
            <select class="btn btn-secondary" id="filter-voice" onchange="filterArticles()">
                <option value="all">All Voices</option>
                <option value="Christopher">Christopher</option>
                <option value="Brian">Brian</option>
                <option value="Emma">Emma</option>
                <option value="Jenny">Jenny</option>
            </select>
        </div>

        <div id="articles-container">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading your audio library...</p>
            </div>
        </div>
    </div>

    <button class="fab" onclick="loadArticles()" title="Reload Articles">
        🔄
    </button>

    <div class="toast" id="toast"></div>

    <script>
        let articles = [];
        let currentlyPlaying = null;
        let listenedArticles = new Set(JSON.parse(localStorage.getItem('listenedArticles') || '[]'));

        // Load articles on page load
        window.addEventListener('DOMContentLoaded', () => {
            loadArticles();
            applyTheme();
        });

        async function loadArticles() {
            const container = document.getElementById('articles-container');
            container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading your audio library...</p></div>';

            try {
                const response = await fetch('/library');
                articles = await response.json();
                
                if (articles.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">📚</div>
                            <h2>No articles yet</h2>
                            <p>Convert articles with the Chrome extension to see them here</p>
                        </div>
                    `;
                } else {
                    displayArticles(articles);
                    updateStats();
                }
            } catch (error) {
                console.error('Error loading articles:', error);
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <h2>Error loading articles</h2>
                        <p>Please try refreshing the page</p>
                    </div>
                `;
            }
        }

        function displayArticles(articlesToShow) {
            const container = document.getElementById('articles-container');
            container.innerHTML = '<div class="articles-grid">' + articlesToShow.map(article => createArticleCard(article)).join('') + '</div>';
            
            // Restore audio states
            articlesToShow.forEach(article => {
                const audio = document.getElementById(`audio-${article.id}`);
                if (audio) {
                    audio.addEventListener('ended', () => markAsListened(article.id));
                }
            });
        }

        function createArticleCard(article) {
            const isListened = listenedArticles.has(article.id);
            const voiceName = article.voice.replace('en-US-', '').replace('Neural', '');
            const estimatedMinutes = Math.ceil(article.word_count / 150);
            
            return `
                <div class="article-card" id="card-${article.id}">
                    <div class="article-header">
                        <div>
                            <h3 class="article-title">${article.title}</h3>
                            <div class="article-meta">
                                <span class="meta-item">📝 ${article.word_count} words</span>
                                <span class="meta-item">⏱️ ~${estimatedMinutes} min</span>
                                <span class="meta-item">🎤 ${voiceName}</span>
                            </div>
                        </div>
                        ${isListened ? '<span title="Listened">✅</span>' : ''}
                    </div>
                    
                    <div class="audio-player">
                        <audio controls class="audio-element" id="audio-${article.id}" src="${article.audio_url}"></audio>
                        
                        <div class="player-controls">
                            <div class="speed-controls">
                                <button class="speed-btn" onclick="setSpeed('${article.id}', 0.75)">0.75x</button>
                                <button class="speed-btn active" onclick="setSpeed('${article.id}', 1)">1x</button>
                                <button class="speed-btn" onclick="setSpeed('${article.id}', 1.25)">1.25x</button>
                                <button class="speed-btn" onclick="setSpeed('${article.id}', 1.5)">1.5x</button>
                                <button class="speed-btn" onclick="setSpeed('${article.id}', 2)">2x</button>
                            </div>
                            
                            <div class="voice-selector">
                                <select class="voice-dropdown" onchange="changeVoice('${article.id}', this.value)" disabled title="Coming soon">
                                    <option value="${article.voice}">${voiceName}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="article-actions">
                        <button class="action-btn ${article.is_favorite ? 'active' : ''}" onclick="toggleFavorite('${article.id}')">
                            ${article.is_favorite ? '❤️' : '🤍'} Favorite
                        </button>
                        <button class="action-btn" onclick="shareArticle('${article.id}')">
                            📤 Share
                        </button>
                        <button class="action-btn" onclick="deleteArticle('${article.id}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `;
        }

        function setSpeed(articleId, speed) {
            const audio = document.getElementById(`audio-${articleId}`);
            if (audio) {
                audio.playbackRate = speed;
                
                // Update active button
                const card = document.getElementById(`card-${articleId}`);
                const buttons = card.querySelectorAll('.speed-btn');
                buttons.forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.textContent === `${speed}x`) {
                        btn.classList.add('active');
                    }
                });
                
                showToast(`Playback speed: ${speed}x`);
            }
        }

        async function toggleFavorite(articleId) {
            try {
                const response = await fetch(`/article/${articleId}/favorite`, {
                    method: 'PUT'
                });
                
                if (response.ok) {
                    const article = articles.find(a => a.id === articleId);
                    article.is_favorite = !article.is_favorite;
                    displayArticles(articles);
                    updateStats();
                    showToast(article.is_favorite ? 'Added to favorites' : 'Removed from favorites');
                }
            } catch (error) {
                console.error('Error toggling favorite:', error);
                showToast('Error updating favorite status');
            }
        }

        async function deleteArticle(articleId) {
            if (!confirm('Are you sure you want to delete this article?')) return;
            
            try {
                const response = await fetch(`/article/${articleId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    articles = articles.filter(a => a.id !== articleId);
                    displayArticles(articles);
                    updateStats();
                    showToast('Article deleted');
                }
            } catch (error) {
                console.error('Error deleting article:', error);
                showToast('Error deleting article');
            }
        }

        function shareArticle(articleId) {
            const article = articles.find(a => a.id === articleId);
            const url = article.source_url || window.location.href;
            
            if (navigator.share) {
                navigator.share({
                    title: article.title,
                    text: `Listen to: ${article.title}`,
                    url: url
                });
            } else {
                navigator.clipboard.writeText(url);
                showToast('Link copied to clipboard!');
            }
        }

        function filterArticles() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const voiceFilter = document.getElementById('filter-voice').value;
            
            let filtered = articles;
            
            if (searchTerm) {
                filtered = filtered.filter(a => 
                    a.title.toLowerCase().includes(searchTerm) ||
                    a.content.toLowerCase().includes(searchTerm)
                );
            }
            
            if (voiceFilter !== 'all') {
                filtered = filtered.filter(a => 
                    a.voice.includes(voiceFilter)
                );
            }
            
            displayArticles(filtered);
        }

        function sortArticles() {
            const sortBy = document.getElementById('sort-select').value;
            let sorted = [...articles];
            
            switch(sortBy) {
                case 'newest':
                    sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                    break;
                case 'oldest':
                    sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
                    break;
                case 'longest':
                    sorted.sort((a, b) => b.word_count - a.word_count);
                    break;
                case 'shortest':
                    sorted.sort((a, b) => a.word_count - b.word_count);
                    break;
                case 'favorites':
                    sorted.sort((a, b) => b.is_favorite - a.is_favorite);
                    break;
            }
            
            displayArticles(sorted);
        }

        function updateStats() {
            document.getElementById('total-articles').textContent = articles.length;
            document.getElementById('total-time').textContent = Math.ceil(articles.reduce((sum, a) => sum + (a.word_count / 150), 0));
            document.getElementById('favorites-count').textContent = articles.filter(a => a.is_favorite).length;
            document.getElementById('listened-count').textContent = listenedArticles.size;
        }

        function markAsListened(articleId) {
            listenedArticles.add(articleId);
            localStorage.setItem('listenedArticles', JSON.stringify([...listenedArticles]));
            displayArticles(articles);
            updateStats();
        }

        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            document.getElementById('theme-icon').textContent = isDark ? '☀️' : '🌙';
        }

        function applyTheme() {
            const isDark = localStorage.getItem('darkMode') === 'true';
            if (isDark) {
                document.body.classList.add('dark-mode');
                document.getElementById('theme-icon').textContent = '☀️';
            }
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        // Change voice (for future implementation with re-conversion)
        async function changeVoice(articleId, newVoice) {
            // This would trigger a re-conversion with the new voice
            showToast('Voice change coming soon!');
        }
    </script>
</body>
</html>
"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Library</title>
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
        <h1>🎧 Audio Library</h1>
        <p>Chrome Extension Conversions</p>
    </div>
    
    <div style="padding: 15px;">
        <button onclick="loadLibrary()" style="width: 100%; padding: 15px; background: #4CAF50; color: white; border: none; border-radius: 8px; font-size: 16px; margin-bottom: 20px;">
            🔄 Load My Audio
        </button>
        <div id="audioList"></div>
    </div>

    <script>
        function loadLibrary() {
            const list = document.getElementById('audioList');
            list.innerHTML = '<p>Loading...</p>';
            
            fetch('/library')
                .then(response => response.json())
                .then(articles => {
                    if (articles.length === 0) {
                        list.innerHTML = '<p>No audio yet. Use Chrome extension to convert articles!</p>';
                        return;
                    }
                    
                    list.innerHTML = articles.map(article => `
                        <div style="background: rgba(255,255,255,0.1); padding: 15px; margin: 10px 0; border-radius: 8px;">
                            <h3>${article.title}</h3>
                            <audio controls style="width: 100%; margin: 10px 0;">
                                <source src="${article.audio_url}" type="audio/mpeg">
                            </audio>
                            <div style="margin-top: 10px;">
                                <button onclick="changeSpeed(this, 0.75)">0.75x</button>
                                <button onclick="changeSpeed(this, 1.0)">1x</button>
                                <button onclick="changeSpeed(this, 1.25)">1.25x</button>
                                <button onclick="changeSpeed(this, 1.5)">1.5x</button>
                            </div>
                            <p>${article.word_count} words</p>
                        </div>
                    `).join('');
                })
                .catch(error => {
                    list.innerHTML = '<p>Error loading. Click "Load My Audio" to try again.</p>';
                });
        }
        
        function changeSpeed(btn, speed) {
            const audio = btn.parentElement.parentElement.querySelector('audio');
            audio.playbackRate = speed;
        }
        
        // Load on page load
        loadLibrary();
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