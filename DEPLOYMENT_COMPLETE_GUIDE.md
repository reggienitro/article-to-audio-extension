# Article-to-Audio Supabase Cloud Deployment Guide

## Project Overview
Complete deployment guide for Article-to-Audio service with Supabase integration and Render hosting.

## Architecture
- **Frontend**: Chrome Extension + Web UI
- **Backend**: FastAPI (Python) server
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage for audio files
- **Hosting**: Render.com
- **TTS Engine**: Edge-TTS

## Prerequisites Completed ✅
- [x] Supabase project created (qslpqxjoupwyclmguniz)
- [x] Schema files prepared and tested
- [x] FastAPI server implemented with Supabase integration
- [x] Test suite created
- [x] Deployment configurations ready
- [x] Environment variables configured

## 1. Database Schema Setup

### Clean Schema File
Use `article2audio_schema_clean.sql` - this has been cleaned of comment issues:

```sql
/* Execute this in Supabase SQL Editor */
/* URL: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz/sql */
```

### What the Schema Creates:
1. **articles table**: Stores article metadata, audio URLs, user preferences
2. **audio-files bucket**: Cloud storage for generated audio files
3. **Storage policies**: Public read, authenticated upload
4. **Performance indexes**: On created_at, user_email, is_favorite
5. **Update trigger**: Auto-updates updated_at timestamp

### Schema Verification
After executing, run:
```bash
python3 verify_schema_execution.py
```

## 2. Local Testing

### Start Local Server
```bash
cd "/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension"
python3 cloud-server.py
```

### Run Test Suite
```bash
# In another terminal
python3 test_supabase_connection.py  # Test database
python3 test_integration.py          # Test API endpoints
python3 test_deployment.py           # Check deployment readiness
```

## 3. Render Deployment

### Deployment Configuration (render.yaml)
```yaml
services:
  - type: web
    name: article-to-audio-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python cloud-server.py
    plan: free
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: 8000
      - key: SUPABASE_URL
        value: https://qslpqxjoupwyclmguniz.supabase.co
      - key: SUPABASE_KEY
        value: [anon key configured]
      - key: EDGE_TTS_VOICE
        value: en-US-BrianNeural
      - key: DEFAULT_STORAGE_MODE
        value: cloud
      - key: AUTO_SYNC
        value: true
```

### Deployment Steps
1. **Connect GitHub Repository**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub account
   - Select repository: article-to-audio-extension
   - Select branch: mac-claude

2. **Configure Service**
   - Name: article-to-audio-server
   - Root Directory: (leave blank)
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python cloud-server.py`

3. **Environment Variables**
   Already configured in render.yaml, but verify:
   - SUPABASE_URL
   - SUPABASE_KEY
   - PORT (8000)
   - EDGE_TTS_VOICE
   - DEFAULT_STORAGE_MODE (cloud)

4. **Deploy**
   - Click "Create Web Service"
   - Monitor deployment logs
   - Wait for "Live" status

## 4. API Endpoints

### Health Check
```bash
GET /health
```

### User Management
```bash
POST /signup
{
  "email": "user@example.com",
  "display_name": "User Name"
}

POST /signin
{
  "email": "user@example.com"
}

GET /user/{email}
```

### Article Conversion
```bash
POST /convert
{
  "url": "https://article-url.com",
  "title": "Article Title",
  "content": "Article content...",
  "voice": "en-US-BrianNeural",
  "user_email": "user@example.com"
}
```

### Library Management
```bash
GET /library/{user_email}
GET /articles/{article_id}
PUT /articles/{article_id}
DELETE /articles/{article_id}
```

### Audio Storage
```bash
POST /upload-audio
(multipart/form-data with audio file)
```

## 5. Chrome Extension Configuration

### Update Extension Settings
Edit `popup.js` to point to deployed server:
```javascript
const SERVER_URL = 'https://article-to-audio-server.onrender.com';
```

### Reload Extension
1. Go to chrome://extensions
2. Click "Reload" on Article-to-Audio extension
3. Test with real article

## 6. Testing Production

### Basic Health Check
```bash
curl https://article-to-audio-server.onrender.com/health
```

### Test Article Conversion
```bash
curl -X POST https://article-to-audio-server.onrender.com/convert \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "title": "Test Article",
    "content": "Test content for audio conversion.",
    "voice": "en-US-BrianNeural",
    "user_email": "test@example.com"
  }'
```

### Update Integration Test
```python
# In test_integration.py, update:
BASE_URL = "https://article-to-audio-server.onrender.com"
```

## 7. Monitoring & Maintenance

### Render Dashboard
- View logs: https://dashboard.render.com → Service → Logs
- Monitor metrics: CPU, Memory, Request count
- Set up alerts for failures

### Supabase Dashboard
- Monitor database: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz
- Check storage usage: Storage → Buckets → audio-files
- View table data: Table Editor → articles

### Health Monitoring Script
```python
import requests
import time

def monitor_health():
    url = "https://article-to-audio-server.onrender.com/health"
    while True:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Service healthy: {response.json()}")
            else:
                print(f"⚠️ Service issue: {response.status_code}")
        except Exception as e:
            print(f"❌ Service down: {e}")
        time.sleep(60)  # Check every minute

monitor_health()
```

## 8. Troubleshooting

### Common Issues

#### Schema Execution Errors
- Remove SQL comments starting with `--`
- Use `/* */` for comments or remove entirely
- Execute statements one by one if needed

#### Deployment Failures
- Check requirements.txt has all dependencies
- Verify Python version compatibility
- Check environment variables in Render

#### API Connection Issues
- Verify CORS settings in cloud-server.py
- Check Supabase credentials
- Ensure storage bucket policies are correct

#### Audio Generation Failures
- Verify edge-tts is installed
- Check voice name is valid
- Ensure adequate disk space on Render

### Debug Commands
```bash
# Check Supabase connection
python3 -c "from supabase import create_client; client = create_client('URL', 'KEY'); print('Connected')"

# Test edge-tts
edge-tts --list-voices | grep en-US

# Check server startup
python3 cloud-server.py --debug
```

## 9. Security Considerations

### API Security
- Anon key is safe for client-side use
- Service key should never be exposed
- Implement rate limiting if needed
- Add authentication for sensitive endpoints

### Data Privacy
- User emails stored securely
- Audio files in public bucket (by design)
- Consider encryption for sensitive content
- Regular security audits

## 10. Future Enhancements

### Planned Features
- [ ] User authentication with Supabase Auth
- [ ] Premium features with payment integration
- [ ] Batch article processing
- [ ] Mobile app development
- [ ] Advanced voice customization
- [ ] Analytics dashboard

### Performance Optimizations
- [ ] CDN for audio delivery
- [ ] Caching layer for frequent articles
- [ ] Background job queue for processing
- [ ] Database query optimization

## Deployment Checklist

### Pre-Deployment
- [x] Schema files prepared
- [x] Test suite created
- [x] Environment variables configured
- [x] Git repository updated
- [ ] Schema executed in Supabase

### Deployment
- [ ] Render service created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health check passing

### Post-Deployment
- [ ] Production API tested
- [ ] Chrome extension updated
- [ ] User documentation updated
- [ ] Monitoring setup
- [ ] Backup strategy defined

## Support & Maintenance

### Regular Tasks
- Weekly: Check logs for errors
- Monthly: Review usage metrics
- Quarterly: Update dependencies
- Annually: Security audit

### Backup Strategy
- Database: Supabase automatic backups
- Audio files: Supabase storage redundancy
- Code: GitHub repository

### Contact & Resources
- Supabase Docs: https://supabase.com/docs
- Render Docs: https://render.com/docs
- Project Repo: https://github.com/[your-username]/article-to-audio-extension
- Issues: GitHub Issues page

---

**Last Updated**: 2025-08-17
**Status**: Ready for deployment after schema execution
**Version**: 1.0.0