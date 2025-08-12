#!/usr/bin/env python3
"""
Local HTTP server to bridge browser extension and article2audio CLI
"""
import json
import subprocess
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import tempfile

class ArticleToAudioHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/status':
            self.send_json_response({'status': 'running', 'message': 'Article to Audio server is running'})
        elif parsed_path.path == '/test':
            # Test article extraction without conversion
            query_params = parse_qs(parsed_path.query)
            url = query_params.get('url', [''])[0]
            
            if not url:
                self.send_json_response({'error': 'URL parameter required'}, 400)
                return
            
            try:
                result = self.test_article_extraction(url)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
        elif parsed_path.path == '/library':
            # Get audio library files
            try:
                result = self.get_audio_library()
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/convert':
            try:
                # Parse request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                url = data.get('url')
                voice = data.get('voice', 'christopher')
                speed = data.get('speed', 'fast')
                save_to_storage = data.get('save_to_storage', False)
                
                if not url:
                    self.send_json_response({'error': 'URL is required'}, 400)
                    return
                
                # Run conversion
                result = self.run_conversion(url, voice, speed, save_to_storage)
                self.send_json_response(result)
                
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def test_article_extraction(self, url):
        """Test article extraction without conversion"""
        try:
            # Run CLI with --dry-run flag (we'll need to add this to the CLI)
            # For now, we'll simulate the test
            cmd = [
                'python3', 
                '/Users/aettefagh/model-finetuning-project/article2audio-enhanced',
                url,
                '--voice', 'christopher',
                '--speed', 'fast'
            ]
            
            # We could add a --test-only flag to the CLI to just extract and analyze
            # For now, let's return basic info
            return {
                'success': True,
                'url': url,
                'message': 'Article extraction test - CLI integration needed',
                'estimated_duration': '2-5 minutes',
                'word_count': 'Unknown (requires CLI integration)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def run_conversion(self, url, voice, speed, save_to_storage):
        """Run the actual article to audio conversion"""
        try:
            # Build CLI command
            cmd = [
                'python3', 
                '/Users/aettefagh/model-finetuning-project/article2audio-enhanced',
                url,
                '--voice', voice,
                '--speed', speed
            ]
            
            if save_to_storage:
                cmd.append('--save')
            
            print(f"🎤 Running command: {' '.join(cmd)}")
            
            # Run the CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Debug output
            print(f"📋 CLI exit code: {result.returncode}")
            print(f"📋 CLI stdout: {result.stdout}")
            if result.stderr:
                print(f"📋 CLI stderr: {result.stderr}")
            
            if result.returncode == 0:
                # Parse output to get filename
                output_lines = result.stdout.strip().split('\n')
                audio_file = None
                
                for line in output_lines:
                    if 'saved to' in line.lower() or '.mp3' in line:
                        # Extract filename from output
                        if '.mp3' in line:
                            audio_file = line.strip()
                        break
                
                return {
                    'success': True,
                    'message': 'Conversion completed successfully',
                    'audio_file': audio_file,
                    'output': result.stdout,
                    'command': ' '.join(cmd)
                }
            else:
                return {
                    'success': False,
                    'error': f'CLI failed with exit code {result.returncode}',
                    'stderr': result.stderr,
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Conversion timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_audio_library(self):
        """Get list of audio files in the library"""
        try:
            audio_dir = '/Users/aettefagh/model-finetuning-project/data/audio'
            
            if not os.path.exists(audio_dir):
                return {'files': [], 'count': 0}
            
            audio_files = []
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3'):
                    filepath = os.path.join(audio_dir, filename)
                    stat = os.stat(filepath)
                    
                    audio_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': stat.st_ctime,
                        'modified': stat.st_mtime
                    })
            
            # Sort by creation time (newest first)
            audio_files.sort(key=lambda x: x['created'], reverse=True)
            
            return {
                'files': audio_files,
                'count': len(audio_files),
                'total_size': sum(f['size'] for f in audio_files)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'files': [],
                'count': 0
            }

    def log_message(self, format, *args):
        """Custom logging to be less verbose"""
        print(f"[{self.address_string()}] {format % args}")

def run_server(port=8888):
    """Run the HTTP server"""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, ArticleToAudioHandler)
    
    print(f"🎧 Article to Audio Server starting on http://localhost:{port}")
    print(f"📋 Available endpoints:")
    print(f"   GET  /status - Server status")
    print(f"   GET  /test?url=... - Test article extraction")
    print(f"   POST /convert - Convert article to audio")
    print(f"\n🔄 Ready for browser extension requests...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == '__main__':
    import sys
    
    port = 8888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    run_server(port)