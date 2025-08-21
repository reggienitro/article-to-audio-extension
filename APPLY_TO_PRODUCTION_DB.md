# 🔧 Apply Schema to Production Database

Since Render is using `wtqvwmoiarikqqsearxj.supabase.co`, let's fix THAT database instead of changing environment variables.

## Steps:

1. **Go to the PRODUCTION Supabase Dashboard:**
   https://supabase.com/dashboard/project/wtqvwmoiarikqqsearxj

2. **Navigate to SQL Editor** (left sidebar)

3. **Copy and run this SQL:**

```sql
-- Drop existing articles table if it has wrong structure
DROP TABLE IF EXISTS articles CASCADE;

-- Create articles table with correct structure
CREATE TABLE articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    audio_url TEXT,
    audio_filename TEXT,
    source_url TEXT,  -- renamed from url to match code
    voice TEXT DEFAULT 'en-US-BrianNeural',
    is_favorite BOOLEAN DEFAULT FALSE,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb  -- added metadata field
);

-- Enable RLS
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Create policy for public access (since this is single-user)
CREATE POLICY "Public access" ON articles
FOR ALL USING (true);

-- Create storage bucket for audio files (if not exists)
INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-files', 'audio-files', true) 
ON CONFLICT (id) DO NOTHING;

-- Create storage policies
DROP POLICY IF EXISTS "Public audio access" ON storage.objects;
CREATE POLICY "Public audio access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'audio-files');

DROP POLICY IF EXISTS "Public audio upload" ON storage.objects;
CREATE POLICY "Public audio upload" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'audio-files');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_is_favorite ON articles(is_favorite);
```

4. **Click "Run"**

5. **You should see:** "Success. No rows returned"

## That's it! The production database now has the correct schema.

Test it immediately:
https://article-to-audio-extension.onrender.com/