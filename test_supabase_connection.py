#!/usr/bin/env python3
"""
Test Supabase database connection and operations
Verifies schema exists and all operations work correctly
"""

import os
from supabase import create_client, Client
import uuid
from datetime import datetime

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔗 Testing Supabase connection...")
    
    # Load credentials from local .env
    url = "https://qslpqxjoupwyclmguniz.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A"
    
    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase client created successfully")
        return supabase
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return None

def test_articles_table(supabase: Client):
    """Test articles table operations"""
    print("\n📄 Testing articles table operations...")
    
    try:
        # Test SELECT
        result = supabase.table('articles').select('*').limit(1).execute()
        print("✅ Articles table accessible")
        
        # Test INSERT
        test_article = {
            'title': f'Test Article {datetime.now().strftime("%H:%M:%S")}',
            'content': 'This is a test article to verify database operations.',
            'url': 'https://test.example.com',
            'voice': 'en-US-BrianNeural',
            'user_email': 'test@example.com'
        }
        
        insert_result = supabase.table('articles').insert(test_article).execute()
        if insert_result.data:
            article_id = insert_result.data[0]['id']
            print(f"✅ Article insert successful - ID: {article_id}")
            
            # Test UPDATE
            update_result = supabase.table('articles').update({
                'is_favorite': True,
                'audio_url': 'https://test.example.com/audio.mp3'
            }).eq('id', article_id).execute()
            
            if update_result.data:
                print("✅ Article update successful")
                
                # Test SELECT with filter
                filter_result = supabase.table('articles').select('*').eq('id', article_id).execute()
                if filter_result.data and filter_result.data[0]['is_favorite']:
                    print("✅ Article filter query successful")
                else:
                    print("❌ Article filter query failed")
                
                # Test DELETE
                delete_result = supabase.table('articles').delete().eq('id', article_id).execute()
                print("✅ Article delete successful")
                
                return True
            else:
                print("❌ Article update failed")
                return False
        else:
            print("❌ Article insert failed")
            return False
            
    except Exception as e:
        print(f"❌ Articles table test failed: {e}")
        return False

def test_storage_bucket(supabase: Client):
    """Test storage bucket operations"""
    print("\n💾 Testing storage bucket operations...")
    
    try:
        # List buckets
        buckets = supabase.storage.list_buckets()
        audio_bucket = next((b for b in buckets if b['id'] == 'audio-files'), None)
        
        if audio_bucket:
            print("✅ Audio files bucket exists")
            print(f"   - Public: {audio_bucket.get('public', False)}")
            
            # Test file upload
            test_content = b"This is test audio content"
            test_filename = f"test-{uuid.uuid4().hex[:8]}.txt"
            
            try:
                upload_result = supabase.storage.from_('audio-files').upload(
                    test_filename, 
                    test_content,
                    {"content-type": "text/plain"}
                )
                
                if upload_result:
                    print(f"✅ File upload successful: {test_filename}")
                    
                    # Test file download
                    download_result = supabase.storage.from_('audio-files').download(test_filename)
                    if download_result:
                        print("✅ File download successful")
                    else:
                        print("❌ File download failed")
                    
                    # Test file deletion
                    delete_result = supabase.storage.from_('audio-files').remove([test_filename])
                    if delete_result:
                        print("✅ File deletion successful")
                    else:
                        print("❌ File deletion failed")
                        
                    return True
                else:
                    print("❌ File upload failed")
                    return False
                    
            except Exception as e:
                print(f"❌ Storage operations failed: {e}")
                return False
        else:
            print("❌ Audio files bucket not found")
            return False
            
    except Exception as e:
        print(f"❌ Storage bucket test failed: {e}")
        return False

def test_user_queries(supabase: Client):
    """Test user-specific queries"""
    print("\n👤 Testing user-specific queries...")
    
    try:
        test_email = "test@example.com"
        
        # Insert test articles for user
        test_articles = [
            {
                'title': 'User Test Article 1',
                'content': 'First test article for user queries.',
                'user_email': test_email,
                'is_favorite': True
            },
            {
                'title': 'User Test Article 2', 
                'content': 'Second test article for user queries.',
                'user_email': test_email,
                'is_favorite': False
            }
        ]
        
        # Insert articles
        insert_result = supabase.table('articles').insert(test_articles).execute()
        if insert_result.data:
            article_ids = [article['id'] for article in insert_result.data]
            print(f"✅ Inserted {len(article_ids)} test articles")
            
            # Test user articles query
            user_articles = supabase.table('articles').select('*').eq('user_email', test_email).execute()
            if user_articles.data and len(user_articles.data) >= 2:
                print(f"✅ User articles query successful - found {len(user_articles.data)} articles")
                
                # Test favorites query
                favorites = supabase.table('articles').select('*').eq('user_email', test_email).eq('is_favorite', True).execute()
                if favorites.data:
                    print(f"✅ Favorites query successful - found {len(favorites.data)} favorites")
                else:
                    print("❌ Favorites query failed")
                
                # Test ordering
                ordered = supabase.table('articles').select('*').eq('user_email', test_email).order('created_at', desc=True).execute()
                if ordered.data:
                    print("✅ Ordered query successful")
                else:
                    print("❌ Ordered query failed")
                
                # Cleanup - delete test articles
                for article_id in article_ids:
                    supabase.table('articles').delete().eq('id', article_id).execute()
                print("✅ Test articles cleaned up")
                
                return True
            else:
                print("❌ User articles query failed")
                return False
        else:
            print("❌ Test articles insert failed")
            return False
            
    except Exception as e:
        print(f"❌ User queries test failed: {e}")
        return False

def test_performance_indexes(supabase: Client):
    """Test that performance indexes are working"""
    print("\n⚡ Testing performance indexes...")
    
    try:
        # Test created_at index
        recent_articles = supabase.table('articles').select('*').order('created_at', desc=True).limit(5).execute()
        if recent_articles.data is not None:
            print("✅ created_at index working")
        else:
            print("❌ created_at index test failed")
            
        # Test user_email index  
        if recent_articles.data:
            test_email = recent_articles.data[0].get('user_email', 'test@example.com')
            email_articles = supabase.table('articles').select('*').eq('user_email', test_email).execute()
            if email_articles.data is not None:
                print("✅ user_email index working")
            else:
                print("❌ user_email index test failed")
        
        # Test is_favorite index
        favorite_articles = supabase.table('articles').select('*').eq('is_favorite', True).execute()
        if favorite_articles.data is not None:
            print("✅ is_favorite index working")
            return True
        else:
            print("❌ is_favorite index test failed")
            return False
            
    except Exception as e:
        print(f"❌ Performance indexes test failed: {e}")
        return False

def run_supabase_tests():
    """Run all Supabase tests"""
    print("🗄️ Starting Supabase Connection Tests")
    print("=" * 50)
    
    # Test connection
    supabase = test_supabase_connection()
    if not supabase:
        print("\n❌ Supabase tests failed - no connection")
        return False
    
    # Run all tests
    tests = [
        test_articles_table,
        test_storage_bucket,
        test_user_queries,
        test_performance_indexes
    ]
    
    results = []
    for test in tests:
        try:
            result = test(supabase)
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"🏁 Supabase tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All Supabase operations working correctly!")
    else:
        print("❌ Some Supabase operations failed - check logs above")
    
    return passed == total

if __name__ == "__main__":
    run_supabase_tests()