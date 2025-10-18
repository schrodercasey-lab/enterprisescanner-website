/**
 * Jupiter AI Configuration - API Keys & Settings
 * Configure your AI backend (Grok/OpenAI/Claude) for real AI responses
 * 
 * @version 1.0.0
 */

const JupiterAIConfig = {
    // ===========================================
    // API CONFIGURATION
    // ===========================================
    
    /**
     * Primary AI Provider
     * Options: 'grok', 'openai', 'claude', 'fallback'
     * 
     * - 'grok': X.AI's Grok (recommended for Jupiter)
     * - 'openai': OpenAI GPT-4/GPT-3.5
     * - 'claude': Anthropic Claude
     * - 'fallback': Use pre-programmed responses (no API needed)
     */
    provider: 'fallback', // Change to 'grok' when you have API key
    
    /**
     * API Keys
     * Get your keys from:
     * - Grok: https://console.x.ai/
     * - OpenAI: https://platform.openai.com/api-keys
     * - Claude: https://console.anthropic.com/
     * 
     * SECURITY WARNING: In production, NEVER expose API keys in frontend!
     * Use a backend proxy server to make API calls securely.
     */
    apiKeys: {
        grok: '', // Add your Grok API key here: 'xai-...'
        openai: '', // Add your OpenAI key here: 'sk-...'
        claude: '' // Add your Claude key here: 'sk-ant-...'
    },
    
    /**
     * API Endpoints
     * Use backend proxy for production (recommended)
     */
    endpoints: {
        grok: 'https://api.x.ai/v1/chat/completions',
        openai: 'https://api.openai.com/v1/chat/completions',
        claude: 'https://api.anthropic.com/v1/messages',
        
        // Use your own backend proxy (RECOMMENDED for production)
        proxy: '/api/chat' // Point to your secure backend
    },
    
    /**
     * Use Backend Proxy
     * HIGHLY RECOMMENDED for production to protect API keys
     * Set to true and configure endpoints.proxy
     */
    useProxy: false, // Set to true in production
    
    // ===========================================
    // AI MODEL SETTINGS
    // ===========================================
    
    models: {
        grok: 'grok-beta', // Grok model
        openai: 'gpt-4-turbo-preview', // or 'gpt-3.5-turbo'
        claude: 'claude-3-opus-20240229' // or 'claude-3-sonnet-20240229'
    },
    
    /**
     * AI Personality & System Prompt
     * Customize how Jupiter AI responds
     */
    systemPrompt: `You are Jupiter, an advanced AI security analyst assistant for Enterprise Scanner platform.

Your capabilities:
- Analyze cybersecurity threats and vulnerabilities
- Explain security concepts clearly to executives and technical users
- Provide actionable remediation advice
- Control and explain the 3D threat map interface
- Answer questions about Enterprise Scanner's features

Your personality:
- Professional yet approachable
- Confident but not arrogant
- Explain complex topics simply
- Use security industry terminology appropriately
- Proactive in suggesting next steps

Context awareness:
- You can see the current threat map layer (global, country, city, network, darkweb)
- You know about active threats being displayed
- You can trigger map controls and zoom levels
- You integrate with voice narration

Response guidelines:
- Keep responses concise but informative (2-4 sentences typical)
- Use emojis sparingly for visual emphasis
- Offer specific actions the user can take
- Reference the current map context when relevant
- Suggest scheduling demos or meetings when appropriate`,

    // ===========================================
    // RESPONSE SETTINGS
    // ===========================================
    
    /**
     * Temperature (0.0 - 2.0)
     * Lower = more focused/deterministic
     * Higher = more creative/random
     */
    temperature: 0.7,
    
    /**
     * Max tokens per response
     * Limits response length
     */
    maxTokens: 500,
    
    /**
     * Response timeout (milliseconds)
     */
    timeout: 30000, // 30 seconds
    
    // ===========================================
    // FEATURES
    // ===========================================
    
    features: {
        voiceOutput: true, // Text-to-speech for AI responses
        voiceInput: true, // Speech-to-text for user input
        fileAnalysis: true, // Upload files for security analysis
        contextAwareness: true, // AI sees current map state
        conversationHistory: true, // Remember previous messages
        smartSuggestions: true, // Context-based quick replies
        realTimeTyping: true // Show "Jupiter is typing..." indicator
    },
    
    // ===========================================
    // SECURITY SETTINGS
    // ===========================================
    
    security: {
        /**
         * Rate Limiting
         * Maximum messages per time window
         */
        rateLimit: {
            maxMessages: 30,
            windowMs: 60000 // 1 minute
        },
        
        /**
         * Content Filtering
         * Block inappropriate content
         */
        contentFilter: true,
        
        /**
         * Conversation Logging
         * Log conversations for quality/security (backend only)
         */
        logConversations: false, // Enable in production backend
        
        /**
         * Data Retention
         * How long to keep conversation history (days)
         */
        retentionDays: 30
    },
    
    // ===========================================
    // UI SETTINGS
    // ===========================================
    
    ui: {
        position: 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
        theme: 'cyberpunk', // 'cyberpunk', 'professional', 'minimal'
        initialMessage: true, // Show welcome message when chat opens
        typingAnimationSpeed: 50, // ms per character (for typewriter effect)
        soundEffects: false // Chat notification sounds
    }
};

// ===========================================
// PRODUCTION SECURITY GUIDE
// ===========================================

console.log(`
╔════════════════════════════════════════════════════════════════╗
║                  JUPITER AI CONFIGURATION                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  🔒 SECURITY BEST PRACTICES FOR PRODUCTION                     ║
║                                                                ║
║  1️⃣  NEVER expose API keys in frontend JavaScript             ║
║     ❌ BAD:  apiKeys.grok = 'xai-actual-key-here'             ║
║     ✅ GOOD: Use backend proxy server                         ║
║                                                                ║
║  2️⃣  Create a secure backend endpoint                         ║
║     Example: /api/chat → Your server → AI provider            ║
║                                                                ║
║  3️⃣  Environment variables for keys                           ║
║     Store keys in: .env, AWS Secrets, etc.                    ║
║                                                                ║
║  4️⃣  Rate limiting & authentication                           ║
║     Prevent abuse and unauthorized access                     ║
║                                                                ║
║  5️⃣  Monitor API usage & costs                                ║
║     Track spending and set budget alerts                      ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  📝 QUICK START GUIDE                                          ║
║                                                                ║
║  FOR DEVELOPMENT/TESTING (Insecure - Local Only):             ║
║                                                                ║
║  1. Get Grok API key: https://console.x.ai/                   ║
║  2. Edit this file (jupiter-ai-config.js)                     ║
║  3. Set: provider = 'grok'                                    ║
║  4. Add: apiKeys.grok = 'your-key-here'                       ║
║  5. Reload page and test Jupiter chat                         ║
║                                                                ║
║  FOR PRODUCTION (Secure - Required):                          ║
║                                                                ║
║  1. Create backend API endpoint: /api/chat                    ║
║  2. Store API keys in environment variables                   ║
║  3. Set: useProxy = true                                      ║
║  4. Set: endpoints.proxy = '/api/chat'                        ║
║  5. Frontend → Your backend → AI provider                     ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  🎯 BACKEND EXAMPLE (Node.js/Express)                          ║
║                                                                ║
║  app.post('/api/chat', async (req, res) => {                  ║
║    const apiKey = process.env.GROK_API_KEY;                   ║
║    const response = await fetch('https://api.x.ai/...', {     ║
║      headers: { 'Authorization': \`Bearer \${apiKey}\` }      ║
║    });                                                         ║
║    res.json(await response.json());                           ║
║  });                                                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
`);

// Export configuration
window.JupiterAIConfig = JupiterAIConfig;

