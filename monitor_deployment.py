#!/usr/bin/env python3
"""
Monitor Render deployment progress
"""

import requests
import time
import json

BASE_URL = "https://article-to-audio-extension-1.onrender.com"

def check_deployment():
    """Check if enhanced server is deployed"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            version = data.get('info', {}).get('version', 'Unknown')
            title = data.get('info', {}).get('title', 'Unknown')
            
            print(f"📊 Current: {title} v{version}")
            
            if 'Personal Data Lake' in title and version.startswith('2.'):
                return True
        return False
    except:
        return False

def monitor_deployment():
    """Monitor deployment until it updates"""
    print("🚀 Monitoring Render deployment...")
    print("Looking for: 'Personal Data Lake' v2.x")
    print("-" * 50)
    
    for i in range(30):  # Monitor for 15 minutes max
        if check_deployment():
            print("\n✅ Enhanced server deployed successfully!")
            
            # Test health immediately
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                if response.status_code == 200:
                    health = response.json()
                    print(f"🔍 Health: {json.dumps(health, indent=2)}")
                    
                    if health.get('supabase_connected'):
                        print("🎉 Personal data lake is LIVE!")
                    else:
                        print("⚠️ Server deployed but Supabase connection issue")
            except Exception as e:
                print(f"❌ Health check failed: {e}")
            
            return True
        
        print(f"⏳ Waiting... ({(i+1)*30}s)")
        time.sleep(30)
    
    print("\n❌ Deployment didn't complete in 15 minutes")
    print("💡 Try manual redeploy in Render dashboard")
    return False

if __name__ == "__main__":
    monitor_deployment()