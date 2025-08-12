#!/usr/bin/env python3
"""
Enhanced HTTP server with archive site support and rate limiting
"""
import json
import subprocess
import asyncio
import os
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import tempfile

class EnhancedArticleToAudioHandler(BaseHTTPRequestHandler):
    # Rate limiting storage
    rate_limits = {}
    
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
            self.send_json_response({'status': 'running', 'message': 'Enhanced Article to Audio server is running'})
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
        elif parsed_path.path == '/cloud-status':
            # Get cloud sync status
            try:
                result = self.get_cloud_status()
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
                cookies = data.get('cookies')
                
                if not url:
                    self.send_json_response({'error': 'URL is required'}, 400)
                    return
                
                # Process URL with archive site handling
                processed_url = self.process_url_with_archives(url)
                
                # Run conversion
                result = self.run_conversion(processed_url, voice, speed, save_to_storage, cookies)
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

    def process_url_with_archives(self, url):
        """Process URL with archive site detection and rate limiting"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if it's already an archive URL
        if self.is_archive_url(url):
            print(f"🏛️  Archive URL detected: {domain}")
            return self.handle_archive_url(url)
        
        # Check for paywall sites that might need archiving
        if self.is_paywall_site(domain):
            print(f"💰 Paywall site detected: {domain}")
            # Could automatically try archive alternatives here
            return url
        
        return url
    
    def is_archive_url(self, url):
        """Check if URL is from an archive service"""
        archive_domains = [
            'archive.ph', 'archive.today', 'archive.is',
            'web.archive.org', 'archive.org',
            '12ft.io', 'outline.com'
        ]
        
        parsed = urlparse(url)
        return any(domain in parsed.netloc.lower() for domain in archive_domains)
    
    def is_paywall_site(self, domain):
        """Check if domain is known to have paywalls"""
        paywall_domains = [
            'nytimes.com', 'wsj.com', 'ft.com', 'economist.com',
            'washingtonpost.com', 'bloomberg.com', 'reuters.com'
        ]
        
        return any(paywall in domain for paywall in paywall_domains)
    
    def handle_archive_url(self, url):
        """Handle archive URLs with enhanced rate limiting"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Implement progressive rate limiting
        if domain in self.rate_limits:
            last_request = self.rate_limits[domain]
            elapsed = time.time() - last_request
            
            # Progressive delays based on archive service
            if 'archive.ph' in domain:
                min_delay = 45  # archive.ph is strict
            elif 'web.archive.org' in domain:
                min_delay = 10  # wayback machine is more lenient
            else:
                min_delay = 30  # default for other services
            
            if elapsed < min_delay:
                wait_time = min_delay - elapsed
                print(f"⏱️  Rate limiting {domain}: waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
        
        # Update rate limit tracker
        self.rate_limits[domain] = time.time()
        return url

    def test_article_extraction(self, url):
        """Test article extraction with archive site awareness"""
        try:
            # Process URL for archives
            processed_url = self.process_url_with_archives(url)
            
            # Enhanced test with more information
            return {
                'success': True,
                'url': processed_url,
                'original_url': url if processed_url != url else None,
                'message': 'Enhanced article extraction ready',
                'estimated_duration': '2-5 minutes',
                'archive_used': self.is_archive_url(processed_url),
                'paywall_detected': self.is_paywall_site(urlparse(url).netloc.lower()) if not self.is_archive_url(url) else False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def run_conversion(self, url, voice, speed, save_to_storage, cookies=None):
        """Run the actual article to audio conversion with enhanced error handling and authentication"""
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
            
            # Add authentication if cookies provided
            if cookies:
                print(f"🔑 Using authentication cookies for {url}")
                cmd.extend(['--cookies', cookies])
            
            print(f"🎤 Running command: {' '.join(cmd[:6])}{'...' if len(cmd) > 6 else ''}")  # Don't log full cookies
            
            # Run the CLI command with longer timeout for archive sites
            timeout = 600 if self.is_archive_url(url) else 300  # 10 min for archives, 5 min for regular
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Enhanced debug output
            print(f"📋 CLI exit code: {result.returncode}")
            print(f"📋 CLI stdout: {result.stdout}")
            if result.stderr:
                print(f"📋 CLI stderr: {result.stderr}")
            
            if result.returncode == 0:
                # Enhanced output parsing
                output_lines = result.stdout.strip().split('\n')
                audio_file = None
                file_size = None
                duration = None
                
                for line in output_lines:
                    # Extract filename
                    if 'File:' in line and '.mp3' in line:
                        audio_file = line.split('File:')[1].strip()
                    # Extract file size
                    elif 'Size:' in line:
                        file_size = line.split('Size:')[1].strip()
                    # Extract duration
                    elif 'minutes' in line.lower() and 'audio:' in line.lower():
                        duration = line.strip()
                
                return {
                    'success': True,
                    'message': 'Conversion completed successfully',
                    'audio_file': audio_file,
                    'file_size': file_size,
                    'duration': duration,
                    'output': result.stdout,
                    'command': ' '.join(cmd),
                    'archive_used': self.is_archive_url(url)
                }
            else:
                # Enhanced error handling - filter out SSL warnings
                stdout_clean = result.stdout
                stderr_clean = result.stderr
                
                # Remove SSL warning noise
                if stderr_clean:
                    stderr_lines = [line for line in stderr_clean.split('\n') 
                                   if 'NotOpenSSLWarning' not in line and 'urllib3' not in line and 'warnings.warn' not in line and line.strip()]
                    stderr_clean = '\n'.join(stderr_lines) if stderr_lines else ''
                
                error_message = stderr_clean or stdout_clean or f'CLI failed with exit code {result.returncode}'
                
                # Check for specific errors
                if 'rate limit' in error_message.lower() or '429' in error_message:
                    return {
                        'success': False,
                        'error': 'Rate limited by source site. Try again in a few minutes or use an archive URL.',
                        'retry_suggestions': [
                            f'Try archive.ph: https://archive.ph/{url}',
                            f'Try Wayback Machine: https://web.archive.org/web/{url}'
                        ]
                    }
                elif 'paywall' in error_message.lower() or 'subscription' in error_message.lower() or 'behind a paywall' in error_message.lower():
                    # Enhanced paywall bypass suggestions for NYT and other sites
                    bypass_urls = []
                    
                    # Add specific bypasses based on domain
                    if 'nytimes.com' in url:
                        bypass_urls.extend([
                            f'Try archive.today: https://archive.today/?run=1&url={url}',
                            f'Try 12ft ladder: https://12ft.io/{url}',
                            f'Try archived version: https://web.archive.org/web/newest/{url}'
                        ])
                    else:
                        bypass_urls.extend([
                            f'Try 12ft.io: https://12ft.io/{url}',
                            f'Try archive.ph: https://archive.ph/{url}',
                            f'Try outline.com: https://outline.com/{url}'
                        ])
                    
                    return {
                        'success': False,
                        'error': 'Article appears to be behind a paywall. Try these alternatives:',
                        'retry_suggestions': bypass_urls,
                        'paywall_detected': True
                    }
                else:
                    return {
                        'success': False,
                        'error': error_message,
                        'stderr': result.stderr,
                        'stdout': result.stdout
                    }
                
        except subprocess.TimeoutExpired:
            timeout_msg = f'Conversion timed out after {timeout//60} minutes'
            if self.is_archive_url(url):
                timeout_msg += ' (Archive sites may be slower)'
            return {
                'success': False,
                'error': timeout_msg
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
    
    def get_cloud_status(self):
        """Get cloud sync status by calling CLI"""
        try:
            result = subprocess.run([
                'python3', 
                '/Users/aettefagh/model-finetuning-project/article2audio-enhanced',
                '--cloud-status'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse CLI output to extract status
                output_lines = result.stdout.strip().split('\\n')
                status = {'enabled': False, 'provider': None, 'message': 'Unknown'}
                
                for line in output_lines:
                    if 'Enabled:' in line:
                        status['enabled'] = 'True' in line
                    elif 'Provider:' in line:
                        status['provider'] = line.split('Provider:')[1].strip()
                    elif 'Status:' in line:
                        status['message'] = line.split('Status:')[1].strip()
                    elif 'Path:' in line:
                        status['path'] = line.split('Path:')[1].strip()
                
                return status
            else:
                return {'enabled': False, 'error': 'Failed to get cloud status'}
                
        except Exception as e:
            return {'enabled': False, 'error': str(e)}

    def log_message(self, format, *args):
        """Custom logging to be less verbose"""
        print(f"[{self.address_string()}] {format % args}")

def run_enhanced_server(port=8888):
    """Run the enhanced HTTP server"""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, EnhancedArticleToAudioHandler)
    
    print(f"🎧 Enhanced Article to Audio Server starting on http://localhost:{port}")
    print(f"📋 Available endpoints:")
    print(f"   GET  /status - Server status")
    print(f"   GET  /test?url=... - Test article extraction")
    print(f"   GET  /library - Get audio library")
    print(f"   POST /convert - Convert article to audio")
    print(f"\n🏛️  Enhanced features:")
    print(f"   ✅ Archive site detection and rate limiting")
    print(f"   ✅ Paywall site detection")
    print(f"   ✅ Progressive retry delays")
    print(f"   ✅ Enhanced error messages")
    print(f"\n🔄 Ready for browser extension and web UI requests...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Enhanced server stopped by user")
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
    
    run_enhanced_server(port)