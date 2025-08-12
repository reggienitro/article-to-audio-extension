# Cloud Sync Design for Article-to-Audio

## Objective
Enable users to convert articles on their laptop/PC and listen to them on their iPhone through cloud storage synchronization.

## User Workflow
1. **Convert** article on laptop using browser extension
2. **Upload** audio file to cloud storage automatically  
3. **Access** files from iPhone via cloud storage app or mobile web interface
4. **Stream/Download** audio files for offline listening

## Cloud Storage Options Analysis

### Option 1: iCloud Drive (Recommended for iPhone users)
**Pros:**
- Native iOS integration
- Automatic sync with Files app
- No additional authentication needed if user logged into iCloud
- Good storage quotas (5GB free, upgradeable)

**Cons:**
- Apple-only ecosystem
- No official third-party API (would need workarounds)
- Limited to macOS/iOS devices

**Implementation:** Use macOS iCloud Drive folder monitoring and direct file system access

### Option 2: Google Drive (Recommended for cross-platform)
**Pros:**
- Excellent API with Python SDK
- 15GB free storage
- Works on all platforms
- Rich mobile app with streaming capabilities

**Cons:**
- Requires OAuth authentication setup
- More complex initial setup

**Implementation:** Google Drive API v3 with service account or OAuth 2.0

### Option 3: Dropbox
**Pros:**
- Simple, reliable API
- Good mobile app
- Cross-platform
- 2GB free (limited but sufficient for audio files)

**Cons:**
- Smaller free storage limit
- OAuth required

**Implementation:** Dropbox API v2 with app authentication

## Recommended Architecture

### Phase 1: Local-First with Cloud Backup (iCloud Drive)
```
[Laptop] → [Local Audio Dir] → [Sync to iCloud Drive] → [iPhone Files App]
```

**Benefits:**
- Minimal setup required
- Leverages existing iCloud sync
- No API authentication needed
- Instant access on iPhone

**Implementation:**
1. Configure audio output directory to be inside `~/Library/Mobile Documents/com~apple~CloudDocs/ArticleAudio/`
2. Files automatically sync via iCloud
3. Access via iPhone Files app → iCloud Drive → ArticleAudio

### Phase 2: Cross-Platform with Google Drive API
```
[Browser Extension] → [Local Server] → [Google Drive API] → [Mobile Web Interface]
```

**Benefits:**
- Works on any platform
- Rich mobile experience
- Streaming playback
- Better organization and metadata

## Implementation Plan

### Phase 1: iCloud Drive Integration (Simplest)

1. **Configure Audio Directory**
   ```python
   AUDIO_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "ArticleAudio"
   ```

2. **Add Sync Status UI**
   - Show iCloud sync status in web interface
   - Display file sync progress
   - Mobile access instructions

3. **Mobile Access Guide**
   - iPhone: Files App → Browse → iCloud Drive → ArticleAudio
   - Tap audio files to play with built-in player
   - Download for offline listening

### Phase 2: Google Drive Integration (Advanced)

1. **Google Drive Setup**
   ```bash
   pip install google-api-python-client google-auth google-auth-oauthlib
   ```

2. **Authentication Flow**
   - One-time OAuth setup
   - Store refresh tokens securely
   - Service account for background uploads

3. **Upload Integration**
   ```python
   def upload_to_gdrive(audio_file, metadata):
       # Upload audio file with metadata
       # Create shareable link
       # Store Drive file ID for management
   ```

4. **Mobile Web Interface**
   - List uploaded audio files
   - Stream audio directly from Drive
   - Download for offline access
   - Search and filter by date/title

## Configuration Options

### User Settings
```json
{
  "cloud_sync": {
    "enabled": true,
    "provider": "icloud|gdrive|dropbox",
    "auto_upload": true,
    "mobile_access": true,
    "sync_metadata": true
  }
}
```

### Metadata Storage
```json
{
  "filename": "20250810_article_christopher.mp3",
  "title": "Article Title",
  "url": "https://...",
  "voice": "christopher",
  "speed": "fast",
  "created": "2025-08-10T12:00:00Z",
  "cloud_url": "https://drive.google.com/...",
  "mobile_accessible": true
}
```

## Security & Privacy

### iCloud Drive
- Files stored in user's personal iCloud account
- End-to-end encryption via iCloud
- No third-party access to content

### Google Drive
- Files stored in user's Google account
- Encryption in transit and at rest
- Granular sharing controls
- Can be made private (not searchable/indexed)

## Next Steps

1. **Implement iCloud Drive integration** (Phase 1)
2. **Test cross-device access** with iPhone
3. **Create mobile access documentation**
4. **Add Google Drive support** (Phase 2) if needed
5. **Build mobile-optimized web player**

## Expected User Experience

**Laptop:**
1. Convert article with browser extension ✅
2. See "☁️ Syncing to iCloud..." notification
3. File appears in web library with cloud icon

**iPhone:**
1. Open Files app → iCloud Drive → ArticleAudio  
2. See converted audio files with descriptive names
3. Tap to play with native iOS audio player
4. Download for offline listening during commute

This provides seamless cross-device access with minimal setup complexity.