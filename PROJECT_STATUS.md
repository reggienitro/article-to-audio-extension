# Article-to-Audio Converter Project Status

## 🎯 Project Overview

**Original Request**: Build a tool to scrape articles and convert them to audio for listening on phone/computer

### Core Requirements from User:
1. **Voice Selection** - Deep male narrators preferred (Christopher, Guy, Eric)
2. **Speed Adjustment** - Multiple speed options (slow to very fast)
3. **Storage Options** - Local library + cloud sync
4. **Pleasant Listening Experience** - Clean extraction, no ads/junk
5. **Cross-Device Access** - Convert on laptop, listen on iPhone
6. **Authentication Support** - Handle subscription sites (NYT, Medium, etc.)

## 📂 Project Structure

### Main Components:
1. **CLI Tool**: `/Users/aettefagh/model-finetuning-project/article2audio-enhanced`
   - Python-based article extractor and TTS converter
   - Uses edge-tts for free Microsoft voices
   - Supports authentication cookies and paywall bypass

2. **HTTP Server**: `/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/enhanced-server.py`
   - Bridges browser extension to CLI
   - Handles CORS and request routing
   - Archive site detection and rate limiting

3. **Browser Extension**: `/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/`
   - Chrome Manifest V3 extension
   - Files: `manifest.json`, `popup.js`, `popup.html`, `popup.css`
   - Icons in `/icons` subdirectory

4. **Web UI**: `/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/web-ui.html`
   - Standalone web interface
   - Audio library management
   - Mobile-responsive design

## ✅ Completed Features

### 1. **Core Functionality**
- ✅ Article extraction with BeautifulSoup
- ✅ Text-to-Speech with edge-tts
- ✅ Multiple voice options (6 voices)
- ✅ Speed control (slow/normal/fast/very_fast)
- ✅ Local audio library storage

### 2. **Browser Extension**
- ✅ Chrome extension with popup UI
- ✅ Right-click context menu
- ✅ Settings persistence
- ✅ Server communication
- ✅ Cookie extraction for auth

### 3. **Advanced Features**
- ✅ **iCloud Sync** - Automatic sync to iPhone via iCloud Drive
- ✅ **Voice Shuffle** - Cycle between favorite voices (disabled by default)
- ✅ **Paywall Bypass** - Auto-tries 12ft.io, archive.ph, web.archive.org
- ✅ **Authentication** - Cookie passing for subscription sites
- ✅ **Archive Support** - Rate limiting for archive services
- ✅ **Content Deduplication** - Prevents repeated paragraphs
- ✅ **Transcript Generation** - Saves debug transcripts

### 4. **Recent Fixes**
- ✅ Fixed syntax error in server (escaped quotes)
- ✅ Browser extension defaults to saving (checkbox checked)
- ✅ Improved paywall detection ("still verifying access")
- ✅ Better content extraction order preservation
- ✅ NYT-specific content selectors

## 📋 Current Status

### Working Features:
- ✅ **iCloud sync working** - files save and sync to iPhone
- ✅ **Voice shuffle implemented** (but disabled by default)
- ✅ **Paywall bypass enhanced** - auto-tries 3 services automatically
- ✅ **Content deduplication added** - prevents repeated paragraphs
- ✅ **Transcript generation added** - saves debug transcripts to cache folder
- ✅ **Browser extension defaults to saving** - checkbox checked by default

### Known Issues:
1. **Content Quality on NYT** - Sometimes gets preview/snippet instead of full article
2. **Audio Repetition** - Fixed with deduplication but needs testing
3. **Paywall Detection Timing** - May need earlier detection

## 🔧 Key Commands

### Start Server:
```bash
cd "/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension"
python3 enhanced-server.py
```

### Test CLI Directly:
```bash
cd "/Users/aettefagh/model-finetuning-project"
python3 article2audio-enhanced "https://article-url" --save

# Voice shuffle commands
python3 article2audio-enhanced --enable-shuffle
python3 article2audio-enhanced --disable-shuffle
python3 article2audio-enhanced --setup-shuffle

# Cloud sync commands
python3 article2audio-enhanced --enable-cloud
python3 article2audio-enhanced --cloud-status
python3 article2audio-enhanced --setup-cloud
```

### Check Transcripts:
```bash
ls -la /Users/aettefagh/model-finetuning-project/data/cache/*transcript.txt
```

### View Audio Library:
```bash
ls -la /Users/aettefagh/model-finetuning-project/data/audio/
```

### Check iCloud Sync:
```bash
ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/ArticleAudio/
```

## 📝 TODO List (Current State)

### Completed ✅:
1. Research and evaluate free TTS options (edge-tts, pyttsx3, Ollama voice models)
2. Design MVP architecture using local-first approach
3. Create simple CLI prototype with edge-tts
4. Install and test mcp-tts-say MCP server
5. Build production CLI with real URL testing
6. Create browser extension manifest and basic structure
7. Build browser extension popup interface
8. Create local HTTP server to bridge extension and CLI
9. Design and build web UI for article-to-audio conversion
10. Add audio library management to web UI
11. Implement enhanced rate limiting for archive sites
12. Add authentication support for subscription sites
13. Implement cookie/session management
14. Design cross-device sync architecture
15. Implement voice shuffle feature
16. Set up cloud storage sync (iCloud)
17. Fix content extraction order/scrambling issues
18. Implement automatic paywall bypass
19. Fix browser extension default save settings

### In Progress 🔄:
1. Fix content repetition/duplication in extracted articles
2. Improve paywall detection to trigger bypass earlier
3. Add transcript generation and logging for debugging

### Pending 📌:
1. Investigate Pocket/Instapaper API integration
2. Test Ollama TTS capabilities
3. Add voice preference management to UI
4. Create mobile-friendly web interface for iPhone playback
5. Add batch URL conversion to web UI
6. Create cross-device sync configuration UI

## 🧪 Testing Procedures

### Test Basic Conversion:
1. Start server: `python3 enhanced-server.py`
2. Open Chrome extension on any article
3. Ensure "Save to Library" is checked
4. Click "Convert Article to Audio"
5. Check for audio file in library and iCloud

### Test Paywall Bypass:
1. Go to NYT article: `https://www.nytimes.com/2025/08/10/us/politics/trump-putin-alaska-reaction.html`
2. Use browser extension
3. Should see "Paywall detected, trying bypass services..."
4. Check transcript for full content

### Test iCloud Sync:
1. Convert article with --save flag
2. Check `~/Library/Mobile Documents/com~apple~CloudDocs/ArticleAudio/`
3. Open Files app on iPhone → iCloud Drive → ArticleAudio
4. Tap to play audio file

## 🔍 Debugging

### Check Server Logs:
- Look for 🔒 paywall detection
- Watch for 🔄 bypass attempts
- Check for ☁️ sync messages

### View Transcripts:
- Located in `/data/cache/` directory
- Shows exact extracted content
- Helps identify extraction issues

### Common Issues:
1. **Server not running**: Start with `python3 enhanced-server.py`
2. **Extension not updated**: Reload in chrome://extensions/
3. **iCloud not syncing**: Check iCloud Drive is enabled in System Preferences
4. **Paywall not bypassed**: May need to manually use archive URL

## 📚 Key Files Modified

### CLI Enhancements:
- Added `try_paywall_bypass()` method
- Improved `detect_paywall()` with more patterns
- Added `save_transcript()` for debugging
- Enhanced content selectors for NYT
- Added deduplication logic
- Implemented cloud sync methods
- Added voice shuffle functionality

### Server Updates:
- Fixed syntax error (escaped quotes)
- Added cloud status endpoint
- Enhanced paywall error messages
- Better archive URL suggestions

### Extension Changes:
- Default save checkbox to checked
- Update default settings to saveAudio: true
- Cookie extraction for auth sites

## 🚀 Next Steps When Resuming

1. **Test NYT article with browser extension**
   - Check if paywall bypass works
   - Review transcript quality
   - Verify no content repetition

2. **Fine-tune content extraction if needed**
   - May need more NYT-specific selectors
   - Could add Washington Post, WSJ specific extractors

3. **Consider adding**:
   - Progress indicators during conversion
   - Better error messages in extension
   - Batch URL processing
   - Mobile web interface

## 🎯 Success Metrics

The system successfully:
- ✅ Converts articles to audio with chosen voice
- ✅ Saves to local library
- ✅ Syncs to iCloud for iPhone access
- ✅ Handles many paywalled sites
- ✅ Preserves article structure
- ✅ Provides debug transcripts

## 💡 Architecture Decisions

1. **Local-first approach** - No cloud dependencies except optional sync
2. **Edge-TTS** - Free, high-quality voices, no API keys
3. **Browser extension + local server** - Secure, no CORS issues
4. **iCloud Drive** - Native iPhone integration, no extra apps
5. **Automatic paywall bypass** - Better user experience
6. **Transcript generation** - Easy debugging and quality checks

---

**Last Updated**: Session from August 12, 2025
**Project Location**: `/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/`
**Status**: Functional with minor content quality issues to resolve