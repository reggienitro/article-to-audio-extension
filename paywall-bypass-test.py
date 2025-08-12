#!/usr/bin/env python3
"""
Test script to check which paywall bypass services work
"""
import requests
import time
from urllib.parse import urlparse

def test_bypass_services(original_url):
    """Test different paywall bypass services"""
    
    bypass_services = [
        {
            'name': '12ft.io',
            'url_template': 'https://12ft.io/{url}',
            'working': None
        },
        {
            'name': 'archive.today',
            'url_template': 'https://archive.today/?run=1&url={url}',
            'working': None
        },
        {
            'name': 'archive.ph',
            'url_template': 'https://archive.ph/{url}',
            'working': None
        },
        {
            'name': 'web.archive.org',
            'url_template': 'https://web.archive.org/web/newest/{url}',
            'working': None
        },
        {
            'name': 'outline.com',
            'url_template': 'https://outline.com/{url}',
            'working': None
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    results = []
    
    for service in bypass_services:
        try:
            bypass_url = service['url_template'].format(url=original_url)
            print(f"Testing {service['name']}: {bypass_url}")
            
            response = requests.get(bypass_url, headers=headers, timeout=15)
            
            # Check response
            if response.status_code == 200:
                content_length = len(response.text)
                has_article_content = any(word in response.text.lower() for word in ['trump', 'putin', 'alaska', 'article'])
                
                service['working'] = True
                service['status_code'] = 200
                service['content_length'] = content_length
                service['has_relevant_content'] = has_article_content
                service['bypass_url'] = bypass_url
                
                print(f"  ✅ {service['name']}: Status {response.status_code}, {content_length} chars, Relevant content: {has_article_content}")
                
            else:
                service['working'] = False
                service['status_code'] = response.status_code
                print(f"  ❌ {service['name']}: Status {response.status_code}")
                
        except Exception as e:
            service['working'] = False
            service['error'] = str(e)
            print(f"  ❌ {service['name']}: Error - {e}")
        
        time.sleep(2)  # Be respectful
        results.append(service)
    
    return results

def find_best_bypass_service(results):
    """Find the best working bypass service"""
    working_services = [s for s in results if s.get('working')]
    
    if not working_services:
        return None
    
    # Prioritize by content quality
    best = max(working_services, key=lambda x: (
        x.get('has_relevant_content', False),
        x.get('content_length', 0)
    ))
    
    return best

if __name__ == '__main__':
    test_url = "https://www.nytimes.com/2025/08/10/us/politics/trump-putin-alaska-reaction.html"
    
    print(f"Testing paywall bypass services for: {test_url}")
    print("=" * 80)
    
    results = test_bypass_services(test_url)
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    
    working = [s for s in results if s.get('working')]
    if working:
        print(f"✅ Working services: {len(working)}")
        for service in working:
            print(f"   - {service['name']}: {service.get('content_length', 0)} chars, Relevant: {service.get('has_relevant_content', False)}")
        
        best = find_best_bypass_service(results)
        if best:
            print(f"\n🏆 Best option: {best['name']}")
            print(f"   URL: {best.get('bypass_url')}")
    else:
        print("❌ No working bypass services found")
    
    failed = [s for s in results if not s.get('working')]
    if failed:
        print(f"\n❌ Failed services: {len(failed)}")
        for service in failed:
            if 'error' in service:
                print(f"   - {service['name']}: {service['error']}")
            else:
                print(f"   - {service['name']}: Status {service.get('status_code')}")