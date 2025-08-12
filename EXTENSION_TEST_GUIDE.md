# Browser Extension Testing Guide

## Quick Installation Steps

1. **Open Chrome** and go to: `chrome://extensions/`
2. **Toggle "Developer mode"** (top-right corner)
3. **Click "Load unpacked"**
4. **Navigate to and select**: `/Users/aettefagh/model-finetuning-project/tools/browser-extensions/article-to-audio/`
5. **Extension should appear** with 🎧 headphones icon

## Test Checklist

### ✅ Basic Installation Test
- [ ] Extension appears in Chrome extensions page
- [ ] Extension icon visible in toolbar
- [ ] No error messages in extensions page

### ✅ Popup Interface Test
1. **Click the extension icon** 🎧
2. **Verify popup opens** with:
   - [ ] Current page URL displayed
   - [ ] Voice dropdown (Christopher selected by default)
   - [ ] Speed dropdown (Fast selected by default)
   - [ ] Save to library checkbox
   - [ ] Convert button and Test button
3. **Test voice selection**:
   - [ ] Christopher (Deep, Authoritative) ⭐
   - [ ] Guy (Rich, Passionate)
   - [ ] Eric (Rational, Mature)
   - [ ] Andrew (Warm, Confident)
   - [ ] Aria (Clear, Positive)
   - [ ] Ava (Expressive, Caring)
4. **Test speed selection**:
   - [ ] Slow (Relaxed)
   - [ ] Normal (Standard) 
   - [ ] Fast (Efficient) ⭐
   - [ ] Very Fast (Rapid)

### ✅ Right-Click Menu Test
1. **Go to any article page** (try BBC, NPR, etc.)
2. **Right-click anywhere** on the page
3. **Look for "🎧 Convert to Audio"** in context menu
4. **Click it** and verify submenu appears with:
   - [ ] Convert This Page
   - [ ] Convert Selected Text (if text selected)
   - [ ] Quick voice options

### ✅ Article Detection Test
1. **Go to a news article** (e.g., https://www.bbc.com/news)
2. **Click extension icon** 
3. **Click "Test Current Page"**
4. **Verify status shows**:
   - [ ] Article detected message
   - [ ] Word count estimate
   - [ ] Audio duration estimate

### ✅ Conversion Simulation Test
1. **On an article page, click extension icon**
2. **Select your preferred voice** (Christopher recommended)
3. **Select speed** (Fast recommended)
4. **Click "Convert Article to Audio"**
5. **Watch for**:
   - [ ] Button changes to "Converting..."
   - [ ] Progress bar appears
   - [ ] Status updates show progress
   - [ ] Success message appears (simulated)

## Test URLs

### ✅ Known Working Sites
- https://www.bbc.com/news/articles/c5yll33v9gwo
- https://www.npr.org (any article)
- https://arstechnica.com (any article)
- https://dev.to (any post)

### ⚠️ Rate Limited Sites
- https://archive.ph/CiweT (use carefully, may be rate limited)

## Expected Behavior

### ✅ Success Cases
- **Article pages**: Should detect content and estimate duration
- **News sites**: Should show "Ready to convert" status
- **Blog posts**: Should work well with most formats

### ⚠️ Warning Cases
- **Homepage/Category pages**: Should warn "may not be an article"
- **Search pages**: Should suggest finding an actual article
- **About/Contact pages**: Should indicate not suitable for conversion

### ❌ Error Cases
- **Rate limited sites**: Should show appropriate error message
- **Paywall sites**: Should detect and report paywall issues
- **Invalid URLs**: Should handle gracefully

## Troubleshooting

### Extension Won't Load
```bash
# Check file permissions
ls -la ~/model-finetuning-project/tools/browser-extensions/article-to-audio/
```
All files should be readable.

### Missing Icons
The extension uses SVG icons converted to PNG. If icons don't show:
1. Check `icons/` folder has all 4 PNG files
2. Reload the extension in chrome://extensions/

### Popup Not Opening
1. Check for JavaScript errors in Chrome DevTools
2. Right-click extension icon → "Inspect popup"
3. Look for console errors

## What the Extension Does (Current State)

### ✅ Working Features
- **UI Interface**: Complete popup with all controls
- **Settings Storage**: Remembers your voice/speed preferences  
- **Article Detection**: Analyzes page content
- **Right-click Menus**: Context menu integration
- **Progress Simulation**: Shows realistic conversion progress

### 🔄 Simulated Features (Not Yet Integrated)
- **Actual CLI Integration**: Currently simulated
- **Real Audio Generation**: Shows success but doesn't call CLI yet
- **File Storage**: Simulated file creation

## Next Steps After Testing

Once you've tested the extension interface:

1. **Report what works/doesn't work**
2. **Note any UI improvements needed**
3. **Test with different article types**
4. **We'll then integrate with the actual CLI**

The extension is fully functional as a UI - it just needs the backend integration to actually call the `article2audio-enhanced` CLI tool.