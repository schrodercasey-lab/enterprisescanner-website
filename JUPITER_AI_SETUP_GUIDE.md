# 🤖 Jupiter AI Setup Guide - Get Real AI Responses!

## Current Status: Fallback Mode ⚠️

Your Jupiter AI chat is currently running in **fallback mode** - it's using pre-programmed responses instead of real AI. This guide will help you enable full Grok-powered intelligence!

---

## 🎯 Quick Start (Development/Testing Only)

### Step 1: Get Your Grok API Key

1. Visit **https://console.x.ai/**
2. Sign up or log in with your X (Twitter) account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `xai-...`)

**Cost:** 
- Grok offers generous free tier
- Pay-as-you-go pricing after that
- ~$0.01-0.05 per conversation typically

### Step 2: Configure Jupiter AI

Open this file:
```
website/js/jupiter-ai-config.js
```

Find these lines:
```javascript
provider: 'fallback', // Change to 'grok' when you have API key

apiKeys: {
    grok: '', // Add your Grok API key here: 'xai-...'
```

Change to:
```javascript
provider: 'grok', // ✅ Changed!

apiKeys: {
    grok: 'xai-YOUR-ACTUAL-KEY-HERE', // ✅ Add your key!
```

### Step 3: Include Config in Your Page

Add to `website/index.html` (in the `<head>` section):
```html
<!-- Jupiter AI Configuration -->
<script src="js/jupiter-ai-config.js?v=20251019c"></script>
```

Make sure it loads **before** `jupiter-ai-chat.js`:
```html
<script src="js/jupiter-ai-config.js?v=20251019c"></script>
<script src="js/jupiter-ai-chat.js?v=20251019c"></script>
```

### Step 4: Test It!

1. Reload your website
2. Open Jupiter AI chat (bottom right button)
3. Type: "test"
4. You should get intelligent AI responses! 🎉

---

## 🔒 Production Setup (REQUIRED for Live Site)

**⚠️ CRITICAL:** Never expose API keys in frontend JavaScript on production!

### Architecture:

```
User Browser → Your Website → Your Backend API → Grok API
                               (API key hidden)
```

### Step 1: Create Backend Proxy

**Example: Node.js/Express**

```javascript
// backend/server.js
const express = require('express');
const fetch = require('node-fetch');
const app = express();

app.use(express.json());

// Secure endpoint that proxies to Grok
app.post('/api/chat', async (req, res) => {
    try {
        // Get API key from environment variable (secure!)
        const apiKey = process.env.GROK_API_KEY;
        
        // Forward request to Grok API
        const response = await fetch('https://api.x.ai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'grok-beta',
                messages: req.body.messages,
                temperature: 0.7,
                max_tokens: 500
            })
        });
        
        const data = await response.json();
        res.json(data);
        
    } catch (error) {
        console.error('Chat API error:', error);
        res.status(500).json({ error: 'Failed to process chat request' });
    }
});

app.listen(3000, () => console.log('Backend running on port 3000'));
```

**Set environment variable:**
```bash
export GROK_API_KEY=xai-your-key-here
```

### Step 2: Configure Frontend to Use Proxy

In `jupiter-ai-config.js`:
```javascript
provider: 'grok',
useProxy: true, // ✅ Use backend proxy
endpoints: {
    proxy: '/api/chat' // Your backend endpoint
},
apiKeys: {
    grok: '', // ❌ Leave empty! Key is in backend
```

### Step 3: Deploy Securely

1. **Backend:**
   - Deploy to your server (same as enterprisescanner.com)
   - Store API key in environment variables
   - Never commit keys to git

2. **Frontend:**
   - No API keys in JavaScript files
   - Configure proxy endpoint
   - Deploy as normal

---

## 🐍 Backend Examples (Multiple Languages)

### Python/Flask

```python
# backend/app.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    api_key = os.environ.get('GROK_API_KEY')
    
    response = requests.post(
        'https://api.x.ai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'grok-beta',
            'messages': request.json['messages'],
            'temperature': 0.7,
            'max_tokens': 500
        }
    )
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
```

### PHP

```php
<?php
// backend/chat.php
header('Content-Type: application/json');

$apiKey = getenv('GROK_API_KEY');
$data = json_decode(file_get_contents('php://input'), true);

$ch = curl_init('https://api.x.ai/v1/chat/completions');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'model' => 'grok-beta',
    'messages' => $data['messages'],
    'temperature' => 0.7,
    'max_tokens' => 500
]));

$response = curl_exec($ch);
curl_close($ch);

echo $response;
?>
```

---

## 🔐 Security Checklist

Before going live:

- [ ] API keys stored in environment variables (not code)
- [ ] Backend proxy implemented (no direct frontend → API calls)
- [ ] Rate limiting enabled (prevent abuse)
- [ ] Authentication required (protect your endpoint)
- [ ] CORS configured properly
- [ ] Error handling doesn't leak sensitive info
- [ ] Logging enabled for monitoring
- [ ] Budget alerts set in Grok dashboard
- [ ] `.env` files in `.gitignore`
- [ ] API keys rotated regularly

---

## 💰 Cost Optimization

### Grok Pricing (Example):
- **Input tokens:** ~$0.50 per 1M tokens
- **Output tokens:** ~$1.50 per 1M tokens
- **Average conversation:** ~500 tokens = ~$0.001

### Tips to Save Money:
1. **Cache common questions** - Store responses to FAQs
2. **Set max_tokens limits** - Prevent overly long responses
3. **Rate limiting** - Prevent spam/abuse
4. **Fallback mode** - Use for non-critical queries
5. **Monitor usage** - Set up budget alerts

---

## 🧪 Testing Your Setup

### Test Script (Browser Console):

```javascript
// Test if config loaded
console.log('Provider:', JupiterAIConfig.provider);
console.log('Has Grok key:', !!JupiterAIConfig.apiKeys.grok);
console.log('Using proxy:', JupiterAIConfig.useProxy);

// Test chat (if using real API)
if (window.jupiterChatWidget) {
    jupiterChatWidget.openChat();
    // Then manually type a message in the chat
}
```

### Expected Behavior:

**Fallback Mode (No API):**
- Responses are pre-programmed
- Message: "I'm currently in fallback mode"
- Instant responses

**Grok Mode (With API):**
- Responses are intelligent and contextual
- Slight delay (0.5-2 seconds)
- Personalized to your question
- Aware of threat map context

---

## 🆘 Troubleshooting

### "Still showing fallback mode"
1. Check `JupiterAIConfig.provider` is set to `'grok'`
2. Verify API key is valid (test in Grok console)
3. Check browser console for errors
4. Clear cache and reload

### "API key invalid"
1. Ensure key starts with `xai-`
2. Check for extra spaces/quotes
3. Verify key not expired in Grok dashboard
4. Try regenerating key

### "CORS errors"
1. Using proxy endpoint? Configure CORS on backend
2. Direct API calls? Use backend proxy instead
3. Check network tab in DevTools

### "Rate limit exceeded"
1. Grok has rate limits per API key
2. Wait a few minutes and try again
3. Implement caching for common questions
4. Consider upgrading Grok plan

---

## 🎨 Customization

### Change AI Personality

Edit `systemPrompt` in `jupiter-ai-config.js`:

```javascript
systemPrompt: `You are Jupiter, but make me sound more casual and funny!
Use emojis liberally and make cybersecurity jokes.`
```

### Change Response Style

```javascript
temperature: 0.9, // More creative (0.0 - 2.0)
maxTokens: 1000, // Longer responses
```

### Use Different AI Provider

```javascript
provider: 'openai', // Use ChatGPT instead
apiKeys: {
    openai: 'sk-...' // OpenAI key
}
```

---

## 📊 Monitoring & Analytics

Track Jupiter AI usage:

```javascript
// Add to jupiter-ai-chat.js
async processUserMessage(content) {
    // Track message
    gtag('event', 'jupiter_message', {
        'event_category': 'ai_chat',
        'event_label': 'user_query',
        'value': 1
    });
    
    // ... rest of function
}
```

Monitor in Google Analytics:
- Message count
- Topics asked about
- Response times
- User engagement

---

## 🚀 Next Level Features

Once basic setup working:

1. **Voice Integration**
   - Text-to-speech for AI responses
   - Speech-to-text for user input
   - Already built into jupiter-ai-chat.js!

2. **File Analysis**
   - Upload security logs
   - AI analyzes for threats
   - Generates reports

3. **Threat Map Control**
   - "Show me threats in California"
   - AI zooms map automatically
   - Context-aware suggestions

4. **Meeting Scheduling**
   - "Schedule a demo"
   - AI collects info and books meeting
   - Calendly integration

---

## 📝 Summary

### For Local Testing (Quick & Easy):
1. Get Grok API key from https://console.x.ai/
2. Add to `jupiter-ai-config.js`
3. Change `provider: 'grok'`
4. Reload and test!

### For Production (Secure & Required):
1. Create backend proxy server
2. Store API key in environment variables
3. Configure frontend to use proxy
4. Deploy both frontend and backend

---

## 🎉 You're Ready!

Once configured, Jupiter AI will:
- ✅ Answer security questions intelligently
- ✅ Control the 3D threat map
- ✅ Provide personalized remediation advice
- ✅ Schedule demos and meetings
- ✅ Analyze uploaded files
- ✅ Speak responses with voice (optional)

**Need help?** Check the troubleshooting section or contact support@enterprisescanner.com

---

**Current Config Status:**
- Provider: `fallback` (change to `grok`)
- API Key: Not configured
- Proxy: Not enabled
- Status: Ready for setup! 🚀
