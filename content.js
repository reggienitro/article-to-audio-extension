// Article to Audio Extension Content Script

class ArticleToAudioContent {
  constructor() {
    this.init();
  }
  
  init() {
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async responses
    });
    
    // Add visual indicators for article content (optional)
    this.detectAndHighlightArticles();
  }
  
  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'extractArticle':
          const article = await this.extractArticleContent();
          sendResponse({ success: true, ...article });
          break;
          
        case 'analyzePageContent':
          const analysis = this.analyzePageContent();
          sendResponse({ success: true, ...analysis });
          break;
          
        case 'highlightArticleContent':
          this.highlightArticleContent();
          sendResponse({ success: true });
          break;
          
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Content script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  
  async extractArticleContent() {
    const selectors = [
      // Primary article selectors
      'article',
      '[role="main"] article',
      '.article-content',
      '.post-content',
      '.entry-content',
      
      // News-specific selectors
      '.story-body',
      '.article-body',
      '.post-body',
      '.content-body',
      '.story-content',
      
      // Blog-specific selectors
      '.post-full-content',
      '.entry-body',
      '.article-wrap .content',
      
      // Fallback selectors
      'main .content',
      '.main-content',
      '#content .content',
      '.content'
    ];
    
    let bestContent = '';
    let bestElement = null;
    let title = this.extractTitle();
    
    // Try each selector to find the best article content
    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      
      for (const element of elements) {
        const text = this.getElementText(element);
        if (text && text.length > bestContent.length && this.isValidArticleContent(text)) {
          bestContent = text;
          bestElement = element;
        }
      }
      
      // If we found substantial content, we can stop
      if (bestContent.length > 1000) {
        break;
      }
    }
    
    // Fallback to paragraph extraction if no good article element found
    if (bestContent.length < 500) {
      const paragraphs = document.querySelectorAll('p');
      const paragraphTexts = Array.from(paragraphs)
        .map(p => this.getElementText(p))
        .filter(text => text && text.length > 30);
      
      if (paragraphTexts.length > 0) {
        bestContent = paragraphTexts.join(' ');
      }
    }
    
    // Clean the extracted content
    bestContent = this.cleanExtractedText(bestContent);
    
    const wordCount = bestContent.split(/\s+/).filter(word => word.length > 0).length;
    const estimatedMinutes = Math.round(wordCount / 180 * 10) / 10;
    
    return {
      title: title,
      content: bestContent,
      wordCount: wordCount,
      estimatedMinutes: estimatedMinutes,
      url: window.location.href,
      extractionMethod: bestElement ? bestElement.tagName.toLowerCase() : 'paragraphs'
    };
  }
  
  extractTitle() {
    // Try multiple methods to get the best title
    const titleSelectors = [
      'h1',
      '.article-title h1',
      '.post-title h1',
      '.headline',
      '.article-headline',
      '.entry-title',
      '.story-headline',
      'header h1'
    ];
    
    for (const selector of titleSelectors) {
      const element = document.querySelector(selector);
      if (element) {
        const title = this.getElementText(element);
        if (title && title.length > 5 && title.length < 200) {
          return title;
        }
      }
    }
    
    // Fallback to document title, cleaned up
    let title = document.title;
    
    // Remove common suffixes from page titles
    const suffixesToRemove = [
      / - .+$/,  // " - Site Name"
      / \| .+$/,  // " | Site Name"  
      / :: .+$/,  // " :: Site Name"
      / \(.+\)$/  // " (Site Name)"
    ];
    
    for (const suffix of suffixesToRemove) {
      title = title.replace(suffix, '');
    }
    
    return title.trim() || 'Article';
  }
  
  getElementText(element) {
    if (!element) return '';
    
    // Remove unwanted child elements
    const clone = element.cloneNode(true);
    const unwantedSelectors = [
      'script', 'style', 'nav', 'aside', 'footer',
      '.advertisement', '.ad', '.ads', '.social-share',
      '.comments', '.comment-section', '.newsletter-signup'
    ];
    
    unwantedSelectors.forEach(selector => {
      const unwantedElements = clone.querySelectorAll(selector);
      unwantedElements.forEach(el => el.remove());
    });
    
    return clone.innerText || clone.textContent || '';
  }
  
  isValidArticleContent(text) {
    // Check if the text looks like article content
    const minLength = 200;
    const maxCommonWordsRatio = 0.7; // Max ratio of very common words
    
    if (text.length < minLength) return false;
    
    // Check for excessive common words (might be navigation/UI text)
    const words = text.toLowerCase().split(/\s+/);
    const commonWords = new Set([
      'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
      'click', 'here', 'more', 'read', 'see', 'view', 'subscribe', 'follow', 'share'
    ]);
    
    const commonWordCount = words.filter(word => commonWords.has(word)).length;
    const commonWordsRatio = commonWordCount / words.length;
    
    return commonWordsRatio < maxCommonWordsRatio;
  }
  
  cleanExtractedText(text) {
    if (!text) return '';
    
    // Remove extra whitespace
    text = text.replace(/\s+/g, ' ');
    
    // Remove common web artifacts
    const artifactsToRemove = [
      /Skip to main content/gi,
      /Skip to content/gi,
      /Advertisement/gi,
      /Subscribe to continue/gi,
      /Sign up for/gi,
      /Follow us on/gi,
      /Share this article/gi,
      /Click here/gi,
      /Read more/gi,
      /© \d{4}.*$/gm,
      /All rights reserved.*$/gm
    ];
    
    artifactsToRemove.forEach(pattern => {
      text = text.replace(pattern, '');
    });
    
    // Improve text for TTS
    const replacements = {
      '&': ' and ',
      '@': ' at ',
      '#': ' hashtag ',
      'vs.': 'versus',
      'etc.': 'etcetera',
      'i.e.': 'that is',
      'e.g.': 'for example'
    };
    
    Object.entries(replacements).forEach(([search, replace]) => {
      text = text.replace(new RegExp(search, 'g'), replace);
    });
    
    return text.trim();
  }
  
  analyzePageContent() {
    const analysis = {
      hasArticleElement: !!document.querySelector('article'),
      hasMainElement: !!document.querySelector('main'),
      paragraphCount: document.querySelectorAll('p').length,
      headingCount: document.querySelectorAll('h1, h2, h3').length,
      wordCount: 0,
      estimatedReadingTime: 0,
      isLikelyArticle: false
    };
    
    // Get rough word count from all paragraphs
    const allText = Array.from(document.querySelectorAll('p'))
      .map(p => p.innerText || p.textContent)
      .join(' ');
    
    analysis.wordCount = allText.split(/\s+/).filter(word => word.length > 0).length;
    analysis.estimatedReadingTime = Math.round(analysis.wordCount / 200 * 10) / 10; // Reading speed ~200 WPM
    
    // Determine if this looks like an article
    analysis.isLikelyArticle = (
      analysis.wordCount > 300 &&
      analysis.paragraphCount > 3 &&
      (analysis.hasArticleElement || analysis.hasMainElement)
    );
    
    return analysis;
  }
  
  detectAndHighlightArticles() {
    // Add subtle visual indicator for detected article content
    const articleElements = document.querySelectorAll('article, .article-content, .post-content');
    
    articleElements.forEach(element => {
      if (element.innerText && element.innerText.length > 500) {
        element.style.position = 'relative';
        
        // Add a small indicator
        const indicator = document.createElement('div');
        indicator.style.cssText = `
          position: absolute;
          top: -5px;
          right: -5px;
          width: 20px;
          height: 20px;
          background: #4a90e2;
          border-radius: 50%;
          font-size: 12px;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          opacity: 0.7;
          cursor: pointer;
          transition: opacity 0.2s;
        `;
        indicator.innerHTML = '🎧';
        indicator.title = 'Convert this article to audio';
        
        indicator.addEventListener('click', () => {
          chrome.runtime.sendMessage({
            action: 'convertArticleElement',
            element: element.outerHTML
          });
        });
        
        indicator.addEventListener('mouseenter', () => {
          indicator.style.opacity = '1';
        });
        
        indicator.addEventListener('mouseleave', () => {
          indicator.style.opacity = '0.7';
        });
        
        element.appendChild(indicator);
      }
    });
  }
  
  highlightArticleContent() {
    // Temporarily highlight the detected article content
    const article = document.querySelector('article, .article-content, .post-content');
    
    if (article) {
      const originalBorder = article.style.border;
      const originalBackground = article.style.background;
      
      article.style.border = '3px solid #4a90e2';
      article.style.background = 'rgba(74, 144, 226, 0.1)';
      
      setTimeout(() => {
        article.style.border = originalBorder;
        article.style.background = originalBackground;
      }, 2000);
    }
  }
}

// Initialize content script
new ArticleToAudioContent();