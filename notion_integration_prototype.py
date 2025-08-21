#!/usr/bin/env python3
"""
Notion Integration Prototype for Article-to-Audio Extension
This is a design prototype - no actual Notion API calls yet
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class NotionArticleSync:
    """
    Syncs audio articles to Notion as a master calendar/database
    """
    
    def __init__(self, notion_token: str, database_id: str):
        """
        Initialize Notion sync with authentication
        
        Args:
            notion_token: Notion Integration Token (from notion.so/my-integrations)
            database_id: ID of Notion database for articles
        """
        self.token = notion_token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_article_page(self, article_data: Dict) -> Dict:
        """
        Create a new page in Notion for an article
        
        Expected Notion Database Schema:
        - Title (title): Article title
        - URL (url): Original article URL  
        - Audio URL (url): Link to audio file
        - Converted Date (date): When converted to audio
        - Duration (number): Audio duration in minutes
        - Voice (select): TTS voice used
        - Tags (multi-select): Article categories
        - Status (select): New, Listened, Archived
        - Notes (rich_text): Personal notes
        - Favorite (checkbox): Is favorite
        """
        
        notion_page = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": article_data.get("title", "Untitled")
                            }
                        }
                    ]
                },
                "URL": {
                    "url": article_data.get("source_url")
                },
                "Audio URL": {
                    "url": article_data.get("audio_url")
                },
                "Converted Date": {
                    "date": {
                        "start": article_data.get("created_at", datetime.now().isoformat())
                    }
                },
                "Voice": {
                    "select": {
                        "name": article_data.get("voice", "Christopher").replace("en-US-", "").replace("Neural", "")
                    }
                },
                "Status": {
                    "select": {
                        "name": "New"
                    }
                },
                "Word Count": {
                    "number": article_data.get("word_count", 0)
                },
                "Favorite": {
                    "checkbox": article_data.get("is_favorite", False)
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Article content preview:\n{article_data.get('content', '')[:500]}..."
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "audio",
                    "audio": {
                        "type": "external",
                        "external": {
                            "url": article_data.get("audio_url", "")
                        }
                    }
                }
            ]
        }
        
        # This would make the API call:
        # response = requests.post(
        #     "https://api.notion.com/v1/pages",
        #     headers=self.headers,
        #     json=notion_page
        # )
        
        return notion_page
    
    def sync_from_supabase(self, articles: List[Dict]) -> List[Dict]:
        """
        Sync articles from Supabase to Notion
        """
        synced_pages = []
        
        for article in articles:
            # Check if article already exists in Notion (by source_url or id)
            # If not, create new page
            page = self.create_article_page(article)
            synced_pages.append(page)
        
        return synced_pages
    
    def create_database_template(self) -> Dict:
        """
        Returns the Notion database structure for initial setup
        """
        return {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "📚 Audio Articles Library"
                    }
                }
            ],
            "properties": {
                "Title": {"title": {}},
                "URL": {"url": {}},
                "Audio URL": {"url": {}},
                "Converted Date": {"date": {}},
                "Voice": {
                    "select": {
                        "options": [
                            {"name": "Christopher", "color": "blue"},
                            {"name": "Brian", "color": "green"},
                            {"name": "Emma", "color": "purple"},
                            {"name": "Jenny", "color": "pink"}
                        ]
                    }
                },
                "Status": {
                    "select": {
                        "options": [
                            {"name": "New", "color": "yellow"},
                            {"name": "Listening", "color": "blue"},
                            {"name": "Listened", "color": "green"},
                            {"name": "Archived", "color": "gray"}
                        ]
                    }
                },
                "Tags": {
                    "multi_select": {
                        "options": [
                            {"name": "Tech", "color": "blue"},
                            {"name": "Business", "color": "green"},
                            {"name": "AI", "color": "purple"},
                            {"name": "Tutorial", "color": "orange"},
                            {"name": "News", "color": "red"}
                        ]
                    }
                },
                "Word Count": {"number": {"format": "number"}},
                "Duration (min)": {"number": {"format": "number"}},
                "Favorite": {"checkbox": {}},
                "Notes": {"rich_text": {}}
            }
        }


class ChromeExtensionNotionFlow:
    """
    Alternative flow: Chrome extension → Notion directly
    """
    
    def convert_and_save_to_notion(self, article_data: Dict) -> Dict:
        """
        1. Chrome extension extracts article
        2. Sends to our server for audio conversion
        3. Server returns audio URL
        4. Extension saves directly to Notion
        """
        
        # This would be in the Chrome extension JavaScript:
        flow = {
            "step1": "Extract article content from current tab",
            "step2": "POST to /convert endpoint for audio",
            "step3": "Receive audio_url from server",
            "step4": "Create Notion page with article + audio",
            "step5": "Open Notion page for user to add notes/tags"
        }
        
        # Chrome extension would use Notion API directly:
        chrome_extension_code = """
        // In popup.js
        async function saveToNotion(articleData) {
            const notionToken = await chrome.storage.sync.get('notionToken');
            const databaseId = await chrome.storage.sync.get('notionDatabaseId');
            
            const response = await fetch('https://api.notion.com/v1/pages', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${notionToken}`,
                    'Content-Type': 'application/json',
                    'Notion-Version': '2022-06-28'
                },
                body: JSON.stringify({
                    parent: { database_id: databaseId },
                    properties: {
                        Title: { title: [{ text: { content: articleData.title }}]},
                        URL: { url: articleData.source_url },
                        'Audio URL': { url: articleData.audio_url },
                        // ... other properties
                    }
                })
            });
            
            return response.json();
        }
        """
        
        return {"flow": flow, "sample_code": chrome_extension_code}


# Webhook Integration for automatic sync
class NotionWebhookSync:
    """
    Set up webhooks for bi-directional sync
    """
    
    def supabase_to_notion_webhook(self):
        """
        Supabase webhook → Our server → Notion API
        
        When new article added to Supabase:
        1. Supabase triggers webhook to our /webhook/notion endpoint
        2. Our server creates corresponding Notion page
        3. Updates Supabase with Notion page ID for linking
        """
        
        webhook_endpoint = """
        @app.post("/webhook/notion")
        async def handle_notion_sync(payload: Dict):
            # Get new article from Supabase webhook
            article = payload['record']
            
            # Create Notion page
            notion_sync = NotionArticleSync(NOTION_TOKEN, DATABASE_ID)
            notion_page = notion_sync.create_article_page(article)
            
            # Update Supabase with Notion page ID
            supabase.table('articles').update({
                'notion_page_id': notion_page['id']
            }).eq('id', article['id']).execute()
            
            return {"status": "synced", "notion_id": notion_page['id']}
        """
        
        return webhook_endpoint


# Calendar View Configuration
def notion_calendar_views():
    """
    Different Notion database views for the audio library
    """
    
    views = {
        "Daily Reading List": {
            "type": "calendar",
            "group_by": "Converted Date",
            "filter": {
                "property": "Status",
                "select": {"does_not_equal": "Archived"}
            }
        },
        "Favorites": {
            "type": "gallery",
            "filter": {
                "property": "Favorite",
                "checkbox": {"equals": True}
            }
        },
        "By Topic": {
            "type": "board",
            "group_by": "Tags"
        },
        "Reading Queue": {
            "type": "list",
            "filter": {
                "property": "Status",
                "select": {"equals": "New"}
            },
            "sort": [
                {"property": "Converted Date", "direction": "descending"}
            ]
        },
        "Weekly Review": {
            "type": "timeline",
            "date_property": "Converted Date"
        }
    }
    
    return views


# Usage Example
if __name__ == "__main__":
    print("Notion Integration Prototype")
    print("=" * 50)
    
    # Example article from our system
    sample_article = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Understanding Notion API Integration",
        "content": "This article explains how to integrate with Notion...",
        "source_url": "https://example.com/notion-guide",
        "audio_url": "data:audio/mpeg;base64,//NkxAA...",
        "voice": "en-US-ChristopherNeural",
        "word_count": 1500,
        "created_at": datetime.now().isoformat(),
        "is_favorite": True
    }
    
    # Initialize sync (would need actual token/database_id)
    # notion = NotionArticleSync("secret_xxx", "database_id_xxx")
    
    # Create Notion page structure
    notion = NotionArticleSync("dummy_token", "dummy_db_id")
    page_structure = notion.create_article_page(sample_article)
    
    print("\n📝 Notion Page Structure:")
    print(json.dumps(page_structure, indent=2)[:500] + "...")
    
    print("\n📅 Available Calendar Views:")
    for view_name, view_config in notion_calendar_views().items():
        print(f"  - {view_name}: {view_config['type']} view")
    
    print("\n🔄 Integration Options:")
    print("  1. Batch sync from Supabase → Notion")
    print("  2. Real-time webhook sync")
    print("  3. Chrome extension → Notion direct")
    print("  4. Bi-directional sync with conflict resolution")
    
    print("\n✅ Next Steps:")
    print("  1. Create Notion integration at notion.so/my-integrations")
    print("  2. Get integration token")
    print("  3. Create database with schema above")
    print("  4. Share database with integration")
    print("  5. Add token to environment variables")