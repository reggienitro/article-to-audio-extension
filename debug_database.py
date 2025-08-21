#!/usr/bin/env python3
"""Debug database connection and data"""

import os
from supabase import create_client

# Load from environment or use directly
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qslpqxjoupwyclmguniz.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A")

print(f"Connecting to: {SUPABASE_URL}")
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test basic query
print("\n1. Testing basic SELECT:")
result = client.table('articles').select('*').execute()
print(f"   Found {len(result.data)} articles")

# Test what the server sees
print("\n2. Testing server-like query:")
query = client.table('articles').select('*')
query = query.order('created_at', desc=False)
query = query.limit(50)
result = query.execute()

print(f"   Found {len(result.data)} articles:")
for article in result.data:
    print(f"   - {article['title']} (ID: {article['id'][:8]}...)")

# Try inserting a test
print("\n3. Testing INSERT:")
test_data = {
    'title': 'Python Debug Test',
    'content': 'Testing from Python script.',
    'voice': 'en-US-ChristopherNeural',
    'word_count': 4,
    'is_favorite': False
}

try:
    result = client.table('articles').insert(test_data).execute()
    if result.data:
        print(f"   ✅ Insert successful! ID: {result.data[0]['id']}")
    else:
        print("   ❌ Insert returned no data")
except Exception as e:
    print(f"   ❌ Insert failed: {e}")

# Check again
print("\n4. Final check:")
result = client.table('articles').select('id, title').execute()
for article in result.data:
    print(f"   - {article['title']} ({article['id'][:8]}...)")