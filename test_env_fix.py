#!/usr/bin/env python3
"""
Test if the environment variable fix worked
Run this after adding SUPABASE_SERVICE_KEY to Render
"""

import requests
import time

BASE_URL = "https://article-to-audio-extension-1.onrender.com"

def test_env_fix():
    """Test if Supabase connection is working after env fix"""
    
    print("🔍 Testing environment variable fix...")
    print("(Make sure you added SUPABASE_SERVICE_KEY to Render first)")
    
    # Wait a moment for deployment to update
    print("⏳ Waiting 30 seconds for Render to update environment...")
    time.sleep(30)
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
            
            if data.get('supabase_connected'):
                print("🎉 Environment fix worked! Supabase is connected!")
                return True
            else:
                print("⚠️ Still not connected - may need schema update")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_database_endpoint():
    """Test if database endpoints are working"""
    
    print("\n📊 Testing database endpoints...")
    
    try:
        response = requests.get(f"{BASE_URL}/articles", timeout=10)
        print(f"Articles endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Database endpoints working!")
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Environment Variable Fix")
    print("=" * 50)
    
    if test_env_fix():
        if test_database_endpoint():
            print("\n✅ Ready for schema update and enhanced deployment!")
        else:
            print("\n⚠️ Need to update schema next")
    else:
        print("\n❌ Environment fix didn't work - proceeding to enhanced server")