#!/usr/bin/env python3
"""
Monitor for enhanced server deployment
"""

import requests
import time
import json

BASE_URL = "https://article-to-audio-extension-1.onrender.com"

def check_enhanced_server():
    """Check if enhanced server is live"""
    try:
        # Method 1: Check API info
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            title = data.get('info', {}).get('title', '')
            version = data.get('info', {}).get('version', '')
            
            if 'Personal Data Lake' in title:
                return True, f"Enhanced server detected: {title} v{version}"
        
        # Method 2: Check for enhanced endpoints
        response = requests.get(f"{BASE_URL}/library", timeout=5)
        if response.status_code != 404:  # 404 = endpoint not found (old server)
            return True, "Enhanced endpoints detected (/library working)"
        
        # Method 3: Check health response structure
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            if 'data_lake' in health:
                return True, "Enhanced health response detected"
        
        return False, "Still old server"
        
    except Exception as e:
        return False, f"Error checking: {e}"

def monitor():
    """Monitor deployment progress"""
    print("🔍 Monitoring for enhanced server deployment...")
    print("⏳ Checking every 15 seconds...")
    print("-" * 50)
    
    for i in range(40):  # Monitor for 10 minutes
        enhanced, status = check_enhanced_server()
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}")
        
        if enhanced:
            print("\n🎉 Enhanced server is LIVE!")
            
            # Test immediately
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                if response.status_code == 200:
                    health = response.json()
                    print("🔍 Enhanced health check:")
                    print(json.dumps(health, indent=2))
                    
                    if health.get('supabase_connected'):
                        print("\n✅ Supabase connected!")
                        print("✅ Personal data lake operational!")
                    else:
                        print("\n⚠️ Supabase connection still pending")
                
                # Test new endpoints
                response = requests.get(f"{BASE_URL}/stats", timeout=10)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"\n📊 Data lake stats: {stats}")
                
            except Exception as e:
                print(f"Error testing enhanced features: {e}")
            
            return True
        
        time.sleep(15)
    
    print("\n⏰ Monitoring timeout - manual check needed")
    return False

if __name__ == "__main__":
    success = monitor()
    if success:
        print("\n🚀 Ready to test full enhanced functionality!")
    else:
        print("\n🔧 May need to check Render deployment logs")