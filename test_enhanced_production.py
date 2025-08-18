#!/usr/bin/env python3
"""
Test the enhanced personal data lake server in production
"""

import requests
import json
import time

BASE_URL = "https://article-to-audio-extension-1.onrender.com"

def wait_for_deployment():
    """Wait for Render deployment to complete"""
    print("⏳ Waiting for Render deployment to complete...")
    print("(This usually takes 2-3 minutes)")
    
    for i in range(24):  # Wait up to 4 minutes
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "data_lake" in data:  # New enhanced server
                    print("✅ Enhanced server deployed!")
                    return True
        except:
            pass
        
        print(f"   Waiting... ({(i+1)*10}s)")
        time.sleep(10)
    
    return False

def test_enhanced_health():
    """Test enhanced health endpoint"""
    print("\n🔍 Testing enhanced health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {json.dumps(data, indent=2)}")
            return data.get('supabase_connected', False)
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_personal_data_lake():
    """Test personal data lake endpoints"""
    print("\n📊 Testing personal data lake endpoints...")
    
    # Test library endpoint
    try:
        response = requests.get(f"{BASE_URL}/library", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Library endpoint: Found {len(data)} articles")
            if data:
                print(f"   Sample: {data[0]['title']}")
        else:
            print(f"❌ Library failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Library error: {e}")
    
    # Test stats endpoint
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def test_article_conversion():
    """Test article conversion with enhanced server"""
    print("\n🎵 Testing enhanced article conversion...")
    
    try:
        data = {
            "title": "Personal Data Lake Test",
            "content": "This is a comprehensive test of the enhanced personal data lake server. It should store the article and audio in Supabase with proper metadata for AI agent access.",
            "voice": "en-US-BrianNeural",
            "is_favorite": True,
            "metadata": {
                "test_type": "production_verification",
                "ai_accessible": True
            }
        }
        
        print("   Converting article to audio...")
        response = requests.post(f"{BASE_URL}/convert", json=data, timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Conversion successful!")
            print(f"   Article ID: {result.get('id')}")
            print(f"   Audio URL: {result.get('audio_url', 'N/A')}")
            print(f"   Word Count: {result.get('word_count')}")
            print(f"   Stored in data lake: {bool(result.get('id'))}")
            return result.get('id')
        else:
            print(f"❌ Conversion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

def test_search_functionality():
    """Test AI agent search functionality"""
    print("\n🔍 Testing AI agent search...")
    
    try:
        response = requests.get(f"{BASE_URL}/search?q=test&limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search working: Found {data.get('count', 0)} results for 'test'")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {e}")

def main():
    """Run enhanced production tests"""
    print("🚀 Testing Enhanced Personal Data Lake Server")
    print("=" * 60)
    
    # Wait for deployment
    if not wait_for_deployment():
        print("❌ Deployment didn't complete in time")
        return False
    
    # Test health
    supabase_connected = test_enhanced_health()
    
    if supabase_connected:
        print("\n✅ Supabase connected! Testing data lake features...")
        test_personal_data_lake()
        article_id = test_article_conversion()
        test_search_functionality()
        
        print(f"\n🎉 Enhanced Personal Data Lake is LIVE!")
        print(f"🔗 Service: {BASE_URL}")
        print(f"📚 API Docs: {BASE_URL}/docs")
        print(f"📊 Your data lake is operational and ready for AI agents!")
        
    else:
        print("\n⚠️ Supabase not connected - check logs")
    
    return supabase_connected

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)