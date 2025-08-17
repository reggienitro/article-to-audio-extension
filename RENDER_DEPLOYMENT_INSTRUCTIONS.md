# Render Deployment Instructions

## 🚀 Deploy Article-to-Audio to Render

### Step 1: Create Render Account & Connect GitHub
1. Go to **https://dashboard.render.com**
2. Sign up/login with your GitHub account
3. Click **"New +"** → **"Web Service"**
4. **Connect your GitHub repository**

### Step 2: Configure Service
**Repository Settings:**
- Repository: `article-to-audio-extension`
- Branch: `mac-claude`
- Root Directory: *(leave blank)*

**Build & Deploy Settings:**
- Environment: **Python 3**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python cloud-server.py`
- Instance Type: **Free** (sufficient for testing)

### Step 3: Environment Variables
*(These are already configured in render.yaml, but verify:)*

```yaml
PORT: 8000
SUPABASE_URL: https://qslpqxjoupwyclmguniz.supabase.co
SUPABASE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A
EDGE_TTS_VOICE: en-US-BrianNeural
DEFAULT_STORAGE_MODE: cloud
AUTO_SYNC: true
USER_EMAIL: aettefagh@gmail.com
```

### Step 4: Deploy
1. Click **"Create Web Service"**
2. **Monitor build logs** - should take 2-3 minutes
3. Wait for **"Live"** status
4. **Note the deployment URL** (e.g., `https://article-to-audio-server.onrender.com`)

### Step 5: Test Deployment

#### Health Check
```bash
curl https://YOUR-APP-NAME.onrender.com/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-17T...",
  "supabase_connected": true
}
```

#### Test Article Conversion
```bash
curl -X POST https://YOUR-APP-NAME.onrender.com/convert \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Test",
    "content": "This is a production test article for the deployed service.",
    "voice": "en-US-BrianNeural",
    "user_email": "test@example.com"
  }'
```

### Step 6: Update Chrome Extension
1. **Edit `popup.js`** in your extension
2. **Change SERVER_URL** to your Render URL:
   ```javascript
   const SERVER_URL = 'https://YOUR-APP-NAME.onrender.com';
   ```
3. **Reload extension** in `chrome://extensions`
4. **Test with real article**

## 🔧 Troubleshooting

### Build Failures
- Check **build logs** in Render dashboard
- Verify **requirements.txt** has all dependencies
- Ensure **Python version compatibility**

### Startup Failures
- Check **application logs** in Render
- Verify **environment variables** are set
- Test **Supabase connection**

### API Errors
- Check **CORS settings** in cloud-server.py
- Verify **Supabase credentials**
- Test **health endpoint** first

### Performance Issues
- Render free tier has **limitations**
- Monitor **memory usage**
- Consider **upgrade** if needed

## 📊 Monitoring

### After Deployment
```bash
# Start monitoring (run locally)
python3 production_monitor.py --url https://YOUR-APP-NAME.onrender.com

# Or single test
python3 production_monitor.py --test --url https://YOUR-APP-NAME.onrender.com
```

### Render Dashboard
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Request count
- **Events**: Deployment history
- **Settings**: Environment variables, scaling

## ✅ Success Criteria

**Deployment Successful When:**
- [ ] ✅ Service shows "Live" status
- [ ] ✅ Health endpoint returns 200 OK
- [ ] ✅ Article conversion works
- [ ] ✅ Audio files are generated
- [ ] ✅ Chrome extension connects
- [ ] ✅ No errors in logs

**Ready for Production When:**
- [ ] ✅ Response time < 30s for conversion
- [ ] ✅ Memory usage stable
- [ ] ✅ Multiple test articles work
- [ ] ✅ Mobile playback functional

## 🔄 Next Steps After Deployment

1. **Test thoroughly** with various articles
2. **Update project documentation** with Render URL
3. **Share with users** for testing
4. **Monitor performance** and errors
5. **Plan feature enhancements**

---

**All configuration files are ready!**
**Just follow these steps and you'll be live in minutes!**