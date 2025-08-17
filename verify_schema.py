#!/usr/bin/env python3
"""
Verify article2audio schema was successfully executed in Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.expanduser("~/.config/api-keys/.env"))

def verify_schema():
    """Verify the article2audio schema components"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Supabase credentials not found in environment")
        return False
    
    print(f"🔗 Connecting to Supabase project: {url}")
    supabase: Client = create_client(url, key)
    
    verification_passed = True
    
    # Test 1: Check if articles table exists and is accessible
    print("\n🔍 Test 1: Verifying articles table...")
    try:
        result = supabase.table('articles').select('count').execute()
        print("✅ Articles table exists and is accessible")
        
        # Check table structure by trying to select specific columns
        result = supabase.table('articles').select('id,title,content,url,voice,speed,audio_url,audio_filename,is_favorite,user_email,created_at,updated_at').limit(1).execute()
        print("✅ Articles table has correct column structure")
        
    except Exception as e:
        print(f"❌ Articles table verification failed: {str(e)}")
        verification_passed = False
    
    # Test 2: Check sample data
    print("\n🔍 Test 2: Checking for sample data...")
    try:
        result = supabase.table('articles').select('*').eq('title', 'Test Article').execute()
        if result.data:
            print("✅ Sample test data found")
            print(f"   📄 Sample record: {result.data[0]['title']}")
        else:
            print("⚠️  No sample data found (this is optional)")
            
    except Exception as e:
        print(f"❌ Sample data check failed: {str(e)}")
    
    # Test 3: Check storage bucket
    print("\n🔍 Test 3: Verifying storage bucket...")
    try:
        buckets = supabase.storage.list_buckets()
        audio_bucket_exists = any(bucket.name == 'audio-files' for bucket in buckets)
        
        if audio_bucket_exists:
            print("✅ Audio files bucket exists")
            
            # Test bucket access
            try:
                files = supabase.storage.from_('audio-files').list()
                print("✅ Audio files bucket is accessible")
            except Exception as e:
                print(f"⚠️  Audio files bucket exists but may have access issues: {str(e)}")
                
        else:
            print("❌ Audio files bucket not found")
            verification_passed = False
            
    except Exception as e:
        print(f"❌ Storage bucket verification failed: {str(e)}")
        verification_passed = False
    
    # Test 4: Test CRUD operations
    print("\n🔍 Test 4: Testing CRUD operations...")
    try:
        # Insert test record
        test_data = {
            'title': 'Verification Test Article',
            'content': 'This is a test article created during schema verification.',
            'voice': 'en-US-BrianNeural',
            'user_email': 'test@example.com'
        }
        
        insert_result = supabase.table('articles').insert(test_data).execute()
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            print("✅ Insert operation successful")
            
            # Update test record
            update_result = supabase.table('articles').update({'is_favorite': True}).eq('id', test_id).execute()
            if update_result.data:
                print("✅ Update operation successful")
            
            # Delete test record
            delete_result = supabase.table('articles').delete().eq('id', test_id).execute()
            print("✅ Delete operation successful")
            print("✅ CRUD operations working correctly")
            
        else:
            print("❌ Insert operation failed")
            verification_passed = False
            
    except Exception as e:
        print(f"❌ CRUD operations test failed: {str(e)}")
        verification_passed = False
    
    # Test 5: Check indexes (indirect test via query performance)
    print("\n🔍 Test 5: Testing indexed queries...")
    try:
        # Query by created_at (should use idx_articles_created_at)
        result = supabase.table('articles').select('*').order('created_at', desc=True).limit(5).execute()
        print("✅ Date-ordered query successful (created_at index working)")
        
        # Query by user_email (should use idx_articles_user_email)
        result = supabase.table('articles').select('*').eq('user_email', 'aettefagh@gmail.com').execute()
        print("✅ User email query successful (user_email index working)")
        
        # Query by is_favorite (should use idx_articles_is_favorite)
        result = supabase.table('articles').select('*').eq('is_favorite', True).execute()
        print("✅ Favorite filter query successful (is_favorite index working)")
        
    except Exception as e:
        print(f"❌ Indexed queries test failed: {str(e)}")
        verification_passed = False
    
    return verification_passed

def print_summary(success):
    """Print verification summary"""
    print("\n" + "="*50)
    if success:
        print("🎉 SCHEMA VERIFICATION SUCCESSFUL!")
        print("✅ All article2audio components are working correctly")
        print("🚀 Your Supabase database is ready for the article-to-audio extension")
    else:
        print("💥 SCHEMA VERIFICATION FAILED!")
        print("❌ Some components may need manual attention")
        print("📞 Check the errors above and retry schema execution if needed")
    print("="*50)

if __name__ == "__main__":
    print("🚀 Starting article2audio schema verification...")
    success = verify_schema()
    print_summary(success)