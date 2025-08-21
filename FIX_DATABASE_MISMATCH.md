# 🚨 DATABASE MISMATCH ISSUE

## Problem Identified
The production server on Render is using a DIFFERENT Supabase database than what we've been configuring locally.

### Server is using:
- URL: `https://wtqvwmoiarikqqsearxj.supabase.co`
- This database has the old "Test Article"

### We've been configuring:
- URL: `https://qslpqxjoupwyclmguniz.supabase.co`  
- This database has the correct schema

## Solution Options

### Option 1: Update Render Environment (Recommended)
1. Go to Render Dashboard: https://dashboard.render.com
2. Find the `article-to-audio-extension` service
3. Go to Environment settings
4. Update:
   - `SUPABASE_URL` = `https://qslpqxjoupwyclmguniz.supabase.co`
   - `SUPABASE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzbHBxeGpvdXB3eWNsbWd1bml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUwNTMzMjUsImV4cCI6MjA3MDYyOTMyNX0.dB41u9cSpH4bD_6W-Jx5rZ4D9ud5yaceNJq-7y6QY5A`
5. Save and let it redeploy

### Option 2: Apply Schema to Current Database
1. Go to: https://supabase.com/dashboard/project/wtqvwmoiarikqqsearxj
2. Navigate to SQL Editor
3. Run the schema from `fix_supabase_schema.sql`
4. Keep using the current database

## After Fixing

Test with:
```bash
curl -X POST "https://article-to-audio-extension.onrender.com/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Fix Test",
    "content": "Testing after fixing database mismatch.",
    "voice": "en-US-ChristopherNeural"
  }'
```

Then check:
```bash
curl "https://article-to-audio-extension.onrender.com/library"
```

Articles should now save and appear correctly!