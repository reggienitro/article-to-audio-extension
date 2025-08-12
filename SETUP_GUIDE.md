# Article to Audio Extension - Setup Guide

🎧 **Get your browser extension working with the article2audio CLI!**

## Quick Setup

### 1. Install the Extension

1. **Open Chrome** → `chrome://extensions/`
2. **Enable Developer Mode** (toggle in top-right)
3. **Click "Load unpacked"**
4. **Select this directory**: `~/AI projects/claude-tools/article-to-audio-extension/`

### 2. Start the Local Server

**Option 1: Use the start script**
```bash
cd "~/AI projects/claude-tools/article-to-audio-extension/"
./start-server.sh
```

**Option 2: Start manually**
```bash
cd "~/AI projects/claude-tools/article-to-audio-extension/"
python3 server.py
```

### 3. Test the Integration

1. **Go to any article** (e.g., https://www.bbc.com/news/articles/c5yll33v9gwo)
2. **Click the extension icon** 🎧  
3. **Click "Test Current Page"** first
4. **Click "Convert Article to Audio"**

## How It Works

```
Browser Extension → Local HTTP Server → article2audio CLI → Audio File
    (popup.js)         (server.py)       (Python script)     (.mp3)
```

### Extension Features
- ✅ **Voice Selection**: Christopher, Guy, Eric, Andrew, Aria, Ava
- ✅ **Speed Control**: Slow, Normal, Fast, Very Fast  
- ✅ **Save Option**: Toggle to save files permanently
- ✅ **Article Testing**: Check compatibility before conversion
- ✅ **Right-click Menu**: Convert from context menu

### Server Endpoints
- `GET /status` - Check if server is running
- `GET /test?url=...` - Test article extraction  
- `POST /convert` - Convert article to audio

## Troubleshooting

### Extension Won't Load
- Check Developer Mode is enabled
- Look for errors in `chrome://extensions/`
- Make sure all files are in the directory

### "Local server not running" Error
```bash
# Start the server first:
cd "~/AI projects/claude-tools/article-to-audio-extension/"
python3 server.py
```

### CLI Not Found Error
Make sure the CLI exists at:
```bash
ls -la /Users/aettefagh/model-finetuning-project/article2audio-enhanced
```

If missing, the CLI should be in your model-finetuning-project directory.

### CORS/Network Errors
- The extension needs localhost permissions (already configured)
- Make sure server is running on port 8888
- Check browser console for detailed errors

### Conversion Fails
1. **Test the CLI directly first**:
   ```bash
   python3 /Users/aettefagh/model-finetuning-project/article2audio-enhanced "https://www.bbc.com/news/articles/c5yll33v9gwo" --voice christopher --speed fast
   ```

2. **Check server logs** for detailed error messages

3. **Verify article URL** is accessible and contains readable content

## Development

### Making Changes

1. **Edit extension files** (popup.js, popup.html, etc.)
2. **Reload extension** in `chrome://extensions/`
3. **Test changes** on a real article

### Adding New Features

- **popup.js**: UI logic and server communication
- **server.py**: Server endpoints and CLI integration  
- **background.js**: Context menus and background tasks
- **manifest.json**: Extension permissions and config

## Testing Checklist

### ✅ Basic Functionality
- [ ] Extension loads without errors
- [ ] Server starts on port 8888
- [ ] Status endpoint responds
- [ ] Extension can connect to server

### ✅ Article Testing  
- [ ] Test Current Page works
- [ ] Shows article detection results
- [ ] Handles non-article pages gracefully

### ✅ Audio Conversion
- [ ] Convert button triggers CLI
- [ ] Progress updates during conversion  
- [ ] Success message shows filename
- [ ] Error handling for failed conversions

### ✅ Voice & Speed Settings
- [ ] Voice dropdown changes are saved
- [ ] Speed settings persist between sessions
- [ ] Save to storage option works

## Next Steps

Once basic functionality works:

1. **Add audio playback** controls in the extension
2. **Build audio library** management
3. **Batch conversion** for multiple articles
4. **Integration with read-later** services (Pocket, Instapaper)

---

**Need Help?** Check the main README.md for additional documentation and troubleshooting tips.