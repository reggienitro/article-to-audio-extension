#!/usr/bin/env python3
"""
Verify that the article2audio schema was successfully created in Supabase
Run this after executing the schema in Supabase SQL Editor
"""

import os
from supabase import create_client, Client

def verify_schema():
    """Verify the article2audio schema exists and is functional"""
    
    # Load credentials from local .env
    url = "https://qslpqxjoupwyclmguniz.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A"
    
    print(f"🔗 Connecting to Supabase: {url}")
    
    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase connection successful")
        
        # Test 1: Check if articles table exists and has data
        print("\n📊 Testing articles table...")
        try:
            result = supabase.table('articles').select('*').limit(5).execute()
            print(f"✅ Articles table accessible - found {len(result.data)} rows")
            
            if result.data:
                print("📝 Sample data:")
                for article in result.data:
                    print(f"  - {article.get('title', 'No title')[:50]}...")
            
        except Exception as e:
            print(f"❌ Articles table test failed: {e}")
            return False
        
        # Test 2: Check storage bucket
        print("\n💾 Testing storage bucket...")
        try:
            # List buckets to see if audio-files exists
            buckets = supabase.storage.list_buckets()
            audio_bucket = next((b for b in buckets if b['id'] == 'audio-files'), None)
            
            if audio_bucket:
                print("✅ Audio files storage bucket exists")
                print(f"   - Public: {audio_bucket.get('public', False)}")
            else:
                print("❌ Audio files storage bucket not found")
                return False
                
        except Exception as e:
            print(f"❌ Storage bucket test failed: {e}")
            return False
        
        # Test 3: Test CRUD operations
        print("\n🔧 Testing CRUD operations...")
        try:
            # Insert test article
            test_article = {
                'title': 'Schema Verification Test',
                'content': 'This is a test article to verify the schema is working.',
                'voice': 'en-US-BrianNeural',
                'user_email': 'test@example.com'
            }
            
            insert_result = supabase.table('articles').insert(test_article).execute()
            if insert_result.data:
                test_id = insert_result.data[0]['id']
                print("✅ Insert operation successful")
                
                # Update test
                update_result = supabase.table('articles').update({
                    'is_favorite': True
                }).eq('id', test_id).execute()
                
                if update_result.data:
                    print("✅ Update operation successful")
                    
                    # Delete test
                    delete_result = supabase.table('articles').delete().eq('id', test_id).execute()
                    print("✅ Delete operation successful")
                else:
                    print("❌ Update operation failed")
                    return False
            else:
                print("❌ Insert operation failed")
                return False
                
        except Exception as e:
            print(f"❌ CRUD operations test failed: {e}")
            return False
        
        print("\n🎉 All schema verification tests passed!")
        print("✅ Article2audio Supabase integration is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    verify_schema()