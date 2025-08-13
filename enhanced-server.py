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
import pathlib

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
        
        # Serve mobile player
        if parsed_path.path == '/mobile' or parsed_path.path == '/mobile-player':
            self.serve_mobile_player()
            return
            
        # Serve iPhone manager
        if parsed_path.path == '/iphone-manager' or parsed_path.path == '/iphone':
            self.serve_iphone_manager()
            return
            
        # API endpoint for audio library
        if parsed_path.path == '/api/library':
            self.serve_audio_library()
            return
            
        # Serve audio files
        if parsed_path.path.startswith('/audio/'):
            self.serve_audio_file(parsed_path.path)
            return
        
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
                
            except json.JSONDecodeError:
                self.send_json_response({
                    'error': 'Invalid JSON in request body',
                    'error_type': 'invalid_json',
                    'user_message': 'The request format is invalid. Please try again.',
                    'suggestions': ['Check if the URL is correctly formatted', 'Try refreshing the page']
                }, 400)
            except KeyError as e:
                self.send_json_response({
                    'error': f'Missing required field: {e}',
                    'error_type': 'missing_field',
                    'user_message': 'Required information is missing from the request.',
                    'suggestions': ['Make sure you\'re on a valid article page', 'Try refreshing the page']
                }, 400)
            except Exception as e:
                error_msg = str(e)
                error_type, user_message, suggestions = self.categorize_error(error_msg)
                
                self.send_json_response({
                    'error': error_msg,
                    'error_type': error_type,
                    'user_message': user_message,
                    'suggestions': suggestions,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }, 500)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def categorize_error(self, error_msg):
        """Categorize errors and provide user-friendly messages"""
        error_msg_lower = error_msg.lower()
        
        # Network/connection errors
        if any(term in error_msg_lower for term in ['connection', 'timeout', 'network', 'dns']):
            return ('network_error', 
                   'Unable to connect to the website. Please check your internet connection.',
                   ['Check your internet connection', 'Try again in a few moments', 'The website might be temporarily down'])
        
        # Paywall errors
        elif any(term in error_msg_lower for term in ['paywall', 'subscription', 'premium', 'login']):
            return ('paywall_error',
                   'This article requires a subscription or login to access.',
                   ['Try using an archive link (archive.today, web.archive.org)', 'Check if you have a subscription', 'Look for a free version of the article'])
        
        # Content errors
        elif any(term in error_msg_lower for term in ['too short', 'no content', 'content found']):
            return ('content_error',
                   'Unable to extract readable content from this page.',
                   ['Make sure this is an article page, not a homepage', 'Try a different article', 'The page might be loading content dynamically'])
        
        # Rate limiting
        elif any(term in error_msg_lower for term in ['rate limit', 'too many requests', '429']):
            return ('rate_limit_error',
                   'Too many requests. Please wait a moment before trying again.',
                   ['Wait 30 seconds and try again', 'The website is limiting requests'])
        
        # Access denied/blocked
        elif any(term in error_msg_lower for term in ['access denied', 'forbidden', '403', 'blocked']):
            return ('access_error',
                   'Access to this website is currently blocked or restricted.',
                   ['The website might be blocking automated requests', 'Try a different article', 'Check if the URL is correct'])
        
        # Article not found
        elif any(term in error_msg_lower for term in ['not found', '404', 'does not exist']):
            return ('not_found_error',
                   'The article could not be found. The link might be broken.',
                   ['Check if the URL is correct', 'The article might have been moved or deleted', 'Try searching for the article on the website'])
        
        # Voice/TTS errors
        elif any(term in error_msg_lower for term in ['voice', 'tts', 'audio', 'edge-tts']):
            return ('audio_error',
                   'There was a problem generating the audio.',
                   ['Try a different voice', 'Check your internet connection', 'The text-to-speech service might be temporarily unavailable'])
        
        # Unknown error
        else:
            return ('unknown_error',
                   'An unexpected error occurred. Please try again.',
                   ['Try refreshing the page', 'Check if the URL is a valid article', 'The issue might be temporary'])

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
    
    def serve_mobile_player(self):
        """Serve the mobile audio player interface"""
        try:
            mobile_player_path = os.path.join(os.path.dirname(__file__), 'mobile-player.html')
            
            if os.path.exists(mobile_player_path):
                with open(mobile_player_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_json_response({'error': 'Mobile player not found'}, 404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def serve_iphone_manager(self):
        """Serve the iPhone manager interface"""
        try:
            iphone_manager_path = os.path.join(os.path.dirname(__file__), 'iphone-manager.html')
            
            if os.path.exists(iphone_manager_path):
                with open(iphone_manager_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_json_response({'error': 'iPhone manager not found'}, 404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def serve_audio_library(self):
        """Serve the audio library as JSON for the mobile player"""
        try:
            library = self.get_enhanced_audio_library()
            self.send_json_response(library)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def serve_audio_file(self, path):
        """Serve audio files from the library"""
        try:
            # Extract filename from path (/audio/filename.mp3)
            filename = path.replace('/audio/', '')
            
            # Look for file in both local and iCloud locations
            local_audio_dir = pathlib.Path.home() / "model-finetuning-project" / "data" / "audio"
            icloud_audio_dir = pathlib.Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "ArticleAudio"
            
            audio_file = None
            for audio_dir in [local_audio_dir, icloud_audio_dir]:
                potential_file = audio_dir / filename
                if potential_file.exists():
                    audio_file = potential_file
                    break
            
            if not audio_file:
                self.send_json_response({'error': 'Audio file not found'}, 404)
                return
            
            # Serve the audio file
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(audio_file.stat().st_size))
            self.end_headers()
            
            with open(audio_file, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def get_enhanced_audio_library(self):
        """Get enhanced audio library with metadata for mobile player"""
        try:
            import glob
            import datetime
            
            # Check both local and iCloud directories
            local_audio_dir = pathlib.Path.home() / "model-finetuning-project" / "data" / "audio"
            icloud_audio_dir = pathlib.Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "ArticleAudio"
            
            articles = []
            
            for audio_dir in [local_audio_dir, icloud_audio_dir]:
                if not audio_dir.exists():
                    continue
                    
                audio_files = list(audio_dir.glob("*.mp3"))
                
                for audio_file in audio_files:
                    try:
                        # Parse filename for metadata
                        filename = audio_file.name
                        
                        # Extract timestamp and title from filename pattern
                        # Format: YYYYMMDD_HHMMSS_Title_voice.mp3
                        parts = filename.replace('.mp3', '').split('_')
                        if len(parts) >= 3:
                            date_str = parts[0]
                            time_str = parts[1]
                            title_parts = parts[2:-1]  # Everything except date, time, and voice
                            voice = parts[-1]
                            
                            # Format title
                            title = ' '.join(title_parts).replace('_', ' ')
                            
                            # Parse date
                            try:
                                date_obj = datetime.datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                                formatted_date = date_obj.strftime("%Y-%m-%d")
                                formatted_time = date_obj.strftime("%H:%M")
                            except:
                                formatted_date = date_str
                                formatted_time = time_str
                        else:
                            title = filename.replace('.mp3', '').replace('_', ' ')
                            formatted_date = "Unknown"
                            formatted_time = "Unknown"
                            voice = "christopher"
                        
                        # Get file size and duration estimate
                        file_size = audio_file.stat().st_size
                        size_mb = round(file_size / (1024 * 1024), 1)
                        
                        # Estimate duration (rough: 1MB ≈ 1 minute for speech)
                        estimated_duration_min = max(1, round(size_mb))
                        duration_str = f"{estimated_duration_min}:00" if estimated_duration_min < 60 else f"{estimated_duration_min//60}:{estimated_duration_min%60:02d}:00"
                        
                        # Determine source based on title patterns
                        source = "Unknown"
                        if "nytimes" in filename.lower() or "new york times" in title.lower():
                            source = "The New York Times"
                        elif "npr" in filename.lower():
                            source = "NPR"
                        elif "washington" in title.lower() and "post" in title.lower():
                            source = "Washington Post"
                        elif "bbc" in filename.lower():
                            source = "BBC"
                        
                        article = {
                            'id': filename.replace('.mp3', ''),
                            'title': title[:80] + ('...' if len(title) > 80 else ''),
                            'source': source,
                            'duration': duration_str,
                            'file': f"/audio/{filename}",
                            'date': formatted_date,
                            'time': formatted_time,
                            'voice': voice.title(),
                            'size': f"{size_mb} MB",
                            'location': 'iCloud' if 'CloudDocs' in str(audio_dir) else 'Local'
                        }
                        
                        articles.append(article)
                        
                    except Exception as e:
                        print(f"Error processing {audio_file}: {e}")
                        continue
            
            # Sort by date/time (newest first) and remove duplicates
            unique_articles = {}
            for article in articles:
                # Use title as key to deduplicate
                key = article['title']
                if key not in unique_articles or article['location'] == 'iCloud':
                    unique_articles[key] = article
            
            sorted_articles = sorted(unique_articles.values(), 
                                   key=lambda x: f"{x['date']}_{x['time']}", 
                                   reverse=True)
            
            return {
                'success': True,
                'articles': sorted_articles,
                'total': len(sorted_articles),
                'message': f'Found {len(sorted_articles)} articles'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'articles': []
            }

def run_enhanced_server(port=8888):
    """Run the enhanced HTTP server"""
    server_address = ('0.0.0.0', port)  # Bind to all interfaces for iPhone access
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