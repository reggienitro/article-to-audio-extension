# Article-to-Audio Server Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended)
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Deploy as Web Service with these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python cloud-server.py`
   - **Plan**: Free
   - **Environment Variables**: See below

### Option 2: Railway
1. Create account at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy automatically using `railway.toml` configuration

### Option 3: Fly.io
1. Install Fly CLI: `brew install flyctl`
2. Login: `fly auth login`
3. Deploy: `fly deploy`

### Option 4: Docker (Self-hosted)
```bash
# Build and run locally
docker compose up -d

# Or build manually
docker build -t article-audio-server .
docker run -p 8000:8000 article-audio-server
```

## 🔧 Environment Variables

### Required (None! Server works out of the box)
- Server works completely locally without any external dependencies

### Optional Supabase Integration
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key

### Optional Configuration
- `PORT`: Server port (default: 8000)
- `EDGE_TTS_VOICE`: Default voice (default: en-US-BrianNeural)
- `DEFAULT_STORAGE_MODE`: local/cloud/ask (default: local)
- `AUTO_SYNC`: true/false (default: false)

## 📱 Usage After Deployment

### Web Interface
- **Main UI**: `https://your-domain.com/`
- **Mobile UI**: `https://your-domain.com/mobile`
- **API Docs**: `https://your-domain.com/docs`

### API Endpoints
- `POST /convert` - Convert article to audio
- `GET /health` - Health check
- `GET /audio/{filename}` - Download audio files
- `POST /favorites/{article_id}/toggle` - Toggle favorites (if Supabase connected)

### Example API Usage
```bash
curl -X POST https://your-domain.com/convert \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "content": "Your article content here...",
    "voice": "en-US-ChristopherNeural",
    "speed": "normal"
  }'
```

## 🔍 Features

### ✅ Working Out of the Box
- **Article-to-Audio Conversion**: Edge TTS with 6+ voices
- **Speed Control**: slow/normal/fast/very_fast
- **Local Storage**: Files saved to `/output` directory
- **Mobile-Optimized UI**: Touch-friendly interface
- **Chunking Support**: Handles long articles (26K+ chars)
- **Cross-Platform**: Works on any device with web browser

### ✅ Optional Cloud Features (when Supabase configured)
- **User Authentication**: Sign up/sign in
- **Cloud Storage**: Cross-device sync
- **Favorites**: Star important articles
- **History**: Track conversions

## 🧪 Testing Deployment

### Health Check
```bash
curl https://your-domain.com/health
# Should return: {"status":"healthy","supabase_connected":false,"timestamp":"..."}
```

### Test Conversion
1. Open `https://your-domain.com/` in browser
2. Paste article text or URL
3. Select voice and speed
4. Click "Convert to Audio"
5. Download and play the MP3 file

### Mobile Test
1. Open `https://your-domain.com/mobile` on phone
2. Should see mobile-optimized interface
3. Test conversion and playback

## 🛠 Troubleshooting

### Common Issues

**Server won't start**
- Check PORT environment variable
- Verify all dependencies in requirements.txt are available

**Audio conversion fails**
- Check article content is sufficient (50+ chars)
- Verify Edge TTS voice name is valid

**Files not accessible**
- Ensure output directory has write permissions
- Check disk space on deployment platform

**Mobile UI not loading**
- Verify mobile-app.html is deployed
- Check CORS settings allow your domain

### Debug Mode
Enable verbose logging by setting environment variable:
```
DEBUG=true
```

## 📦 Dependencies

### Python Packages (requirements.txt)
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- edge-tts>=6.1.0
- supabase>=2.0.0 (optional)
- python-dotenv>=1.0.0

### System Requirements
- Python 3.11+
- ~100MB disk space for audio files
- Internet connection for Edge TTS

## 🔐 Security Notes

- Server allows CORS from all origins for development
- No authentication required for local storage mode
- Supabase integration adds optional user auth
- API keys should be set as environment variables, never committed

## 🎯 Success Metrics

After deployment, you should be able to:
1. ✅ Convert articles to audio via web interface
2. ✅ Access from any device with internet connection
3. ✅ Download MP3 files directly
4. ✅ Use mobile-optimized interface on phone
5. ✅ API integration for external apps

---

**Ready to deploy!** The server is production-ready and will work immediately after deployment, even without any configuration.