# Article-to-Audio Project Backlog

## 🚀 High Priority (Current Focus)

### Speed Controls & Mobile Experience
- [ ] **Implement speed controls during playback/listening**
  - Add playback speed options (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x)
  - Mobile-friendly speed toggle during audio playback
  - Remember speed preference per user
  - Quick speed adjustment without restarting audio

- [ ] **Fix audio sequence ordering issues on iPhone**
  - Debug transcript analysis to identify ordering problems
  - Test iCloud sync file ordering
  - Ensure proper chronological playback sequence

- [ ] **Create better mobile UI for iPhone listening experience**
  - Mobile-optimized web interface for audio library
  - Better touch controls for iPhone
  - Improved file organization in iPhone Files app
  - Native iOS shortcuts integration

## 🔧 Medium Priority (Core Improvements)

### Voice & Audio Enhancement
- [ ] **Add more voice options beyond current 6 voices**
  - Expand from 6 to 15+ available edge-tts voices
  - Add voice preview/sample functionality
  - Categorize voices by style (news, conversational, etc.)
  - Voice randomization improvements

- [ ] **Voice preference management in UI**
  - Save favorite voices per user
  - Voice categorization (news vs conversational)
  - Per-article voice selection memory
  - Voice shuffle configuration interface

- [ ] **Test Ollama TTS capabilities**
  - Alternative to edge-tts with potentially better voices
  - Local AI voice generation
  - Compare quality vs edge-tts
  - Performance benchmarking

### Content Processing
- [ ] **Refine deduplication algorithm to prevent text truncation**
  - Fix sentence boundary detection
  - Improve 80% overlap threshold logic
  - Prevent legitimate content from being removed
  - Better handling of quotes and dialogue

- [ ] **Address content duplication in extracted articles**
  - Enhanced paragraph-level deduplication
  - Preserve article structure while removing duplicates
  - Handle edge cases in news article formatting

- [ ] **Washington Post, WSJ specific extractors**
  - Expand beyond NYT paywall bypass
  - Site-specific content selectors
  - Custom authentication handling per site
  - Optimized extraction patterns

### Technical Infrastructure
- [ ] **Improve timeout handling for slower websites**
  - Configurable timeout settings
  - Better retry logic for failed requests
  - Progressive timeout increases
  - Better error messages for timeout failures

## 🎯 Future Features (Roadmap)

### Authentication & Access
- [ ] **Design future credential storage system for subscription sites**
  - Encrypted credential storage in browser extension
  - Auto-login flow before article extraction
  - Support for NYT, WSJ, Medium, WashPost, etc.
  - Master password protection for security
  - Per-site authentication management

### Batch Processing & Automation
- [ ] **Implement batch URL processing**
  - Queue management for multiple articles
  - Progress tracking and status updates
  - Error handling per article in batch
  - Browser extension UI for batch operations

- [ ] **Add batch URL conversion to web UI**
  - Process multiple articles at once from web interface
  - Queue management system
  - Progress indicators during batch conversion
  - Resume failed conversions

- [ ] **Reading list integration**
  - Pocket API integration
  - Instapaper API support
  - Browser bookmark sync
  - Auto-convert saved articles

### Audio Content Discovery & Integration
- [ ] **AudioScrape MCP integration**
  - Integrate with MCP.AudioScrape.com server (1M+ hours audio search)
  - Search podcasts/interviews by topic, speaker, keyword
  - Semantic search across spoken content with timestamps
  - OAuth 2.1 authentication setup
  - Complement article-to-audio with existing audio discovery

- [ ] **Related content discovery features**
  - After article conversion, suggest related podcasts/interviews
  - Cross-reference article topics with expert discussions
  - Topic-based audio recommendations
  - Speaker-based content filtering
  - Integration with article topic extraction

- [ ] **Content validation and enhancement**
  - Search for expert commentary on article topics
  - Find follow-up discussions or rebuttals
  - Discover source interviews for article quotes
  - Validate article claims against spoken content
  - Create curated playlists combining articles + related audio

### Advanced Features
- [ ] **Podcast-style features**
  - Auto-generate episode metadata
  - RSS feed for converted articles
  - Playlist creation and management
  - Skip intro/outro functionality

- [ ] **AI-powered enhancements**
  - Article summarization options
  - Key points extraction
  - Topic-based organization
  - Smart playlist recommendations

### Mobile & Cross-Platform
- [ ] **Native mobile app consideration**
  - iOS/Android app for better mobile experience
  - Offline playback capabilities
  - Background audio playback
  - Car integration (CarPlay/Android Auto)

- [ ] **Desktop app integration**
  - System tray notifications
  - Keyboard shortcuts for quick conversion
  - Desktop widget for article queue
  - Better local file organization

- [ ] **Cross-device sync configuration UI**
  - Settings for iCloud vs other cloud providers
  - Sync preferences management
  - Device-specific settings
  - Sync status monitoring

## 🔍 Quality & Performance

### Testing & Reliability
- [ ] **Comprehensive site testing**
  - Test paywall bypass across 20+ news sites
  - Document success rates per site
  - Maintain compatibility matrix
  - Regular regression testing

- [ ] **Performance optimization**
  - Faster content extraction
  - Reduced memory usage
  - Cached bypass service responses
  - Parallel processing where possible

### User Experience
- [ ] **Better error handling & feedback**
  - User-friendly error messages
  - Retry suggestions for failed conversions
  - Progress indicators for long conversions
  - Success/failure notifications

- [ ] **Progress indicators during conversion**
  - Real-time feedback in browser extension
  - Better UX for long conversions
  - Estimated time remaining
  - Stage-by-stage progress updates

- [ ] **Better error messages in extension**
  - User-friendly error handling
  - Clearer feedback on failures
  - Actionable error resolution steps
  - Context-aware help suggestions

- [ ] **Accessibility improvements**
  - Screen reader compatibility
  - Keyboard navigation support
  - High contrast mode support
  - Font size adjustments

## 🛠️ Technical Debt & Maintenance

### Code Quality
- [ ] **Test suite development**
  - Unit tests for core extraction logic
  - Integration tests for paywall bypass
  - End-to-end testing automation
  - Performance benchmarking

- [ ] **Code refactoring**
  - Modularize extraction logic
  - Improve error handling patterns
  - Better configuration management
  - Documentation improvements

### Security & Privacy
- [ ] **Security audit**
  - Credential storage security review
  - API key management improvements
  - Input sanitization audit
  - HTTPS enforcement everywhere

- [ ] **Privacy enhancements**
  - Local-first processing options
  - Optional cloud sync
  - Data retention policies
  - User data export functionality

## 🌟 Innovation & Experiments

### Experimental Features
- [ ] **AI voice cloning integration**
  - Custom voice creation from samples
  - Celebrity voice options (with licensing)
  - Personalized reading voices
  - Emotional tone adjustment

- [ ] **Smart content curation**
  - ML-based article recommendations
  - Topic clustering and organization
  - Reading time optimization
  - Content quality scoring

- [ ] **Social features**
  - Shared playlists
  - Article recommendations from friends
  - Community-contributed voice packs
  - Usage statistics and insights

## 📋 Completed Items ✅

- ✅ **Test current system with real NYT articles**
- ✅ **Fix NYT content extraction** (791→1440 words, 82% improvement)  
- ✅ **Implement speed controls during playback/listening**
- ✅ **Create better mobile UI for iPhone listening experience**
- ✅ **Set up GitHub repository for project version control**
- ✅ **Analyze transcript to verify NYT paywall detection**

### **Legacy Project Completions:**
- ✅ **Research and evaluate free TTS options** (edge-tts, pyttsx3, Ollama voice models)
- ✅ **Design MVP architecture** using local-first approach
- ✅ **Create simple CLI prototype** with edge-tts
- ✅ **Install and test mcp-tts-say MCP server**
- ✅ **Build production CLI** with real URL testing
- ✅ **Create browser extension** manifest and basic structure
- ✅ **Build browser extension popup interface**
- ✅ **Create local HTTP server** to bridge extension and CLI
- ✅ **Design and build web UI** for article-to-audio conversion
- ✅ **Add audio library management** to web UI
- ✅ **Implement enhanced rate limiting** for archive sites
- ✅ **Add authentication support** for subscription sites
- ✅ **Implement cookie/session management**
- ✅ **Design cross-device sync architecture**
- ✅ **Implement voice shuffle feature**
- ✅ **Set up cloud storage sync** (iCloud)
- ✅ **Fix content extraction order/scrambling issues**
- ✅ **Implement automatic paywall bypass**
- ✅ **Fix browser extension default save settings**
- ✅ **Add transcript generation and logging** for debugging
- ✅ **Create mobile-friendly web interface** for iPhone playback

- ✅ **Core functionality implementation**
  - Article extraction with BeautifulSoup
  - Text-to-Speech with edge-tts
  - Browser extension integration
  - iCloud sync for cross-device access
  - Paywall bypass for multiple services

## 🔄 Integration Opportunities

### Task Management
- [ ] **TaskMaster integration**
  - Import backlog items into TaskMaster
  - Track progress with TaskMaster commands
  - Generate PRDs for major features
  - Sprint planning and milestone tracking

### Database & Backend
- [ ] **Supabase integration** (Explicitly backlogged by user)
  - User account management
  - Cloud-based audio library storage
  - Cross-device article sync
  - Usage analytics and metrics

### Development Tools
- [ ] **CI/CD pipeline setup**
  - Automated testing on commits
  - Browser extension packaging
  - Release automation
  - Deployment to GitHub releases

## 📝 **Complete Legacy Objectives Summary**

### **From PROJECT_STATUS.md - Still Pending:**
- [ ] **Pocket/Instapaper API integration** - Reading list service integration
- [ ] **Test Ollama TTS capabilities** - Alternative voice generation
- [ ] **Voice preference management in UI** - Save favorite voices per user
- [ ] **Batch URL conversion to web UI** - Process multiple articles at once
- [ ] **Cross-device sync configuration UI** - Settings for cloud providers
- [ ] **Washington Post, WSJ specific extractors** - Expand paywall bypass
- [ ] **Progress indicators during conversion** - Real-time feedback
- [ ] **Better error messages in extension** - User-friendly error handling

### **Current Session Priorities:**
1. **Audio sequence ordering issues on iPhone** (affects daily usage)
2. **Voice expansion** (simple config change for immediate benefit)
3. **Content deduplication refinement** (quality improvement)

---

**Last Updated**: August 12, 2025
**Project Status**: Core functionality working, mobile UI complete, focusing on remaining UX issues
**GitHub Repository**: https://github.com/reggienitro/article-to-audio-extension