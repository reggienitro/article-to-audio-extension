#!/usr/bin/env python3
import http.server
import ssl
import subprocess
import socket
import os
import shutil

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def create_self_signed_cert():
    """Create a self-signed certificate for HTTPS"""
    cert_file = "server.crt"
    key_file = "server.key"
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("📜 Using existing certificate")
        return cert_file, key_file
    
    print("🔐 Creating self-signed certificate...")
    
    # Create self-signed certificate
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", 
        "-keyout", key_file, "-out", cert_file, "-days", "365", 
        "-nodes", "-subj", "/C=US/ST=CA/L=Local/O=Dev/CN=localhost"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Certificate created successfully")
        return cert_file, key_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create certificate: {e}")
        return None, None
    except FileNotFoundError:
        print("❌ OpenSSL not found. Install with: brew install openssl")
        return None, None

def copy_demo_files():
    """Copy demo files to current directory"""
    icloud_demo = "/Users/aettefagh/Library/Mobile Documents/com~apple~CloudDocs/Mobile-Demos/chrome-mobile-demo.html"
    
    if os.path.exists(icloud_demo):
        shutil.copy2(icloud_demo, "./chrome-mobile-demo.html")
        print("📱 Copied Chrome mobile demo")
    
    # Also copy the regular mobile player if it exists
    if os.path.exists("./mobile-player.html"):
        print("📱 Mobile player already available")

def main():
    port = 8443  # Standard HTTPS port for testing
    local_ip = get_local_ip()
    
    print("🚀 Starting HTTPS mobile server...")
    print(f"📱 Access from iPhone at: https://{local_ip}:{port}")
    print(f"🌐 Files available:")
    print(f"   - https://{local_ip}:{port}/chrome-mobile-demo.html")
    print(f"   - https://{local_ip}:{port}/mobile-player.html")
    print("")
    print("⚠️  Accept the security warning in Chrome (self-signed cert)")
    print("🛑 Press Ctrl+C to stop")
    print("")
    
    # Copy demo files
    copy_demo_files()
    
    # Create certificate
    cert_file, key_file = create_self_signed_cert()
    
    if not cert_file or not key_file:
        print("❌ Cannot create HTTPS server without certificate")
        print("💡 Falling back to HTTP server on port 8888...")
        os.system("python3 -m http.server 8888 --bind 0.0.0.0")
        return
    
    # Create HTTPS server
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add headers for mobile compatibility
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
        
        def do_GET(self):
            print(f"📱 Request: {self.path} from {self.client_address[0]}")
            super().do_GET()
    
    server_address = ('0.0.0.0', port)
    httpd = http.server.HTTPServer(server_address, MyHTTPRequestHandler)
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"✅ HTTPS server running on https://{local_ip}:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        
        # Cleanup certificate files
        for file in [cert_file, key_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️  Removed {file}")

if __name__ == "__main__":
    main()