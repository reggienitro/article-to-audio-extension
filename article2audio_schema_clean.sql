/* Article-to-Audio Schema for Supabase */

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

INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-files', 'audio-files', true) 
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Public audio access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'audio-files');

CREATE POLICY "Authenticated audio upload" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'audio-files');

CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_user_email ON articles(user_email);
CREATE INDEX IF NOT EXISTS idx_articles_is_favorite ON articles(is_favorite);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO articles (title, content, voice, user_email) VALUES 
('Test Article', 'This is a test article to verify the schema is working correctly.', 'en-US-BrianNeural', 'aettefagh@gmail.com')
ON CONFLICT DO NOTHING;