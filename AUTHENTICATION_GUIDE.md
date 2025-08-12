# 🔑 Authentication Setup Guide

Your article-to-audio system now supports **authenticated article conversion** for subscription sites like NYT, Medium, WSJ, etc.

## 🚀 Quick Setup

### 1. Update Browser Extension
1. **Go to Chrome Extensions**: `chrome://extensions/`
2. **Find "Article to Audio" extension**
3. **Click the refresh icon** 🔄 (to pick up new cookie permissions)
4. **Verify permissions**: The extension should now have "Read and change data on all websites" 

### 2. Restart Enhanced Server
```bash
cd "/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension"
python3 enhanced-server.py
```

## ✅ Supported Subscription Sites

The extension **automatically detects and handles cookies** for these sites:

### News & Media
- **New York Times** (nytimes.com)
- **Wall Street Journal** (wsj.com) 
- **Washington Post** (washingtonpost.com)
- **Financial Times** (ft.com)
- **The Economist** (economist.com)
- **Bloomberg** (bloomberg.com)
- **Reuters** (reuters.com)
- **The New Yorker** (newyorker.com)
- **The Atlantic** (theatlantic.com)
- **Wired** (wired.com)

### Platforms
- **Medium** (medium.com)
- **Substack** (substack.com)

## 🎯 How It Works

### Browser Extension (Recommended)
1. **Log into your subscription sites** (NYT, Medium, etc.) in Chrome
2. **Use the browser extension** on any article from those sites
3. **Extension automatically uses your login cookies** 🔑
4. **Article converts successfully** despite paywall!

### Web UI (Limited)
- Web UI can't access cookies directly due to browser security
- Use the browser extension for authenticated articles
- Web UI works great for free articles

## 🧪 Testing Authentication

### Test with NYT Article
1. **Log into nytimes.com** in Chrome
2. **Find any article** (even premium ones)
3. **Click the browser extension icon** 🎧
4. **Click "Convert Article to Audio"**
5. **Should work despite paywall!** ✅

### Expected Behavior
- ✅ **Free articles**: Work in both extension and web UI
- ✅ **Subscription articles**: Work in browser extension with your login
- ❌ **Subscription articles**: Fail in web UI (no cookie access)

## 📋 Server Logs

When using authenticated requests, you'll see:
```
🔑 Using authentication cookies for https://www.nytimes.com/...
🔑 Added 15 authentication cookies
🎤 Running command: python3 .../article2audio-enhanced ...
```

## 🔧 Troubleshooting

### Extension Permission Issues
- **Reload extension** in `chrome://extensions/`
- **Check permissions**: Should include "Read and change data"
- **Try logging out and back into the subscription site**

### Authentication Not Working
- **Clear cookies**: Log out and back into the subscription site
- **Check server logs**: Should show "🔑 Using authentication cookies"
- **Test with free article first**: Ensure basic functionality works

### Cookie Errors
- **Restart Chrome** if cookie access seems broken
- **Check subscription status**: Ensure your account is active
- **Try incognito mode**: Test if regular browsing works

## 🎵 Success Indicators

### When Authentication Works:
- ✅ Server logs show: "🔑 Added X authentication cookies"
- ✅ Article extracts successfully despite paywall
- ✅ Audio generates normally
- ✅ No "paywall" error messages

### When It Doesn't:
- ❌ Server shows: "❌ Error: Article is behind a paywall"
- ❌ Extension shows archive site suggestions
- ❌ No cookie logs in server output

## 🔒 Privacy & Security

### What Cookies Are Used:
- **Only authentication cookies** from subscription sites
- **Passed securely** to local server only
- **Never stored** or logged permanently
- **Only used** for article extraction

### Data Safety:
- 🔒 **Cookies never leave your machine** (only sent to localhost)
- 🔒 **No cloud services** involved
- 🔒 **No tracking** or data collection
- 🔒 **Your subscription credentials** stay private

## 🚀 Next Steps

Once authentication is working:
1. **Test with your subscriptions** (NYT, Medium, etc.)
2. **Convert premium articles** to audio
3. **Build your audio library** with authenticated content
4. **Enjoy your premium articles** as audio! 🎧

---

**Ready to test?** Try a premium NYT article with the browser extension! 📰🎵