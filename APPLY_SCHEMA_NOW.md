# ⚠️ URGENT: Apply Database Schema Fix

The database schema is incorrect and preventing articles from being saved.

## Steps to Apply Schema:

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz

2. Navigate to SQL Editor (left sidebar)

3. Copy and paste the contents of `fix_supabase_schema.sql`

4. Click "Run" to execute

## What This Fixes:

- Renames `url` column to `source_url` to match server code
- Adds `metadata` JSONB column for storing extra data
- Removes unused columns (speed, user_email, updated_at)
- Creates proper indexes

## After Applying:

The system should start saving articles correctly and they will appear in the mobile interface.

## Test:
```bash
curl -X POST "https://article-to-audio-extension.onrender.com/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test After Schema Fix",
    "url": "https://example.com/test",
    "content": "Testing if articles are saved after schema fix.",
    "voice": "en-US-ChristopherNeural",
    "save": true
  }'
```

Then check: https://article-to-audio-extension.onrender.com/library