#!/usr/bin/env python3
"""
Test the production API after Render deployment
Update the BASE_URL to your Render deployment URL
"""

import requests
import json
import time

# UPDATE THIS TO YOUR RENDER URL
BASE_URL = "https://article-to-audio-extension-1.onrender.com"

def test_production_health():
    """Test production health endpoint"""
    print("🔍 Testing production health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Supabase: {data.get('supabase_connected', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_production_conversion():
    """Test article conversion in production"""
    print("\n🎵 Testing production article conversion...")
    try:
        data = {
            "title": "Production Test Article",
            "content": "This is a comprehensive test article for the production deployment. It contains sufficient content to generate meaningful audio output and verify that all systems are working correctly in the cloud environment.",
            "url": "https://production-test.example.com",
            "voice": "en-US-BrianNeural",
            "user_email": "production-test@example.com"
        }
        
        print("   Sending conversion request...")
        response = requests.post(f"{BASE_URL}/convert", json=data, timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Conversion successful")
            print(f"   Article ID: {result.get('article_id', 'N/A')}")
            print(f"   Audio URL: {result.get('audio_url', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return result
        else:
            print(f"❌ Conversion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

def test_production_library():
    """Test library access in production"""
    print("\n📚 Testing production library access...")
    try:
        response = requests.get(f"{BASE_URL}/library/production-test@example.com", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            print(f"✅ Library access successful - {len(articles)} articles found")
            
            if articles:
                print("   Recent articles:")
                for article in articles[:3]:
                    print(f"   - {article.get('title', 'No title')[:50]}...")
            
            return True
        else:
            print(f"❌ Library access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Library access error: {e}")
        return False

def test_production_signup():
    """Test user signup in production"""
    print("\n👤 Testing production user signup...")
    try:
        data = {
            "email": "production-test@example.com",
            "display_name": "Production Test User"
        }
        
        response = requests.post(f"{BASE_URL}/signup", json=data, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Signup successful")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False

def test_cors_headers():
    """Test CORS headers for browser extension"""
    print("\n🌐 Testing CORS headers...")
    try:
        response = requests.options(f"{BASE_URL}/health", headers={
            'Origin': 'chrome-extension://abcdef',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }, timeout=10)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS headers present")
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
            return True
        else:
            print("❌ CORS headers missing")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def run_production_tests():
    """Run all production tests"""
    print("🚀 Testing Production Article-to-Audio API")
    print(f"🔗 Base URL: {BASE_URL}")
    print("=" * 60)
    
    if "https://article-to-audio-server.onrender.com" in BASE_URL:
        print("⚠️  Please update BASE_URL with your actual Render deployment URL")
        print("   Find it in your Render dashboard after deployment")
        print("=" * 60)
    
    tests = [
        test_production_health,
        test_cors_headers,
        test_production_signup,
        test_production_conversion,
        test_production_library
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"🏁 Production tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Production deployment is working perfectly!")
        print("\n✅ Ready for:")
        print("   - Chrome extension update")
        print("   - User testing")
        print("   - Feature enhancements")
    else:
        print("⚠️ Some tests failed - check the issues above")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check Render deployment logs")
        print("   2. Verify environment variables")
        print("   3. Test Supabase connection")
        print("   4. Wait for full deployment completion")
    
    print(f"\n📊 Monitor service: python3 production_monitor.py --url {BASE_URL}")
    
    return passed == total

if __name__ == "__main__":
    success = run_production_tests()
    exit(0 if success else 1)