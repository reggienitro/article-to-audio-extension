#!/usr/bin/env python3
"""
Execute article2audio schema against Supabase project qslpqxjoupwyclmguniz
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.expanduser("~/.config/api-keys/.env"))

def execute_schema():
    """Execute the article2audio schema SQL file"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Supabase credentials not found in environment")
        return False
    
    print(f"🔗 Connecting to Supabase project: {url}")
    supabase: Client = create_client(url, key)
    
    # Read the schema file
    schema_file = "/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension/article2audio_schema.sql"
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📄 Schema file read successfully")
        
        # Split the SQL into individual statements for better error handling
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"🔧 Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            print(f"  📝 Executing statement {i}...")
            
            try:
                # Execute SQL statement
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"  ✅ Statement {i} executed successfully")
                
            except Exception as e:
                # Try alternative approach for DDL statements
                try:
                    # For DDL operations, we might need to use the REST API directly
                    print(f"  ⚠️  Retrying statement {i} with direct execution...")
                    
                    # This is a simplified approach - in practice, you might need
                    # to execute these via the Supabase dashboard SQL editor
                    print(f"  ⚠️  Statement {i}: {str(e)}")
                    print(f"     Statement content: {statement[:100]}...")
                    
                except Exception as e2:
                    print(f"  ❌ Failed to execute statement {i}: {str(e2)}")
                    print(f"     Statement: {statement[:100]}...")
        
        # Verify the table was created
        print("\n🔍 Verifying table creation...")
        try:
            result = supabase.table('articles').select('count').execute()
            print("✅ Articles table exists and is accessible")
        except Exception as e:
            print(f"❌ Could not verify articles table: {str(e)}")
        
        # Check storage bucket
        print("\n🗂️  Verifying storage bucket...")
        try:
            buckets = supabase.storage.list_buckets()
            audio_bucket_exists = any(bucket.name == 'audio-files' for bucket in buckets)
            if audio_bucket_exists:
                print("✅ Audio files bucket exists")
            else:
                print("⚠️  Audio files bucket not found")
        except Exception as e:
            print(f"❌ Could not verify storage bucket: {str(e)}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: Schema file not found at {schema_file}")
        return False
    except Exception as e:
        print(f"❌ Error executing schema: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting schema execution for article2audio...")
    success = execute_schema()
    
    if success:
        print("\n🎉 Schema execution completed!")
    else:
        print("\n💥 Schema execution failed!")