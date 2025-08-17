#!/usr/bin/env python3
"""
Integration tests for Article-to-Audio FastAPI server with Supabase
Tests all endpoints and database operations
"""

import requests
import json
import time
import os
from typing import Dict, Any

# Server configuration
BASE_URL = "http://localhost:5000"  # Change to Render URL after deployment
TEST_EMAIL = "test@example.com"
TEST_DISPLAY_NAME = "Test User"

def test_server_health():
    """Test if server is running and responsive"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not reachable: {e}")
        return False

def test_user_signup():
    """Test user signup functionality"""
    print("\n👤 Testing user signup...")
    try:
        data = {
            "email": TEST_EMAIL,
            "display_name": TEST_DISPLAY_NAME
        }
        response = requests.post(f"{BASE_URL}/signup", json=data, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ User signup successful")
            print(f"   User ID: {result.get('user_id', 'N/A')}")
            return True
        else:
            print(f"❌ User signup failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ User signup error: {e}")
        return False

def test_user_signin():
    """Test user signin functionality"""
    print("\n🔑 Testing user signin...")
    try:
        data = {"email": TEST_EMAIL}
        response = requests.post(f"{BASE_URL}/signin", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User signin successful")
            print(f"   User: {result.get('display_name', 'N/A')}")
            return True
        else:
            print(f"❌ User signin failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ User signin error: {e}")
        return False

def test_article_conversion():
    """Test article to audio conversion"""
    print("\n🎵 Testing article conversion...")
    try:
        # Test with a simple text article
        data = {
            "url": "https://example.com/test-article",
            "title": "Integration Test Article",
            "content": "This is a test article for integration testing. It contains enough text to generate meaningful audio output for our testing purposes.",
            "voice": "en-US-BrianNeural",
            "user_email": TEST_EMAIL
        }
        
        response = requests.post(f"{BASE_URL}/convert", json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Article conversion successful")
            print(f"   Audio URL: {result.get('audio_url', 'N/A')}")
            print(f"   Article ID: {result.get('article_id', 'N/A')}")
            return result
        else:
            print(f"❌ Article conversion failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Article conversion error: {e}")
        return None

def test_library_access(user_email: str):
    """Test user library access"""
    print("\n📚 Testing library access...")
    try:
        response = requests.get(f"{BASE_URL}/library/{user_email}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Library access successful")
            print(f"   Found {len(result.get('articles', []))} articles")
            return result
        else:
            print(f"❌ Library access failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Library access error: {e}")
        return None

def test_article_operations(article_id: str):
    """Test article update and delete operations"""
    print(f"\n🔧 Testing article operations for ID: {article_id}")
    
    # Test update - mark as favorite
    try:
        data = {"is_favorite": True}
        response = requests.put(f"{BASE_URL}/articles/{article_id}", json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Article update successful")
        else:
            print(f"❌ Article update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Article update error: {e}")
        return False
    
    # Test delete
    try:
        response = requests.delete(f"{BASE_URL}/articles/{article_id}", timeout=10)
        
        if response.status_code in [200, 204]:
            print("✅ Article delete successful")
            return True
        else:
            print(f"❌ Article delete failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Article delete error: {e}")
        return False

def test_audio_upload():
    """Test audio file upload to storage"""
    print("\n📤 Testing audio upload...")
    try:
        # Create a small test audio file
        test_audio_content = b"RIFF" + b"\x00" * 36 + b"WAVE"  # Minimal WAV header
        
        files = {
            'audio': ('test.wav', test_audio_content, 'audio/wav')
        }
        data = {
            'user_email': TEST_EMAIL,
            'filename': 'integration_test.wav'
        }
        
        response = requests.post(f"{BASE_URL}/upload-audio", files=files, data=data, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Audio upload successful")
            print(f"   File URL: {result.get('public_url', 'N/A')}")
            return result
        else:
            print(f"❌ Audio upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Audio upload error: {e}")
        return None

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n⚠️ Testing error handling...")
    
    # Test invalid article conversion
    try:
        data = {"invalid": "data"}
        response = requests.post(f"{BASE_URL}/convert", json=data, timeout=10)
        
        if response.status_code >= 400:
            print("✅ Error handling for invalid conversion data works")
        else:
            print("❌ Error handling failed - should have returned 4xx status")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test non-existent article access
    try:
        response = requests.get(f"{BASE_URL}/articles/non-existent-id", timeout=10)
        
        if response.status_code == 404:
            print("✅ Error handling for non-existent article works")
        else:
            print("❌ Error handling failed - should have returned 404")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Article-to-Audio Integration Tests")
    print("=" * 60)
    
    # Test 1: Server health
    if not test_server_health():
        print("\n❌ Integration tests failed - server not accessible")
        return False
    
    # Test 2: User management
    test_user_signup()
    test_user_signin()
    
    # Test 3: Core functionality
    conversion_result = test_article_conversion()
    
    # Test 4: Library operations
    test_library_access(TEST_EMAIL)
    
    # Test 5: Article operations
    if conversion_result and conversion_result.get('article_id'):
        test_article_operations(conversion_result['article_id'])
    
    # Test 6: File upload
    test_audio_upload()
    
    # Test 7: Error handling
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("🏁 Integration tests completed!")
    print("\n💡 Next steps:")
    print("   1. Review any failed tests above")
    print("   2. Check server logs for errors")
    print("   3. Verify Supabase data in dashboard")
    print("   4. Test with real article URLs")

if __name__ == "__main__":
    run_integration_tests()