/* Run these queries in Supabase SQL Editor to verify schema */

/* Check if articles table exists */
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'articles' 
ORDER BY ordinal_position;

/* Check if table has data */
SELECT COUNT(*) as total_articles FROM articles;

/* Check sample data */
SELECT id, title, user_email, created_at FROM articles LIMIT 3;

/* Check storage buckets */
SELECT id, name, public FROM storage.buckets WHERE id = 'audio-files';

/* Check storage policies */
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';

/* Check indexes */
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'articles';

/* Check triggers */
SELECT trigger_name, event_manipulation, action_statement 
FROM information_schema.triggers 
WHERE event_object_table = 'articles';