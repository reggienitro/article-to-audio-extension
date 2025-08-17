/* Personal Data Lake Schema for Article-to-Audio */
/* Single-user system with AI agent access in mind */

-- Drop existing table if we're restructuring
DROP TABLE IF EXISTS article_audio CASCADE;

-- Create simplified article_audio table for personal data lake
CREATE TABLE article_audio (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    audio_url TEXT,
    audio_filename TEXT,
    source_url TEXT,
    voice TEXT DEFAULT 'en-US-BrianNeural',
    is_favorite BOOLEAN DEFAULT FALSE,
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb  -- Flexible field for AI agents
);

-- Indexes for efficient queries
CREATE INDEX idx_article_audio_created ON article_audio(created_at DESC);
CREATE INDEX idx_article_audio_favorite ON article_audio(is_favorite);
CREATE INDEX idx_article_audio_title ON article_audio USING gin(to_tsvector('english', title));
CREATE INDEX idx_article_audio_content ON article_audio USING gin(to_tsvector('english', content));

-- Storage bucket for audio files (if not exists)
INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-files', 'audio-files', true) 
ON CONFLICT (id) DO NOTHING;

-- Storage policies for audio files
DROP POLICY IF EXISTS "Public audio access" ON storage.objects;
CREATE POLICY "Public audio access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'audio-files');

DROP POLICY IF EXISTS "Audio upload" ON storage.objects;
CREATE POLICY "Audio upload" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'audio-files');

DROP POLICY IF EXISTS "Audio delete" ON storage.objects;
CREATE POLICY "Audio delete" 
ON storage.objects FOR DELETE 
USING (bucket_id = 'audio-files');

-- Test the setup
INSERT INTO article_audio (title, content, voice, word_count) VALUES 
('Data Lake Test', 'Testing the personal data lake setup for article-to-audio system.', 'en-US-BrianNeural', 10)
ON CONFLICT DO NOTHING;

-- Verify setup
SELECT 'Setup complete!' as status, COUNT(*) as test_records FROM article_audio;