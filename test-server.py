#!/usr/bin/env python3
"""
Test the article to audio server
"""
import requests
import json

def test_server():
    SERVER_URL = 'http://localhost:8888'
    
    print("🧪 Testing Article to Audio Server")
    print("=" * 40)
    
    # Test 1: Check status endpoint
    try:
        print("1️⃣ Testing status endpoint...")
        response = requests.get(f"{SERVER_URL}/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running!")
            print(f"   📋 Response: {response.json()}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        print(f"   💡 Make sure server is running:")
        print(f"      python3 server.py")
        return False
    
    # Test 2: Test article extraction
    test_url = "https://www.bbc.com/news/articles/c5yll33v9gwo"
    print(f"\n2️⃣ Testing article extraction with: {test_url}")
    
    try:
        response = requests.get(f"{SERVER_URL}/test", params={'url': test_url}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Article test passed!")
            print(f"   📋 Result: {result}")
        else:
            print(f"   ❌ Article test failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Article test error: {e}")
    
    # Test 3: Test conversion (simulation only for now)
    print(f"\n3️⃣ Testing conversion endpoint...")
    
    try:
        payload = {
            'url': test_url,
            'voice': 'christopher',
            'speed': 'fast', 
            'save_to_storage': False
        }
        
        response = requests.post(
            f"{SERVER_URL}/convert",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Conversion test passed!")
                print(f"   🎵 Audio file: {result.get('audio_file', 'Not specified')}")
            else:
                print("   ❌ Conversion failed:")
                print(f"      Error: {result.get('error')}")
        else:
            print(f"   ❌ Conversion request failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Conversion test error: {e}")
    
    print(f"\n✅ Server testing complete!")
    print(f"💡 If all tests pass, the extension should work!")

if __name__ == '__main__':
    test_server()