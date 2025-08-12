#!/usr/bin/env python3
"""
Simplified debug server to isolate connection issues
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class DebugHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        print("✅ CORS preflight handled")

    def do_GET(self):
        """Handle GET requests"""
        print(f"📥 GET request: {self.path}")
        
        if self.path == '/status':
            self.send_json_response({'status': 'debug_server_running', 'message': 'Debug server is working!'})
            print("✅ Status request handled")
        elif self.path.startswith('/test'):
            # Handle test endpoint with URL parameter
            self.send_json_response({
                'success': True,
                'message': 'Debug test endpoint working!',
                'estimated_duration': '2-3 minutes (simulated)'
            })
            print("✅ Test request handled")
        else:
            self.send_json_response({'error': 'Not found'}, 404)
            print("❌ Unknown endpoint")

    def do_POST(self):
        """Handle POST requests"""
        print(f"📥 POST request: {self.path}")
        
        if self.path == '/convert':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"📋 Received data: {data}")
                
                self.send_json_response({
                    'success': True,
                    'message': 'Debug conversion - server is working!',
                    'received_data': data,
                    'audio_file': 'debug_test.mp3'
                })
                print("✅ Debug conversion handled")
                
            except Exception as e:
                print(f"❌ Error handling POST: {e}")
                self.send_json_response({'error': str(e)}, 500)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def send_json_response(self, data, status=200):
        """Send JSON with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom logging"""
        print(f"🌐 [{self.address_string()}] {format % args}")

def run_debug_server():
    PORT = 8888
    print(f"🐛 DEBUG SERVER starting on http://localhost:{PORT}")
    print("This simplified server will help isolate connection issues")
    print("=" * 60)
    
    try:
        with HTTPServer(('localhost', PORT), DebugHandler) as httpd:
            print(f"✅ Server bound to port {PORT}")
            print(f"🔄 Waiting for requests... (Ctrl+C to stop)")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print("Try: lsof -i :8888 to see what's using it")
        else:
            print(f"❌ Server error: {e}")
    except KeyboardInterrupt:
        print(f"\n🛑 Debug server stopped")

if __name__ == '__main__':
    run_debug_server()