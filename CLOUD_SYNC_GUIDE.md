# 📱 Cloud Sync Setup Guide

Your article-to-audio system now supports **cross-device sync** for iPhone listening! Convert articles on your laptop and listen on your iPhone seamlessly.

## 🚀 Quick Setup (iCloud Drive)

### 1. Enable Cloud Sync
```bash
cd "/Users/aettefagh/model-finetuning-project"
python3 article2audio-enhanced --setup-cloud
```

Or enable quickly:
```bash
python3 article2audio-enhanced --enable-cloud
```

### 2. Check Status
```bash
python3 article2audio-enhanced --cloud-status
```

### 3. Convert Article with Cloud Sync
```bash
# Convert and save to both local library AND iCloud
python3 article2audio-enhanced "https://example.com/article" --save
```

The `--save` flag now:
- ✅ Saves to local audio library
- ☁️ **Automatically syncs to iCloud Drive**
- 📱 Makes available on iPhone

## 📱 iPhone Access

### Method 1: Files App (Recommended)
1. **Open Files app** on iPhone
2. **Browse → iCloud Drive**
3. **Open "ArticleAudio" folder**
4. **Tap any audio file** to play with native iOS player
5. **Download for offline** listening (tap and hold → Download)

### Method 2: Music App Integration
1. **Long-press audio file** in Files app
2. **Share → Add to Apple Music**
3. **Access from Music app** for better playback controls

## 🎧 Usage Workflow

### On Laptop/PC:
1. **Browse to any article** (NYT, Medium, BBC, etc.)
2. **Click browser extension** 🎧 
3. **Select "Convert Article to Audio"**
4. **Enable "Save to Library"** checkbox
5. **See confirmation**: "📱 Available on iPhone via iCloud Drive"

### On iPhone:
1. **Open Files app** → iCloud Drive → ArticleAudio
2. **See your converted articles** with descriptive filenames
3. **Tap to play immediately** or download for offline
4. **Perfect for commuting, workouts, etc.** 🚗🏃‍♂️

## 📋 File Organization

### Filename Format
```
20250810_195530_Article_Title_christopher.mp3
└─ Date/Time ─┘ └─ Title ─┘ └─Voice─┘
```

### Metadata Files
Each audio file gets a companion `.json` file with:
```json
{
  "title": "Article Title",
  "url": "https://original-article-url",
  "voice": "christopher",
  "speed": "fast",
  "created": "2025-08-10 19:55:30",
  "word_count": 1200,
  "file_size_mb": 4.5
}
```

## ⚙️ Configuration Options

### Check Current Settings
```bash
python3 article2audio-enhanced --cloud-status
```

### Disable Cloud Sync
```bash
python3 article2audio-enhanced --disable-cloud
```

### Re-enable Cloud Sync
```bash
python3 article2audio-enhanced --enable-cloud
```

## 🔧 Troubleshooting

### "iCloud Drive not available"
- **Check iCloud is signed in** on macOS
- **Enable iCloud Drive** in System Preferences → Apple ID → iCloud
- **Restart the application** after enabling iCloud

### "Files not appearing on iPhone"
- **Wait 30-60 seconds** for sync (files can be large)
- **Check iPhone iCloud storage** isn't full
- **Force refresh** Files app (swipe down in ArticleAudio folder)
- **Check network connection** on both devices

### "Permission denied" errors
- **Check iCloud Drive folder exists**: `~/Library/Mobile Documents/com~apple~CloudDocs/`
- **Verify write permissions** to iCloud folder
- **Try manually creating ArticleAudio folder** in iCloud Drive

## 📊 Storage Management

### File Sizes (Typical)
- **5-minute article**: ~2-3 MB
- **15-minute article**: ~6-8 MB  
- **30-minute article**: ~12-15 MB

### iCloud Storage
- **Free tier**: 5GB (enough for 300+ articles)
- **Upgrade options**: 50GB ($0.99/month), 200GB ($2.99/month)

### Cleanup Commands
```bash
# List all audio files with sizes
ls -lah ~/Library/Mobile\ Documents/com~apple~CloudDocs/ArticleAudio/

# Remove old files (older than 30 days)
find ~/Library/Mobile\ Documents/com~apple~CloudDocs/ArticleAudio/ -name "*.mp3" -mtime +30 -delete
```

## 🔮 Future Enhancements

### Coming Soon:
- **Google Drive integration** for cross-platform sync
- **Dropbox support** for team sharing
- **Mobile web interface** for direct iPhone conversion
- **Smart cleanup** based on listening history
- **Playlist management** for organized listening

### Advanced Features (Phase 2):
- **Direct streaming** from cloud storage
- **Offline download management** on iPhone
- **Shared libraries** for families/teams
- **Cross-device progress sync** (remember playback position)

## 🎯 Pro Tips

### Optimize for iPhone:
1. **Use descriptive article titles** for easy browsing
2. **Prefer shorter articles** (5-15 minutes) for mobile listening
3. **Download overnight** on WiFi for offline commute listening
4. **Use AirPods/headphones** for best experience

### Batch Processing:
```bash
# Convert multiple articles and auto-sync
python3 article2audio-enhanced "https://article1.com" --save
python3 article2audio-enhanced "https://article2.com" --save
python3 article2audio-enhanced "https://article3.com" --save
```

### Voice Variety:
```bash
# Enable voice shuffle for variety across synced files
python3 article2audio-enhanced --setup-shuffle
```

---

## ✅ Success Indicators

When cloud sync is working properly:

**Laptop:**
- ☁️ "Syncing to iCloud Drive..." message appears
- ✅ "Synced to iCloud Drive" confirmation
- 📱 "Available on iPhone via iCloud Drive" message

**iPhone:**
- Files app shows ArticleAudio folder in iCloud Drive
- Audio files appear with proper names and dates
- Tap-to-play works immediately
- Files can be downloaded for offline access

**Ready to start syncing your articles for iPhone listening?** 🎧📱

Run `python3 article2audio-enhanced --setup-cloud` to begin!