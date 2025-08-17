#!/usr/bin/env python3
"""
Test local FastAPI server startup and basic functionality
"""

import subprocess
import time
import requests
import signal
import os
import sys
from typing import Optional

class LocalServerTester:
    def __init__(self, server_file: str = "cloud-server.py", port: int = 5000):
        self.server_file = server_file
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.server_process: Optional[subprocess.Popen] = None
    
    def start_server(self):
        """Start the FastAPI server in background"""
        print(f"🚀 Starting server: {self.server_file}")
        
        # Change to project directory
        os.chdir('/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension')
        
        try:
            self.server_process = subprocess.Popen([
                'python3', self.server_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"📋 Server PID: {self.server_process.pid}")
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for attempt in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully on port {self.port}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            
            print("❌ Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server process"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Server stopped")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        print("\n🌐 Testing CORS headers...")
        try:
            response = requests.options(f"{self.base_url}/health", timeout=5)
            headers = response.headers
            
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            missing_headers = []
            for header in cors_headers:
                if header not in headers:
                    missing_headers.append(header)
            
            if missing_headers:
                print(f"⚠️ Missing CORS headers: {missing_headers}")
                return False
            else:
                print("✅ CORS headers properly configured")
                return True
                
        except Exception as e:
            print(f"❌ CORS test error: {e}")
            return False
    
    def test_signup_endpoint(self):
        """Test user signup endpoint"""
        print("\n👤 Testing signup endpoint...")
        try:
            data = {
                "email": "localtest@example.com",
                "display_name": "Local Test User"
            }
            response = requests.post(f"{self.base_url}/signup", json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Signup successful: {result.get('message', 'No message')}")
                return True
            else:
                print(f"❌ Signup failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Signup test error: {e}")
            return False
    
    def test_conversion_endpoint(self):
        """Test article conversion endpoint"""
        print("\n🎵 Testing conversion endpoint...")
        try:
            data = {
                "title": "Local Test Article",
                "content": "This is a local test article for server testing. It contains enough text to generate meaningful audio.",
                "url": "https://localhost/test",
                "voice": "en-US-BrianNeural",
                "user_email": "localtest@example.com"
            }
            
            response = requests.post(f"{self.base_url}/convert", json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Conversion successful: {result.get('message', 'No message')}")
                if 'audio_url' in result:
                    print(f"   Audio URL: {result['audio_url']}")
                return True
            else:
                print(f"❌ Conversion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Conversion test error: {e}")
            return False
    
    def test_library_endpoint(self):
        """Test library access endpoint"""
        print("\n📚 Testing library endpoint...")
        try:
            response = requests.get(f"{self.base_url}/library/localtest@example.com", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                articles = result.get('articles', [])
                print(f"✅ Library access successful: {len(articles)} articles found")
                return True
            else:
                print(f"❌ Library access failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Library test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all server tests"""
        print("🧪 Starting Local Server Tests")
        print("=" * 50)
        
        # Start server
        if not self.start_server():
            print("❌ Cannot proceed - server failed to start")
            return False
        
        try:
            # Run tests
            tests = [
                self.test_health_endpoint,
                self.test_cors_headers,
                self.test_signup_endpoint,
                self.test_conversion_endpoint,
                self.test_library_endpoint
            ]
            
            results = []
            for test in tests:
                try:
                    result = test()
                    results.append(result)
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {e}")
                    results.append(False)
            
            # Summary
            passed = sum(results)
            total = len(results)
            
            print(f"\n{'='*50}")
            print(f"🏁 Local server tests completed: {passed}/{total} passed")
            
            if passed == total:
                print("✅ Local server is working correctly!")
                print("🚀 Ready for production deployment!")
            else:
                print("❌ Some tests failed - check server configuration")
            
            return passed == total
            
        finally:
            # Always stop server
            self.stop_server()

def main():
    """Main test runner"""
    tester = LocalServerTester()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Interrupted by user")
        tester.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())