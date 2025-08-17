#!/usr/bin/env python3
"""
Setup Article-to-Audio schema in Supabase project
Creates necessary tables for storing articles and audio files
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def setup_schema():
    """Create the article2audio schema in Supabase"""
    
    # Load credentials
    load_dotenv('/Users/aettefagh/.config/api-keys/.env')
    
    url = os.getenv("SUPABASE_URL")
    # Try service key first, fall back to anon key
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"🔗 Connecting to Supabase: {url}")
    
    try:
        supabase: Client = create_client(url, key)
        
        # Test connection
        result = supabase.table('_test_connection').select('*').limit(1).execute()
        print("✅ Supabase connection successful")
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False
    
    # SQL to create article2audio schema
    schema_sql = """
    -- Create articles table
    CREATE TABLE IF NOT EXISTS articles (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        url TEXT,
        voice TEXT DEFAULT 'en-US-BrianNeural',
        speed TEXT DEFAULT 'normal',
        audio_url TEXT,
        audio_filename TEXT,
        is_favorite BOOLEAN DEFAULT FALSE,
        user_email TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create storage bucket for audio files
    INSERT INTO storage.buckets (id, name, public) 
    VALUES ('audio-files', 'audio-files', true) 
    ON CONFLICT (id) DO NOTHING;

    -- Create storage policy for audio files
    CREATE POLICY IF NOT EXISTS "Public audio access" 
    ON storage.objects FOR SELECT 
    USING (bucket_id = 'audio-files');

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_articles_user_email ON articles(user_email);
    CREATE INDEX IF NOT EXISTS idx_articles_is_favorite ON articles(is_favorite);

    -- Create updated_at trigger
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    CREATE TRIGGER IF NOT EXISTS update_articles_updated_at 
        BEFORE UPDATE ON articles 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    print("🛠️ Creating article2audio schema...")
    
    try:
        # Execute schema creation
        # Note: We'll need to run this in Supabase SQL editor since Python client doesn't support DDL
        print("⚠️ Schema creation requires SQL Editor access")
        print("📋 Copy this SQL to your Supabase SQL Editor:")
        print("-" * 50)
        print(schema_sql)
        print("-" * 50)
        print("\n✅ After running the SQL, your project will be ready for article2audio!")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

if __name__ == "__main__":
    setup_schema()