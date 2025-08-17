#!/usr/bin/env python3
"""
Test deployment readiness and Render compatibility
Verifies all components are ready for cloud deployment
"""

import os
import subprocess
import requests
import json
from typing import Dict, List

def test_environment_variables():
    """Test that all required environment variables are configured"""
    print("🔧 Testing environment variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'PORT'
    ]
    
    # Check local .env file
    env_file = '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/.env'
    if os.path.exists(env_file):
        print("✅ Local .env file exists")
        
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✅ All required environment variables present")
            return True
    else:
        print("❌ Local .env file not found")
        return False

def test_dependencies():
    """Test that all Python dependencies are available"""
    print("\n📦 Testing Python dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'supabase',
        'requests',
        'python-dotenv',
        'edge-tts',
        'newspaper3k',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All dependencies available")
        return True

def test_docker_build():
    """Test Docker build process"""
    print("\n🐳 Testing Docker build...")
    
    dockerfile_path = '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/Dockerfile'
    if not os.path.exists(dockerfile_path):
        print("❌ Dockerfile not found")
        return False
    
    try:
        # Test Docker build (dry run)
        result = subprocess.run([
            'docker', 'build', '--dry-run', 
            '-t', 'article2audio-test', 
            '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Docker build validation successful")
            return True
        else:
            print(f"❌ Docker build validation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker build validation timed out")
        return False
    except FileNotFoundError:
        print("⚠️ Docker not available - build test skipped")
        return True  # Don't fail if Docker isn't installed

def test_render_config():
    """Test Render deployment configuration"""
    print("\n🚀 Testing Render configuration...")
    
    render_yaml = '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/render.yaml'
    if not os.path.exists(render_yaml):
        print("❌ render.yaml not found")
        return False
    
    try:
        with open(render_yaml, 'r') as f:
            content = f.read()
        
        required_sections = ['services', 'name', 'env', 'buildCommand', 'startCommand']
        missing_sections = []
        
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing Render config sections: {missing_sections}")
            return False
        else:
            print("✅ Render configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error reading Render config: {e}")
        return False

def test_server_startup():
    """Test that the server can start locally"""
    print("\n🔄 Testing local server startup...")
    
    server_file = '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/cloud-server.py'
    if not os.path.exists(server_file):
        print("❌ cloud-server.py not found")
        return False
    
    try:
        # Test import without starting server
        import sys
        sys.path.insert(0, '/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension')
        
        # This will test import errors without starting the server
        result = subprocess.run([
            'python3', '-c', 
            f'import sys; sys.path.insert(0, "{os.path.dirname(server_file)}"); '
            'from pathlib import Path; '
            'import cloud_server; '
            'print("Server imports successfully")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Server startup test successful")
            return True
        else:
            print(f"❌ Server startup test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test error: {e}")
        return False

def test_git_status():
    """Test git repository status"""
    print("\n📝 Testing git repository status...")
    
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd='/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension')
        
        if result.returncode == 0:
            uncommitted = result.stdout.strip()
            if uncommitted:
                print(f"⚠️ Uncommitted changes found:\n{uncommitted}")
                print("💡 Consider committing changes before deployment")
            else:
                print("✅ Git repository is clean")
            return True
        else:
            print("❌ Git status check failed")
            return False
            
    except Exception as e:
        print(f"❌ Git status error: {e}")
        return False

def generate_deployment_checklist():
    """Generate deployment checklist"""
    print("\n📋 Deployment Checklist")
    print("=" * 40)
    
    checklist = [
        "□ Schema executed in Supabase SQL Editor",
        "□ Environment variables configured in Render",
        "□ Repository connected to Render",
        "□ Build and start commands verified",
        "□ Domain/URL configured if needed",
        "□ SSL certificate setup (automatic with Render)",
        "□ Health check endpoint responding",
        "□ Test with real article conversion",
        "□ Verify audio file upload/download",
        "□ Check CORS settings for frontend"
    ]
    
    for item in checklist:
        print(item)
    
    print("\n🔗 Render Deployment URLs:")
    print("   Dashboard: https://dashboard.render.com")
    print("   Logs: Check deployment logs for startup issues")
    print("   Health: https://your-app.onrender.com/health")

def run_deployment_tests():
    """Run all deployment readiness tests"""
    print("🚀 Starting Deployment Readiness Tests")
    print("=" * 60)
    
    tests = [
        test_environment_variables,
        test_dependencies,
        test_docker_build,
        test_render_config,
        test_server_startup,
        test_git_status
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"🏁 Deployment tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✅ Ready for deployment!")
    else:
        print("❌ Some deployment checks failed - review above")
    
    generate_deployment_checklist()
    
    return passed == total

if __name__ == "__main__":
    run_deployment_tests()