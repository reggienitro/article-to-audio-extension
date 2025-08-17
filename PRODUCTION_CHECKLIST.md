# Article-to-Audio Production Deployment Checklist

## Pre-Deployment Checklist ✅

### Database Setup
- [x] Supabase project created (qslpqxjoupwyclmguniz)
- [ ] **CRITICAL**: Execute schema in Supabase SQL Editor
  - Copy from `article2audio_schema_clean.sql` (comment issues fixed)
  - URL: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz/sql
- [ ] Verify schema with: `python3 verify_schema_execution.py`
- [x] Storage bucket configured (audio-files)
- [x] Storage policies set (public read, auth upload)

### Code & Configuration
- [x] All code committed to git (mac-claude branch)
- [x] Environment variables configured in render.yaml
- [x] Requirements.txt updated with all dependencies
- [x] Health check endpoint implemented (/health)
- [x] CORS headers configured for browser extension
- [x] Error handling implemented
- [x] Test suite created and documented

### Testing
- [x] Schema verification script ready
- [x] Integration tests created
- [x] Deployment readiness tests created
- [x] Local server imports validated
- [x] API endpoints documented

## Deployment Steps

### 1. Final Schema Execution
```sql
-- Copy this to Supabase SQL Editor:
/* Execute in https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz/sql */

CREATE TABLE IF NOT EXISTS articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT,
    voice TEXT DEFAULT 'en-US-BrianNeural',
    speed TEXT DEFAULT 'normal',
    audio_url TEXT,
    audio_filename TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    user_email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-files', 'audio-files', true) 
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Public audio access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'audio-files');

CREATE POLICY "Authenticated audio upload" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'audio-files');

CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_user_email ON articles(user_email);
CREATE INDEX IF NOT EXISTS idx_articles_is_favorite ON articles(is_favorite);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO articles (title, content, voice, user_email) VALUES 
('Test Article', 'This is a test article to verify the schema is working correctly.', 'en-US-BrianNeural', 'aettefagh@gmail.com')
ON CONFLICT DO NOTHING;
```

### 2. Render Deployment
1. **Create Render Account & Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository

2. **Configure Service**
   - Repository: article-to-audio-extension
   - Branch: mac-claude
   - Root Directory: (leave blank)
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python cloud-server.py`

3. **Environment Variables** (Already in render.yaml)
   ```yaml
   PORT: 8000
   SUPABASE_URL: https://qslpqxjoupwyclmguniz.supabase.co
   SUPABASE_KEY: [configured in render.yaml]
   EDGE_TTS_VOICE: en-US-BrianNeural
   DEFAULT_STORAGE_MODE: cloud
   AUTO_SYNC: true
   USER_EMAIL: aettefagh@gmail.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Monitor build logs
   - Wait for "Live" status

### 3. Post-Deployment Verification

#### Health Check
```bash
curl https://article-to-audio-server.onrender.com/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-17T...",
  "version": "1.0.0",
  "supabase_connected": true
}
```

#### Test Article Conversion
```bash
curl -X POST https://article-to-audio-server.onrender.com/convert \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Test",
    "content": "This is a production test article.",
    "voice": "en-US-BrianNeural",
    "user_email": "test@example.com"
  }'
```

#### Run Full Integration Tests
```bash
# Update BASE_URL in test_integration.py first
python3 test_integration.py
```

### 4. Chrome Extension Update
1. **Update Server URL**
   - Edit `popup.js`
   - Change `SERVER_URL` to: `https://article-to-audio-server.onrender.com`

2. **Reload Extension**
   - Go to chrome://extensions
   - Click "Reload" on Article-to-Audio extension

3. **Test with Real Article**
   - Visit a news article
   - Click extension icon
   - Test conversion and playback

## Post-Deployment Monitoring

### Automated Monitoring
```bash
# Start production monitoring
python3 production_monitor.py

# Or run single test
python3 production_monitor.py --test

# Monitor for specific duration
python3 production_monitor.py --duration 60  # 60 minutes
```

### Manual Checks
- [ ] Service responding on Render URL
- [ ] Database queries working
- [ ] Audio file upload/download functional
- [ ] Chrome extension connecting to new server
- [ ] User signup/signin working
- [ ] Article conversion generating audio
- [ ] Audio playback in browser/mobile

### Performance Metrics
- [ ] Response time < 2 seconds for health check
- [ ] Response time < 30 seconds for article conversion
- [ ] Memory usage within Render limits
- [ ] No errors in application logs

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Schema Execution Fails
**Problem**: Syntax errors in SQL
**Solution**: Use `article2audio_schema_clean.sql` (fixed comments)

#### 2. Render Build Fails
**Problem**: Missing dependencies
**Solution**: Check requirements.txt, add missing packages

#### 3. Server Won't Start
**Problem**: Port conflicts or import errors
**Solution**: Check Render logs, verify file names

#### 4. Database Connection Fails
**Problem**: Wrong Supabase credentials
**Solution**: Verify SUPABASE_URL and SUPABASE_KEY in environment

#### 5. CORS Errors
**Problem**: Browser extension can't connect
**Solution**: Verify CORS headers in cloud-server.py

#### 6. Audio Generation Fails
**Problem**: Edge-TTS not working
**Solution**: Check voice names, ensure edge-tts installed

### Debug Commands
```bash
# Check Supabase connection
python3 -c "from supabase import create_client; client = create_client('URL', 'KEY'); print('Connected')"

# Test edge-tts
edge-tts --list-voices | grep en-US

# Check API endpoint
curl -v https://article-to-audio-server.onrender.com/health
```

## Security & Maintenance

### Security Checklist
- [x] Anon key used (safe for client-side)
- [x] No service key exposed
- [x] HTTPS enforced by Render
- [x] Input validation in API endpoints
- [x] Error messages don't leak sensitive info

### Maintenance Schedule
- **Daily**: Check monitoring alerts
- **Weekly**: Review Render logs and metrics
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

### Backup Strategy
- **Database**: Supabase automatic backups enabled
- **Audio Files**: Supabase storage redundancy
- **Code**: Git repository with multiple branches

## Success Criteria

### Deployment Success
- [ ] ✅ Health check returns 200 OK
- [ ] ✅ Article conversion creates audio file
- [ ] ✅ Audio file accessible via URL
- [ ] ✅ Database operations (CRUD) working
- [ ] ✅ Chrome extension connects successfully
- [ ] ✅ No errors in Render logs

### Performance Success
- [ ] Response time < 2s for health check
- [ ] Response time < 30s for conversion
- [ ] 99%+ uptime over 24 hours
- [ ] Memory usage within limits

### User Experience Success
- [ ] Extension converts articles without errors
- [ ] Audio plays correctly in browser
- [ ] Library saves and retrieves articles
- [ ] Mobile playback works

## Emergency Procedures

### If Service Goes Down
1. Check Render dashboard for status
2. Review application logs
3. Check Supabase status
4. Restart service if needed
5. Roll back to previous deployment if critical

### If Database Issues
1. Check Supabase dashboard
2. Verify connection credentials
3. Test with simple query
4. Contact Supabase support if needed

### If Extension Stops Working
1. Check CORS headers
2. Verify server URL in popup.js
3. Test API endpoints manually
4. Reload extension in browser

---

**Deployment Status**: Ready (pending schema execution)
**Next Action**: Execute schema in Supabase SQL Editor
**Contact**: Review logs and documentation for issues