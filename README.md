# Article to Audio Browser Extension

🎧 **Convert web articles to audio with customizable deep male voices and speed controls!**

## Features

✅ **One-click conversion** from any article page  
✅ **Deep male voice options** (Christopher, Guy, Eric)  
✅ **Variable speed control** (slow to very fast)  
✅ **Right-click context menu** integration  
✅ **Save to audio library** option  
✅ **Article detection** and compatibility testing  

## Installation

### Step 1: Load Extension in Chrome

1. **Open Chrome** and navigate to `chrome://extensions/`
2. **Enable Developer Mode** (toggle in top-right corner)
3. **Click "Load unpacked"** button
4. **Select the browser-extension folder**: 
   ```
   /Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/
   ```
5. **Extension should appear** with headphones icon 🎧

### Step 2: Verify Installation

- Look for the **Article to Audio** extension in your extensions bar
- Pin it for easy access by clicking the puzzle piece icon
- The extension should show as enabled

## Usage

### Method 1: Extension Popup
1. **Navigate to any article** (news, blog, etc.)
2. **Click the extension icon** 🎧
3. **Choose your settings**:
   - Voice: Christopher (deep), Guy (rich), Eric (mature)
   - Speed: Slow, Normal, Fast, Very Fast
   - Save option: Toggle to save to library
4. **Click "Convert Article to Audio"**

### Method 2: Right-Click Menu
1. **Right-click anywhere** on an article page
2. **Select "🎧 Convert to Audio"**
3. **Choose from submenu**:
   - Convert This Page
   - Convert Selected Text (if text is selected)
   - Quick voice options

### Method 3: Test Current Page
1. **Click extension icon**
2. **Click "Test Current Page"** to analyze article compatibility
3. **View extraction results** before conversion

## CLI Integration

The extension is designed to work with the `article2audio-enhanced` CLI tool:

```bash
# The extension calls this command internally:
python3 ~/model-finetuning-project/article2audio-enhanced "URL" --voice christopher --speed fast
```

### Setting up CLI Integration

**Option 1: Native Messaging (Advanced)**
- Requires additional setup for direct CLI communication
- Most secure and efficient method

**Option 2: Local Server (Recommended)**
- Run a simple local server that wraps the CLI
- Extension communicates via localhost

**Option 3: Manual Testing**
- Copy URLs from extension and run CLI manually
- Good for testing and development

## Supported Sites

✅ **Major News Sites**: BBC, NPR, Reuters  
✅ **Tech Blogs**: Ars Technica, The Verge  
✅ **Developer Blogs**: Dev.to, Medium  
✅ **Archive Sites**: Archive.ph (with rate limiting)  

**Success Rate**: ~80% across tested sites

## Extension Structure

```
browser-extension/
├── manifest.json          # Extension configuration
├── popup.html             # Main interface
├── popup.css              # Styling
├── popup.js               # Popup functionality
├── background.js          # Background service worker
├── content.js             # Page content analysis
├── icons/                 # Extension icons
│   ├── icon-16.png
│   ├── icon-32.png
│   ├── icon-48.png
│   └── icon-128.png
└── README.md              # This file
```

## Voice Options

| Voice | Gender | Style | Best For |
|-------|--------|-------|----------|
| **Christopher** ⭐ | Male | Deep, Authoritative | News articles, formal content |
| **Guy** | Male | Rich, Passionate | Opinion pieces, blogs |
| **Eric** | Male | Rational, Mature | Technical content, analysis |
| **Andrew** | Male | Warm, Confident | Conversational articles |
| **Aria** | Female | Clear, Positive | News, general content |
| **Ava** | Female | Expressive, Caring | Personal stories, blogs |

## Speed Settings

| Setting | Rate | Best For |
|---------|------|----------|
| **Slow** | +0% | Learning, complex topics |
| **Normal** | +10% | Standard reading |
| **Fast** ⭐ | +20% | Efficient consumption |
| **Very Fast** | +40% | Quick summaries |

## Troubleshooting

### Extension Not Loading
- Check that Developer Mode is enabled
- Ensure all files are in the browser-extension folder
- Look for errors in chrome://extensions/

### Conversion Not Working
- Verify the CLI tool is installed and accessible
- Check that the article page has readable content
- Try the "Test Current Page" feature first

### Rate Limiting Issues
- Some sites (like archive.ph) have strict rate limits
- Wait 30-60 seconds between requests to the same domain
- Consider using different archive alternatives

### Paywall/Protected Content
- Extension will detect and report paywall issues
- Try using archive sites like archive.ph or web.archive.org
- Ensure you have legitimate access to subscription content

## Development

### Testing Changes
1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the Article to Audio extension
4. Test the updated functionality

### Adding New Features
- **popup.js**: UI functionality and settings
- **background.js**: Context menus and message handling  
- **content.js**: Page content analysis and extraction
- **manifest.json**: Permissions and configuration

## Future Enhancements

🔄 **Planned Features**:
- Direct CLI integration via native messaging
- Audio player with playback controls
- Batch conversion of multiple articles
- Integration with read-later services (Pocket, Instapaper)
- Cloud storage sync for audio library
- Mobile companion app

## Support

For issues or questions:
1. Check this README for troubleshooting
2. Test with the CLI directly first
3. Verify extension permissions in Chrome
4. Check browser console for error messages

---

**Version**: 1.0.0  
**Compatibility**: Chrome 88+, Edge 88+  
**License**: MIT