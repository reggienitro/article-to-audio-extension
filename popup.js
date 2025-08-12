// Article to Audio Extension Popup JavaScript

class ArticleToAudioPopup {
  constructor() {
    this.currentUrl = '';
    this.settings = {
      voice: 'christopher',
      speed: 'fast',
      saveAudio: true  // Default to saving for cloud sync
    };
    
    this.init();
  }
  
  async init() {
    await this.loadSettings();
    await this.getCurrentPageUrl();
    this.bindEvents();
    this.updateUI();
  }
  
  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get(['voice', 'speed', 'saveAudio']);
      this.settings = {
        voice: result.voice || 'christopher',
        speed: result.speed || 'fast',
        saveAudio: result.saveAudio !== undefined ? result.saveAudio : true
      };
    } catch (error) {
      console.log('Using default settings');
    }
  }
  
  async saveSettings() {
    try {
      await chrome.storage.sync.set(this.settings);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }
  
  async getCurrentPageUrl() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.url) {
        this.currentUrl = tab.url;
        document.getElementById('url-input').value = tab.url;
        
        // Check if URL is suitable for article extraction
        if (this.isArticleUrl(tab.url)) {
          this.updateStatus('Ready to convert article to audio', 'info');
        } else {
          this.updateStatus('This page may not be an article', 'warning');
        }
      }
    } catch (error) {
      this.updateStatus('Unable to access current page', 'error');
      console.error('Failed to get current page:', error);
    }
  }
  
  isArticleUrl(url) {
    // Check for common article URL patterns
    const articleIndicators = [
      '/article', '/news/', '/blog/', '/post/', '/story/', 
      '/articles/', '/posts/', '.html', '/read/'
    ];
    
    const nonArticleIndicators = [
      '/search', '/category', '/tag', '/archive', 
      '/about', '/contact', '/home', '/?', '/#'
    ];
    
    const urlLower = url.toLowerCase();
    
    // Check for non-article indicators first
    if (nonArticleIndicators.some(indicator => urlLower.includes(indicator))) {
      return false;
    }
    
    // Check for article indicators
    return articleIndicators.some(indicator => urlLower.includes(indicator)) || 
           urlLower.match(/\d{4}\/\d{2}\/\d{2}/) || // Date patterns
           urlLower.match(/\/[\w-]{20,}/); // Long URL segments (often article slugs)
  }
  
  bindEvents() {
    // Voice selection
    document.getElementById('voice-select').addEventListener('change', (e) => {
      this.settings.voice = e.target.value;
      this.saveSettings();
    });
    
    // Speed selection
    document.getElementById('speed-select').addEventListener('change', (e) => {
      this.settings.speed = e.target.value;
      this.saveSettings();
    });
    
    // Save audio checkbox
    document.getElementById('save-audio').addEventListener('change', (e) => {
      this.settings.saveAudio = e.target.checked;
      this.saveSettings();
    });
    
    // Refresh URL button
    document.getElementById('refresh-url').addEventListener('click', () => {
      this.getCurrentPageUrl();
    });
    
    // Convert button
    document.getElementById('convert-btn').addEventListener('click', () => {
      this.convertArticle();
    });
    
    // Test button
    document.getElementById('test-btn').addEventListener('click', () => {
      this.testCurrentPage();
    });
    
    // Footer buttons
    document.getElementById('settings-btn').addEventListener('click', () => {
      this.openSettings();
    });
    
    document.getElementById('library-btn').addEventListener('click', () => {
      this.openLibrary();
    });
    
    document.getElementById('help-btn').addEventListener('click', () => {
      this.openHelp();
    });
  }
  
  updateUI() {
    // Set current settings in UI
    document.getElementById('voice-select').value = this.settings.voice;
    document.getElementById('speed-select').value = this.settings.speed;
    document.getElementById('save-audio').checked = this.settings.saveAudio;
  }
  
  updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    const statusText = statusEl.querySelector('.status-text');
    const statusIcon = statusEl.querySelector('.status-icon');
    
    statusText.textContent = message;
    
    // Remove existing status classes
    statusEl.classList.remove('success', 'error', 'warning');
    
    // Add new status class and icon
    switch (type) {
      case 'success':
        statusEl.classList.add('success');
        statusIcon.textContent = '✅';
        break;
      case 'error':
        statusEl.classList.add('error');
        statusIcon.textContent = '❌';
        break;
      case 'warning':
        statusEl.classList.add('warning');
        statusIcon.textContent = '⚠️';
        break;
      default:
        statusIcon.textContent = 'ℹ️';
    }
  }
  
  showProgress(show = true, progress = 0, text = 'Processing...') {
    const progressEl = document.getElementById('progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (show) {
      progressEl.style.display = 'block';
      progressFill.style.width = `${progress}%`;
      progressText.textContent = text;
    } else {
      progressEl.style.display = 'none';
    }
  }
  
  async convertArticle() {
    if (!this.currentUrl) {
      this.updateStatus('No URL to convert', 'error');
      return;
    }
    
    const convertBtn = document.getElementById('convert-btn');
    
    try {
      // Disable button and show progress
      convertBtn.disabled = true;
      convertBtn.innerHTML = '<span class="btn-icon">⏳</span>Converting...';
      this.showProgress(true, 10, 'Sending to article2audio CLI...');
      this.updateStatus('Starting conversion...', 'info');
      
      // Simulate progress updates (in real implementation, these would come from the CLI)
      setTimeout(() => {
        this.showProgress(true, 30, 'Extracting article content...');
      }, 1000);
      
      setTimeout(() => {
        this.showProgress(true, 60, 'Generating audio with TTS...');
      }, 2000);
      
      setTimeout(() => {
        this.showProgress(true, 90, 'Finalizing audio file...');
      }, 3000);
      
      // Call the CLI (this would be implemented via native messaging or local server)
      const result = await this.callArticle2AudioCLI(this.currentUrl);
      
      if (result.success) {
        this.showProgress(true, 100, 'Complete!');
        this.updateStatus(`Audio generated successfully! (${result.duration})`, 'success');
        
        // Show audio file info
        if (this.settings.saveAudio) {
          this.updateStatus(`Saved to library: ${result.filename}`, 'success');
        } else {
          this.updateStatus(`Temporary file ready for playback`, 'success');
        }
      } else {
        throw new Error(result.error);
      }
      
    } catch (error) {
      this.updateStatus(`Conversion failed: ${error.message}`, 'error');
      console.error('Conversion error:', error);
    } finally {
      // Re-enable button and hide progress
      convertBtn.disabled = false;
      convertBtn.innerHTML = '<span class="btn-icon">🎤</span>Convert Article to Audio';
      setTimeout(() => {
        this.showProgress(false);
      }, 2000);
    }
  }
  
  async callArticle2AudioCLI(url) {
    const SERVER_URL = 'http://localhost:8888';
    
    try {
      // Check if server is running
      const statusResponse = await fetch(`${SERVER_URL}/status`);
      if (!statusResponse.ok) {
        throw new Error('Local server is not running. Please start server.py first.');
      }
      
      // Get cookies for the domain if it's a subscription site
      const cookies = await this.getCookiesForUrl(url);
      
      // Make conversion request
      const response = await fetch(`${SERVER_URL}/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          voice: this.settings.voice,
          speed: this.settings.speed,
          save_to_storage: this.settings.saveAudio,
          cookies: cookies
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        return {
          success: true,
          filename: result.audio_file || 'Unknown filename',
          duration: 'Conversion completed',
          output: result.output
        };
      } else {
        throw new Error(result.error || 'Unknown conversion error');
      }
      
    } catch (error) {
      console.error('CLI call failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async testCurrentPage() {
    if (!this.currentUrl) {
      this.updateStatus('No URL to test', 'error');
      return;
    }
    
    this.updateStatus('Testing article extraction...', 'info');
    
    try {
      const SERVER_URL = 'http://localhost:8888';
      
      // Check if server is running first
      const statusResponse = await fetch(`${SERVER_URL}/status`);
      if (!statusResponse.ok) {
        throw new Error('Local server is not running. Please start server.py first.');
      }
      
      // Test article extraction via server
      const response = await fetch(`${SERVER_URL}/test?url=${encodeURIComponent(this.currentUrl)}`);
      const result = await response.json();
      
      if (result.success) {
        this.updateStatus(`✅ Article test passed: ${result.estimated_duration}`, 'success');
      } else {
        this.updateStatus(`❌ Test failed: ${result.error}`, 'error');
      }
      
    } catch (error) {
      this.updateStatus(`Test failed: ${error.message}`, 'error');
      console.error('Page test error:', error);
    }
  }
  
  // This function runs in the context of the webpage
  analyzePageContent() {
    const selectors = [
      'article', '[role="main"]', '.article-content', '.post-content',
      '.entry-content', '.story-body', '.article-body', 'main .content'
    ];
    
    let bestContent = '';
    let title = document.title;
    
    // Try each selector to find article content
    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        const text = element.innerText || element.textContent;
        if (text && text.length > bestContent.length) {
          bestContent = text;
        }
      }
    }
    
    // Fallback to paragraphs
    if (bestContent.length < 200) {
      const paragraphs = document.querySelectorAll('p');
      bestContent = Array.from(paragraphs)
        .map(p => p.innerText || p.textContent)
        .filter(text => text && text.length > 50)
        .join(' ');
    }
    
    const wordCount = bestContent.split(/\s+/).length;
    const estimatedMinutes = Math.round(wordCount / 180 * 10) / 10;
    
    return {
      articleFound: bestContent.length > 500,
      title: title,
      wordCount: wordCount,
      estimatedMinutes: estimatedMinutes,
      contentLength: bestContent.length
    };
  }
  
  openSettings() {
    // In a full implementation, this would open a settings page
    this.updateStatus('Settings functionality coming soon!', 'info');
  }
  
  openLibrary() {
    // In a full implementation, this would open the audio library
    this.updateStatus('Audio library functionality coming soon!', 'info');
  }
  
  async getCookiesForUrl(url) {
    try {
      const urlObj = new URL(url);
      const domain = urlObj.hostname;
      
      // Check if this is a subscription site that might need cookies
      const subscriptionSites = [
        'nytimes.com', 'wsj.com', 'washingtonpost.com', 'ft.com',
        'economist.com', 'bloomberg.com', 'medium.com', 'substack.com',
        'reuters.com', 'newyorker.com', 'theatlantic.com', 'wired.com'
      ];
      
      const needsCookies = subscriptionSites.some(site => domain.includes(site));
      
      if (needsCookies) {
        // Get all cookies for this domain
        const cookies = await chrome.cookies.getAll({
          domain: domain.startsWith('.') ? domain : `.${domain}`
        });
        
        // Format cookies for server
        if (cookies.length > 0) {
          return cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
        }
      }
      
      return null;
    } catch (error) {
      console.warn('Failed to get cookies:', error);
      return null;
    }
  }

  openHelp() {
    // Open help documentation
    chrome.tabs.create({
      url: 'https://github.com/your-username/article-to-audio#usage'
    });
  }
}

// Initialize the popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new ArticleToAudioPopup();
});