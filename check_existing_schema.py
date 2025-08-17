#!/usr/bin/env python3
"""
Check existing articles table structure in Supabase
"""

from supabase import create_client

def check_existing_schema():
    """Check what's already in the database"""
    
    url = "https://qslpqxjoupwyclmguniz.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A"
    
    supabase = create_client(url, key)
    
    print("🔍 Checking existing database structure...")
    
    try:
        # Try to query the articles table to see what columns exist
        result = supabase.table('articles').select('*').limit(1).execute()
        
        if result.data:
            print("✅ Articles table exists with data:")
            print("📋 Sample record:")
            for key, value in result.data[0].items():
                print(f"   {key}: {value}")
            
            print(f"\n📊 Available columns: {list(result.data[0].keys())}")
        else:
            print("✅ Articles table exists but is empty")
            
            # Try to get column info by inserting a test record
            try:
                test_result = supabase.table('articles').insert({}).execute()
            except Exception as e:
                print(f"📋 Column info from error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error checking articles table: {e}")
        
        if "articles" in str(e):
            print("💡 Table exists but might have different structure")
        else:
            print("💡 Table might not exist yet")
    
    # Check storage buckets
    try:
        buckets = supabase.storage.list_buckets()
        print(f"\n💾 Storage buckets:")
        for bucket in buckets:
            print(f"   - {bucket['id']}: public={bucket.get('public', False)}")
    except Exception as e:
        print(f"❌ Error checking storage: {e}")

if __name__ == "__main__":
    check_existing_schema()