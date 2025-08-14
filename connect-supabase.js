// Supabase connection module for mobile UI
// This replaces the demo mode with real functionality

class SupabaseConnector {
    constructor(supabaseUrl, supabaseKey) {
        if (!supabaseUrl || !supabaseKey) {
            console.warn('Supabase credentials not provided - running in demo mode');
            this.demoMode = true;
            return;
        }
        
        this.demoMode = false;
        this.supabaseUrl = supabaseUrl;
        this.supabaseKey = supabaseKey;
        this.currentUser = null;
        
        // Initialize Supabase client if available
        if (typeof window !== 'undefined' && window.supabase) {
            this.client = window.supabase.createClient(supabaseUrl, supabaseKey);
            this.initializeAuth();
        }
    }
    
    async initializeAuth() {
        // Check for existing session
        const { data: { session } } = await this.client.auth.getSession();
        if (session) {
            this.currentUser = session.user;
            return session;
        }
        
        // Listen for auth changes
        this.client.auth.onAuthStateChange((event, session) => {
            if (event === 'SIGNED_IN' && session) {
                this.currentUser = session.user;
                this.onAuthChange?.(true, session.user);
            } else if (event === 'SIGNED_OUT') {
                this.currentUser = null;
                this.onAuthChange?.(false, null);
            }
        });
    }
    
    async signIn(email, password) {
        if (this.demoMode) {
            // Demo mode login
            this.currentUser = { email: email || 'demo@example.com' };
            return { success: true, user: this.currentUser };
        }
        
        try {
            const { data, error } = await this.client.auth.signInWithPassword({
                email,
                password
            });
            
            if (error) throw error;
            
            this.currentUser = data.user;
            return { success: true, user: data.user };
        } catch (error) {
            console.error('Sign in error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async signUp(email, password) {
        if (this.demoMode) {
            return { success: true, message: 'Demo mode - no real signup' };
        }
        
        try {
            const { data, error } = await this.client.auth.signUp({
                email,
                password
            });
            
            if (error) throw error;
            
            return { 
                success: true, 
                message: 'Check your email for verification',
                user: data.user 
            };
        } catch (error) {
            console.error('Sign up error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async signOut() {
        if (this.demoMode) {
            this.currentUser = null;
            return { success: true };
        }
        
        try {
            const { error } = await this.client.auth.signOut();
            if (error) throw error;
            
            this.currentUser = null;
            return { success: true };
        } catch (error) {
            console.error('Sign out error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async saveArticle(article) {
        if (this.demoMode) {
            console.log('Demo: Would save article:', article);
            return { success: true, id: 'demo-' + Date.now() };
        }
        
        if (!this.currentUser) {
            return { success: false, error: 'Not authenticated' };
        }
        
        try {
            const { data, error } = await this.client
                .from('articles')
                .insert({
                    user_id: this.currentUser.id,
                    title: article.title,
                    content: article.content,
                    source_url: article.sourceUrl,
                    audio_url: article.audioUrl,
                    is_favorite: article.isFavorite || false,
                    metadata: article.metadata || {}
                })
                .select()
                .single();
            
            if (error) throw error;
            
            return { success: true, data };
        } catch (error) {
            console.error('Save article error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async getArticles() {
        if (this.demoMode) {
            // Return demo articles
            return {
                success: true,
                data: [
                    {
                        id: 'demo1',
                        title: 'Demo Article 1',
                        source_url: 'https://example.com',
                        created_at: new Date().toISOString(),
                        is_favorite: false
                    }
                ]
            };
        }
        
        if (!this.currentUser) {
            return { success: false, error: 'Not authenticated' };
        }
        
        try {
            const { data, error } = await this.client
                .from('articles')
                .select('*')
                .eq('user_id', this.currentUser.id)
                .order('created_at', { ascending: false });
            
            if (error) throw error;
            
            return { success: true, data };
        } catch (error) {
            console.error('Get articles error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async toggleFavorite(articleId) {
        if (this.demoMode) {
            console.log('Demo: Would toggle favorite for:', articleId);
            return { success: true };
        }
        
        if (!this.currentUser) {
            return { success: false, error: 'Not authenticated' };
        }
        
        try {
            // First get current status
            const { data: article } = await this.client
                .from('articles')
                .select('is_favorite')
                .eq('id', articleId)
                .single();
            
            // Toggle the status
            const { error } = await this.client
                .from('articles')
                .update({ is_favorite: !article.is_favorite })
                .eq('id', articleId);
            
            if (error) throw error;
            
            return { success: true, isFavorite: !article.is_favorite };
        } catch (error) {
            console.error('Toggle favorite error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async updateStorageMode(mode) {
        // Save to user preferences
        if (this.demoMode) {
            localStorage.setItem('storageMode', mode);
            return { success: true };
        }
        
        if (!this.currentUser) {
            return { success: false, error: 'Not authenticated' };
        }
        
        try {
            const { error } = await this.client
                .from('user_preferences')
                .upsert({
                    user_id: this.currentUser.id,
                    storage_mode: mode,
                    updated_at: new Date().toISOString()
                });
            
            if (error) throw error;
            
            return { success: true };
        } catch (error) {
            console.error('Update storage mode error:', error);
            return { success: false, error: error.message };
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseConnector;
}