/* Fix existing articles table by adding missing columns */

/* Drop and recreate the table with correct structure */
DROP TABLE IF EXISTS articles CASCADE;

/* Create articles table with all required columns */
CREATE TABLE articles (
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

/* Create storage bucket if not exists */
INSERT INTO storage.buckets (id, name, public) 
VALUES ('audio-files', 'audio-files', true) 
ON CONFLICT (id) DO NOTHING;

/* Create storage policies */
DROP POLICY IF EXISTS "Public audio access" ON storage.objects;
CREATE POLICY "Public audio access" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'audio-files');

DROP POLICY IF EXISTS "Authenticated audio upload" ON storage.objects;
CREATE POLICY "Authenticated audio upload" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'audio-files');

/* Create indexes */
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_user_email ON articles(user_email);
CREATE INDEX idx_articles_is_favorite ON articles(is_favorite);

/* Create trigger function */
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

/* Create trigger */
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

/* Add test data */
INSERT INTO articles (title, content, voice, user_email) VALUES 
('Test Article', 'This is a test article to verify the schema is working correctly.', 'en-US-BrianNeural', 'aettefagh@gmail.com');