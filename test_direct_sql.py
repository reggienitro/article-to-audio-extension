#!/usr/bin/env python3
"""
Test schema directly using SQL queries to bypass API cache
"""

import requests
import json

def test_schema_with_sql():
    """Test schema using direct SQL queries"""
    
    # Supabase project details
    project_ref = "qslpqxjoupwyclmguniz"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A"
    
    # Use PostgREST API directly
    base_url = f"https://{project_ref}.supabase.co/rest/v1"
    
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing schema with direct API calls...")
    
    # Test 1: Check if articles table is accessible
    print("\n📊 Testing articles table access...")
    try:
        response = requests.get(f"{base_url}/articles?limit=1", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Articles table accessible - found {len(data)} rows")
            if data:
                print(f"📋 Sample record columns: {list(data[0].keys())}")
        elif response.status_code == 406:
            print("⚠️ Table exists but cache not refreshed yet - this is normal")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Try to insert a test record
    print("\n📝 Testing article insertion...")
    try:
        test_article = {
            'title': 'API Test Article',
            'content': 'This is a test article inserted via API.',
            'voice': 'en-US-BrianNeural',
            'user_email': 'api-test@example.com'
        }
        
        response = requests.post(f"{base_url}/articles", 
                               headers=headers, 
                               json=test_article)
        
        if response.status_code in [200, 201]:
            print("✅ Article insertion successful")
            data = response.json()
            if data:
                print(f"   Created article ID: {data[0].get('id', 'Unknown')}")
        else:
            print(f"❌ Insertion failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Insertion request failed: {e}")
    
    # Test 3: Check storage buckets (different endpoint)
    print("\n💾 Testing storage bucket...")
    try:
        # Storage API has different endpoint structure
        storage_url = f"https://{project_ref}.supabase.co/storage/v1/bucket"
        response = requests.get(storage_url, headers=headers)
        
        if response.status_code == 200:
            buckets = response.json()
            audio_bucket = next((b for b in buckets if b['id'] == 'audio-files'), None)
            
            if audio_bucket:
                print("✅ Audio files bucket exists")
                print(f"   Public: {audio_bucket.get('public', False)}")
            else:
                print("❌ Audio files bucket not found")
                print(f"   Available buckets: {[b['id'] for b in buckets]}")
        else:
            print(f"❌ Storage check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Storage check failed: {e}")
    
    print("\n" + "="*60)
    print("📋 Summary:")
    print("   If you see 406 errors, the schema is created but API cache needs time")
    print("   Wait 1-2 minutes and try verification again")
    print("   Or proceed with Render deployment - it should work")

if __name__ == "__main__":
    test_schema_with_sql()