// Article to Audio Extension Background Script

class ArticleToAudioBackground {
  constructor() {
    this.init();
  }
  
  init() {
    // Create context menu when extension is installed
    chrome.runtime.onInstalled.addListener(() => {
      this.createContextMenu();
    });
    
    // Handle context menu clicks
    chrome.contextMenus.onClicked.addListener((info, tab) => {
      this.handleContextMenuClick(info, tab);
    });
    
    // Handle messages from popup and content scripts
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async responses
    });
    
    // Handle extension icon clicks
    chrome.action.onClicked.addListener((tab) => {
      // The popup will handle this, but we can add fallback logic here
      console.log('Extension icon clicked for tab:', tab.url);
    });
  }
  
  createContextMenu() {
    // Remove existing context menus
    chrome.contextMenus.removeAll(() => {
      // Create main context menu item
      chrome.contextMenus.create({
        id: 'article-to-audio-main',
        title: '🎧 Convert to Audio',
        contexts: ['page', 'selection', 'link']
      });
      
      // Create submenu items
      chrome.contextMenus.create({
        id: 'convert-current-page',
        parentId: 'article-to-audio-main',
        title: '🎤 Convert This Page',
        contexts: ['page']
      });
      
      chrome.contextMenus.create({
        id: 'convert-selection',
        parentId: 'article-to-audio-main',
        title: '📝 Convert Selected Text',
        contexts: ['selection']
      });
      
      chrome.contextMenus.create({
        id: 'convert-link',
        parentId: 'article-to-audio-main',
        title: '🔗 Convert Linked Article',
        contexts: ['link']
      });
      
      // Add separator
      chrome.contextMenus.create({
        id: 'separator-1',
        parentId: 'article-to-audio-main',
        type: 'separator',
        contexts: ['page', 'selection', 'link']
      });
      
      // Quick voice options
      const voices = [
        { id: 'quick-christopher', title: '👨 Christopher (Deep)', voice: 'christopher' },
        { id: 'quick-guy', title: '👨 Guy (Rich)', voice: 'guy' },
        { id: 'quick-eric', title: '👨 Eric (Mature)', voice: 'eric' }
      ];
      
      voices.forEach(voice => {
        chrome.contextMenus.create({
          id: voice.id,
          parentId: 'article-to-audio-main',
          title: voice.title,
          contexts: ['page']
        });
      });
    });
  }
  
  async handleContextMenuClick(info, tab) {
    console.log('Context menu clicked:', info.menuItemId, 'on tab:', tab.url);
    
    try {
      switch (info.menuItemId) {
        case 'convert-current-page':
          await this.convertCurrentPage(tab);
          break;
          
        case 'convert-selection':
          await this.convertSelection(info.selectionText, tab);
          break;
          
        case 'convert-link':
          await this.convertLink(info.linkUrl, tab);
          break;
          
        case 'quick-christopher':
        case 'quick-guy':
        case 'quick-eric':
          const voice = info.menuItemId.replace('quick-', '');
          await this.convertWithVoice(tab.url, voice);
          break;
          
        default:
          console.log('Unknown context menu item:', info.menuItemId);
      }
    } catch (error) {
      console.error('Context menu action failed:', error);
      this.showNotification('Conversion failed: ' + error.message, 'error');
    }
  }
  
  async convertCurrentPage(tab) {
    // Send message to content script to extract article content
    try {
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'extractArticle'
      });
      
      if (response && response.success) {
        await this.processConversion({
          url: tab.url,
          title: response.title,
          content: response.content,
          method: 'current-page'
        });
      } else {
        throw new Error('Failed to extract article content');
      }
    } catch (error) {
      // Fallback: use the URL directly
      await this.processConversion({
        url: tab.url,
        method: 'url-fallback'
      });
    }
  }
  
  async convertSelection(selectionText, tab) {
    if (!selectionText || selectionText.trim().length < 50) {
      throw new Error('Selected text is too short for conversion');
    }
    
    await this.processConversion({
      url: tab.url,
      title: 'Selected Text',
      content: selectionText,
      method: 'selection'
    });
  }
  
  async convertLink(linkUrl, tab) {
    await this.processConversion({
      url: linkUrl,
      method: 'link'
    });
  }
  
  async convertWithVoice(url, voice) {
    await this.processConversion({
      url: url,
      voice: voice,
      method: 'quick-voice'
    });
  }
  
  async processConversion(params) {
    // Show processing notification
    this.showNotification('🎤 Starting article-to-audio conversion...', 'info');
    
    // Get user settings
    const settings = await this.getSettings();
    
    // Prepare conversion parameters
    const conversionParams = {
      url: params.url,
      voice: params.voice || settings.voice || 'christopher',
      speed: settings.speed || 'fast',
      saveAudio: settings.saveAudio || false,
      method: params.method || 'unknown'
    };
    
    // In a real implementation, this would call the CLI
    // For now, we'll simulate the process
    try {
      const result = await this.simulateConversion(conversionParams);
      
      if (result.success) {
        this.showNotification(
          `✅ Audio generated! Duration: ${result.duration}`,
          'success'
        );
        
        // Store conversion history
        await this.storeConversionHistory({
          url: params.url,
          title: params.title || 'Article',
          voice: conversionParams.voice,
          timestamp: Date.now(),
          filename: result.filename
        });
        
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      this.showNotification('❌ Conversion failed: ' + error.message, 'error');
      throw error;
    }
  }
  
  async simulateConversion(params) {
    // Simulate conversion delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Simulate successful conversion
    return {
      success: true,
      filename: `article_${Date.now()}_${params.voice}.mp3`,
      duration: '3.7 minutes',
      fileSize: '1.2 MB'
    };
  }
  
  async getSettings() {
    try {
      return await chrome.storage.sync.get(['voice', 'speed', 'saveAudio']);
    } catch (error) {
      return {
        voice: 'christopher',
        speed: 'fast',
        saveAudio: false
      };
    }
  }
  
  async storeConversionHistory(entry) {
    try {
      const { conversionHistory = [] } = await chrome.storage.local.get(['conversionHistory']);
      conversionHistory.unshift(entry);
      
      // Keep only the last 50 conversions
      if (conversionHistory.length > 50) {
        conversionHistory.splice(50);
      }
      
      await chrome.storage.local.set({ conversionHistory });
    } catch (error) {
      console.error('Failed to store conversion history:', error);
    }
  }
  
  showNotification(message, type = 'info') {
    const iconMap = {
      info: 'icons/icon-48.png',
      success: 'icons/icon-48.png',
      error: 'icons/icon-48.png'
    };
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: iconMap[type] || iconMap.info,
      title: 'Article to Audio',
      message: message
    });
  }
  
  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'convertUrl':
          const result = await this.processConversion({
            url: message.url,
            voice: message.voice,
            method: 'popup'
          });
          sendResponse({ success: true, result });
          break;
          
        case 'getConversionHistory':
          const { conversionHistory = [] } = await chrome.storage.local.get(['conversionHistory']);
          sendResponse({ success: true, history: conversionHistory });
          break;
          
        case 'clearHistory':
          await chrome.storage.local.remove(['conversionHistory']);
          sendResponse({ success: true });
          break;
          
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Message handling error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
}

// Initialize background script
new ArticleToAudioBackground();