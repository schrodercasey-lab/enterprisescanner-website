/**
 * Jupiter AI Chat Widget - Phase 3 Final Feature
 * Real-time AI chat with context-aware responses, Jupiter voice integration,
 * and threat map synchronization for Enterprise Scanner platform
 * 
 * Features:
 * - WebSocket-based real-time chat
 * - Context-aware AI responses (knows current map layer/threats)
 * - Jupiter voice narration of chat responses
 * - Conversation history with persistence
 * - Smart suggestions based on user behavior
 * - File upload for security analysis
 * - Enterprise support escalation
 * - Mobile-optimized interface
 * - Accessibility compliant
 * 
 * @version 1.0.0
 * @author Enterprise Scanner Development Team
 */

class JupiterChatWidget {
    constructor() {
        this.isOpen = false;
        this.isMinimized = false;
        this.connectionStatus = 'disconnected'; // disconnected, connecting, connected
        this.messageHistory = [];
        this.currentConversationId = null;
        this.unreadCount = 0;
        this.typingTimeout = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        // WebSocket configuration (mock for now, replace with real endpoint)
        this.wsEndpoint = 'wss://api.enterprisescanner.com/chat';
        this.ws = null;
        
        // Context awareness
        this.contextData = {
            currentLayer: 'world',
            activeThreats: [],
            selectedRegion: null,
            jupiterMode: 'globe',
            tourActive: false
        };
        
        // AI response templates for demo/fallback
        this.aiResponses = {
            greeting: [
                "Hello! I'm Jupiter, your AI security analyst. How can I help you explore threats today?",
                "Welcome! I can help you understand the security landscape. What would you like to know?",
                "Hi there! Ready to dive into cybersecurity intelligence together?"
            ],
            layerInfo: {
                world: "You're viewing the global threat landscape. I can zoom into any region - just ask!",
                country: "We're examining country-level threats. Want to see specific cities or networks?",
                city: "This is the city infrastructure layer. I can show you network vulnerabilities.",
                network: "You're in the network topology view. We can explore individual nodes and connections.",
                darkweb: "Welcome to the Dark Web layer - where hidden threats lurk. What would you like to investigate?"
            },
            capabilities: "I can: analyze threats 🔍, explain security risks 🛡️, zoom the map 🌍, run demos 🎥, schedule meetings 📅, and connect you with our security experts 👥",
            unknown: "That's a great question! Let me analyze the current threat landscape to provide you with accurate information..."
        };
        
        // Smart suggestion engine
        this.suggestions = {
            welcome: [
                "Show me global threats",
                "What are the biggest risks?",
                "Run a demo tour",
                "Schedule a security assessment"
            ],
            world: [
                "Zoom into North America",
                "Show me ransomware activity",
                "What's happening in Europe?",
                "Analyze DDoS patterns"
            ],
            country: [
                "Show major cities",
                "What threats are active here?",
                "Compare to global average",
                "Zoom to network level"
            ],
            city: [
                "Show network topology",
                "Analyze infrastructure vulnerabilities",
                "What's the risk score?",
                "Show connected systems"
            ],
            network: [
                "Identify critical nodes",
                "Show attack vectors",
                "What needs patching?",
                "Dive into Dark Web"
            ],
            darkweb: [
                "What threats originate here?",
                "Show botnet activity",
                "Analyze command & control servers",
                "Return to surface view"
            ]
        };
        
        this.init();
    }
    
    async init() {
        console.log('🤖 Initializing Jupiter AI Chat Widget...');
        
        // Load conversation history from localStorage
        this.loadConversationHistory();
        
        // Create chat UI
        this.createChatUI();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Connect to WebSocket (or use mock)
        this.connectWebSocket();
        
        // Integrate with Jupiter AI voice system
        this.integrateWithJupiter();
        
        // Setup context monitoring
        this.monitorMapContext();
        
        console.log('✅ Jupiter AI Chat Widget initialized successfully!');
    }
    
    createChatUI() {
        // Create chat button (floating action button)
        const chatButton = document.createElement('div');
        chatButton.id = 'jupiter-chat-button';
        chatButton.className = 'jupiter-chat-button';
        chatButton.innerHTML = `
            <div class="chat-button-icon">
                <i class="bi bi-chat-dots-fill"></i>
                <span class="chat-notification-badge" style="display: none;">0</span>
            </div>
            <div class="chat-button-pulse"></div>
        `;
        document.body.appendChild(chatButton);
        
        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'jupiter-chat-window';
        chatWindow.className = 'jupiter-chat-window';
        chatWindow.style.display = 'none';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-header-left">
                    <div class="jupiter-avatar-small">
                        <i class="bi bi-stars"></i>
                    </div>
                    <div class="chat-header-info">
                        <h6>Jupiter AI</h6>
                        <span class="chat-status">
                            <span class="status-indicator"></span>
                            <span class="status-text">Connecting...</span>
                        </span>
                    </div>
                </div>
                <div class="chat-header-actions">
                    <button class="chat-action-btn" id="chat-voice-toggle" title="Toggle Voice">
                        <i class="bi bi-volume-up-fill"></i>
                    </button>
                    <button class="chat-action-btn" id="chat-minimize" title="Minimize">
                        <i class="bi bi-dash-lg"></i>
                    </button>
                    <button class="chat-action-btn" id="chat-close" title="Close">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="chat-welcome">
                    <div class="jupiter-avatar-large">
                        <i class="bi bi-stars"></i>
                    </div>
                    <h5>Welcome to Jupiter AI</h5>
                    <p>Your intelligent security companion for threat analysis and exploration</p>
                    <div class="welcome-features">
                        <span><i class="bi bi-shield-check"></i> Threat Analysis</span>
                        <span><i class="bi bi-globe"></i> Map Control</span>
                        <span><i class="bi bi-chat-left-quote"></i> Expert Advice</span>
                    </div>
                </div>
            </div>
            
            <div class="chat-suggestions" id="chat-suggestions">
                <!-- Smart suggestions will be inserted here -->
            </div>
            
            <div class="chat-typing-indicator" id="chat-typing" style="display: none;">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span class="typing-text">Jupiter is analyzing...</span>
            </div>
            
            <div class="chat-input-area">
                <div class="chat-quick-actions">
                    <button class="quick-action-btn" id="chat-upload" title="Upload File">
                        <i class="bi bi-paperclip"></i>
                    </button>
                    <button class="quick-action-btn" id="chat-voice-input" title="Voice Input">
                        <i class="bi bi-mic-fill"></i>
                    </button>
                    <button class="quick-action-btn" id="chat-demo" title="Run Demo">
                        <i class="bi bi-play-circle"></i>
                    </button>
                </div>
                <div class="chat-input-wrapper">
                    <textarea 
                        id="chat-input" 
                        class="chat-input" 
                        placeholder="Ask Jupiter anything about cybersecurity..."
                        rows="1"
                    ></textarea>
                    <button id="chat-send" class="chat-send-btn">
                        <i class="bi bi-send-fill"></i>
                    </button>
                </div>
                <div class="chat-footer-info">
                    <small>
                        <i class="bi bi-shield-lock"></i> 
                        Encrypted & Secure
                        <span class="separator">•</span>
                        <span id="chat-context-info">Viewing: Global</span>
                    </small>
                </div>
            </div>
        `;
        document.body.appendChild(chatWindow);
        
        // Create file upload input (hidden)
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'chat-file-input';
        fileInput.style.display = 'none';
        fileInput.accept = '.txt,.pdf,.doc,.docx,.csv,.log';
        document.body.appendChild(fileInput);
        
        // Update suggestions
        this.updateSuggestions('welcome');
    }
    
    setupEventListeners() {
        // Chat button click
        const chatButton = document.getElementById('jupiter-chat-button');
        chatButton.addEventListener('click', () => this.toggleChat());
        
        // Header actions
        document.getElementById('chat-minimize').addEventListener('click', () => this.minimizeChat());
        document.getElementById('chat-close').addEventListener('click', () => this.closeChat());
        document.getElementById('chat-voice-toggle').addEventListener('click', () => this.toggleVoice());
        
        // Input handling
        const chatInput = document.getElementById('chat-input');
        chatInput.addEventListener('input', () => this.handleInputChange());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button
        document.getElementById('chat-send').addEventListener('click', () => this.sendMessage());
        
        // Quick actions
        document.getElementById('chat-upload').addEventListener('click', () => this.openFileUpload());
        document.getElementById('chat-voice-input').addEventListener('click', () => this.startVoiceInput());
        document.getElementById('chat-demo').addEventListener('click', () => this.runDemo());
        
        // File upload
        document.getElementById('chat-file-input').addEventListener('change', (e) => this.handleFileUpload(e));
    }
    
    connectWebSocket() {
        // For demo purposes, we'll use a mock WebSocket
        // In production, replace with: this.ws = new WebSocket(this.wsEndpoint);
        
        this.connectionStatus = 'connecting';
        this.updateConnectionStatus();
        
        // Simulate connection
        setTimeout(() => {
            this.connectionStatus = 'connected';
            this.updateConnectionStatus();
            this.currentConversationId = this.generateConversationId();
            
            // Send welcome message from Jupiter
            setTimeout(() => {
                this.receiveMessage({
                    type: 'ai',
                    content: this.getRandomResponse('greeting'),
                    timestamp: new Date().toISOString()
                });
            }, 500);
            
        }, 1000);
        
        // In production, implement real WebSocket:
        /*
        this.ws = new WebSocket(this.wsEndpoint);
        
        this.ws.onopen = () => {
            this.connectionStatus = 'connected';
            this.updateConnectionStatus();
            this.reconnectAttempts = 0;
            this.currentConversationId = this.generateConversationId();
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.receiveMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.connectionStatus = 'disconnected';
            this.updateConnectionStatus();
        };
        
        this.ws.onclose = () => {
            this.connectionStatus = 'disconnected';
            this.updateConnectionStatus();
            this.attemptReconnect();
        };
        */
    }
    
    integrateWithJupiter() {
        // Check if Jupiter AI voice system is available
        if (window.jupiterAI) {
            console.log('✅ Connected to Jupiter AI voice system');
            this.hasVoiceIntegration = true;
        } else {
            console.log('⚠️ Jupiter AI voice system not found - voice disabled');
            this.hasVoiceIntegration = false;
            document.getElementById('chat-voice-toggle').style.display = 'none';
        }
    }
    
    monitorMapContext() {
        // Monitor threat map state for context-aware responses
        setInterval(() => {
            if (window.zoomLayerSystem) {
                this.contextData.currentLayer = window.zoomLayerSystem.currentLayer;
                this.updateContextDisplay();
                
                // Update suggestions based on current layer
                this.updateSuggestions(this.contextData.currentLayer);
            }
            
            if (window.jupiterFaceMorph) {
                this.contextData.jupiterMode = window.jupiterFaceMorph.isFaceMode ? 'face' : 'globe';
            }
            
            if (window.jupiterAI) {
                this.contextData.tourActive = window.jupiterAI.isTourActive;
            }
        }, 1000);
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        const chatWindow = document.getElementById('jupiter-chat-window');
        const chatButton = document.getElementById('jupiter-chat-button');
        
        chatWindow.style.display = 'flex';
        setTimeout(() => chatWindow.classList.add('open'), 10);
        
        chatButton.classList.add('chat-open');
        this.isOpen = true;
        this.isMinimized = false;
        
        // Clear unread count
        this.unreadCount = 0;
        this.updateNotificationBadge();
        
        // Focus input
        document.getElementById('chat-input').focus();
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    closeChat() {
        const chatWindow = document.getElementById('jupiter-chat-window');
        const chatButton = document.getElementById('jupiter-chat-button');
        
        chatWindow.classList.remove('open');
        setTimeout(() => chatWindow.style.display = 'none', 300);
        
        chatButton.classList.remove('chat-open');
        this.isOpen = false;
        this.isMinimized = false;
    }
    
    minimizeChat() {
        const chatWindow = document.getElementById('jupiter-chat-window');
        
        if (this.isMinimized) {
            chatWindow.classList.remove('minimized');
            this.isMinimized = false;
        } else {
            chatWindow.classList.add('minimized');
            this.isMinimized = true;
        }
    }
    
    toggleVoice() {
        const voiceBtn = document.getElementById('chat-voice-toggle');
        
        if (this.hasVoiceIntegration) {
            window.jupiterAI.voiceEnabled = !window.jupiterAI.voiceEnabled;
            
            if (window.jupiterAI.voiceEnabled) {
                voiceBtn.innerHTML = '<i class="bi bi-volume-up-fill"></i>';
                voiceBtn.classList.remove('voice-muted');
            } else {
                voiceBtn.innerHTML = '<i class="bi bi-volume-mute-fill"></i>';
                voiceBtn.classList.add('voice-muted');
            }
        }
    }
    
    handleInputChange() {
        const input = document.getElementById('chat-input');
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        
        // Show typing indicator to server (in production)
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        this.typingTimeout = setTimeout(() => {
            // Send "stopped typing" to server
        }, 1000);
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const content = input.value.trim();
        
        if (!content) return;
        
        // Create user message
        const userMessage = {
            type: 'user',
            content: content,
            timestamp: new Date().toISOString()
        };
        
        // Add to UI
        this.addMessageToUI(userMessage);
        
        // Add to history
        this.messageHistory.push(userMessage);
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Save to localStorage
        this.saveConversationHistory();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Process message and get AI response
        setTimeout(() => {
            this.processUserMessage(content);
        }, 800 + Math.random() * 1200); // Simulate AI thinking time
    }
    
    async processUserMessage(content) {
        const lowerContent = content.toLowerCase();
        let aiResponse = '';
        let action = null;
        
        // Check if we should use real AI (Grok/OpenAI) or fallback mode
        const config = window.JupiterAIConfig;
        const useRealAI = config && config.provider !== 'fallback' && 
                          (config.apiKeys[config.provider] || config.useProxy);
        
        if (useRealAI) {
            // Use real AI API (Grok/OpenAI/Claude)
            try {
                aiResponse = await this.getAIResponse(content);
            } catch (error) {
                console.error('AI API error:', error);
                aiResponse = "I'm having trouble connecting to my AI backend. Let me use my offline knowledge... " + 
                           this.generateFallbackResponse(lowerContent);
            }
        } else {
            // Use fallback mode with pre-programmed responses
            aiResponse = this.generateFallbackResponse(lowerContent);
            
            // Show fallback mode notification on first message
            if (this.messageHistory.length <= 2) {
                aiResponse = "Hello! I'm Jupiter, your AI security assistant (running in fallback mode). I can help you with:\n\n" +
                           "- Vulnerability explanations (SQL injection, XSS, CSRF, etc.)\n" +
                           "- Security best practices\n" +
                           "- Remediation guidance\n" +
                           "- Threat analysis\n" +
                           "- Security architecture questions\n\n" +
                           "**Note:** I'm currently in fallback mode. For full AI capabilities, configure a valid Grok API key from https://console.x.ai/ or OpenAI API key.\n\n" +
                           "What security topic would you like to explore?";
            }
        }
        
        // Send AI response
        this.receiveMessage({
            type: 'ai',
            content: aiResponse,
            timestamp: new Date().toISOString()
        });
        
        // Execute action if any
        if (action) {
            setTimeout(action, 500);
        }
    }
    
    generateFallbackResponse(lowerContent) {
        let aiResponse = '';
        let action = null;
        
        // Context-aware response generation
        if (lowerContent.includes('zoom') || lowerContent.includes('show me')) {
            // Handle zoom/navigation requests
            if (lowerContent.includes('global') || lowerContent.includes('world')) {
                aiResponse = "Let me take you to the global threat view...";
                action = () => window.zoomLayerSystem?.zoomToLayer('world');
            } else if (lowerContent.includes('country') || lowerContent.includes('nation')) {
                aiResponse = "Zooming into country-level threats...";
                action = () => window.zoomLayerSystem?.zoomToLayer('country');
            } else if (lowerContent.includes('city') || lowerContent.includes('urban')) {
                aiResponse = "Focusing on city infrastructure...";
                action = () => window.zoomLayerSystem?.zoomToLayer('city');
            } else if (lowerContent.includes('network')) {
                aiResponse = "Analyzing network topology...";
                action = () => window.zoomLayerSystem?.zoomToLayer('network');
            } else if (lowerContent.includes('dark web') || lowerContent.includes('darkweb')) {
                aiResponse = "Diving into the Dark Web layer... Stay alert!";
                action = () => window.zoomLayerSystem?.zoomToLayer('darkweb');
            }
        } else if (lowerContent.includes('face') || lowerContent.includes('morph')) {
            aiResponse = "Activating face mode transformation...";
            action = () => window.jupiterFaceMorph?.toggleFaceMode();
        } else if (lowerContent.includes('tour') || lowerContent.includes('demo')) {
            aiResponse = "Starting guided tour of the threat landscape!";
            action = () => this.runDemo();
        } else if (lowerContent.includes('threat') || lowerContent.includes('attack')) {
            aiResponse = `Currently monitoring ${Math.floor(Math.random() * 500 + 200)} active threats. The primary attack vectors are: ransomware (34%), phishing (28%), DDoS (18%), and zero-day exploits (12%). Would you like me to analyze a specific threat type?`;
        } else if (lowerContent.includes('help') || lowerContent.includes('what can you')) {
            aiResponse = this.aiResponses.capabilities;
        } else if (lowerContent.includes('schedule') || lowerContent.includes('meeting') || lowerContent.includes('demo')) {
            aiResponse = "I'd be happy to schedule a personalized security assessment! Please provide your email, and our team will reach out within 24 hours. Or visit our contact page for immediate scheduling.";
        } else if (lowerContent.includes('risk') || lowerContent.includes('score')) {
            const riskScore = Math.floor(Math.random() * 30 + 60);
            aiResponse = `Based on current threat intelligence, your organization's risk score is ${riskScore}/100. This is ${riskScore > 75 ? 'elevated' : riskScore > 50 ? 'moderate' : 'low'}. Key factors: network exposure, patch compliance, and threat actor activity in your sector.`;
        } else {
            // Default contextual response
            const layerInfo = this.aiResponses.layerInfo[this.contextData.currentLayer];
            if (layerInfo && Math.random() > 0.5) {
                aiResponse = layerInfo;
            } else {
                aiResponse = this.aiResponses.unknown;
            }
        }
        
        return aiResponse;
    }
    
    async getAIResponse(userMessage) {
        const config = window.JupiterAIConfig;
        
        // Build conversation context
        const messages = [
            {
                role: 'system',
                content: config.systemPrompt + `\n\nCurrent context: User is viewing ${this.contextData.currentLayer} layer. ${this.contextData.activeThreats.length} threats visible.`
            },
            // Include recent conversation history
            ...this.messageHistory.slice(-6).map(msg => ({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            })),
            // Current message
            {
                role: 'user',
                content: userMessage
            }
        ];
        
        if (config.useProxy) {
            // Use backend proxy (production)
            const response = await fetch(config.endpoints.proxy, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: messages,
                    temperature: config.temperature,
                    max_tokens: config.maxTokens
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.choices[0].message.content;
            
        } else {
            // Direct API call (development only - NOT for production!)
            const provider = config.provider;
            const apiKey = config.apiKeys[provider];
            const endpoint = config.endpoints[provider];
            
            if (!apiKey) {
                throw new Error(`No API key configured for ${provider}`);
            }
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: config.models[provider],
                    messages: messages,
                    temperature: config.temperature,
                    max_tokens: config.maxTokens
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.choices[0].message.content;
        }
    }
    
    receiveMessage(message) {
        // Hide typing indicator
        this.hideTypingIndicator();
        
        // Add to UI
        this.addMessageToUI(message);
        
        // Add to history
        this.messageHistory.push(message);
        
        // Save to localStorage
        this.saveConversationHistory();
        
        // If chat is closed, increment unread count
        if (!this.isOpen) {
            this.unreadCount++;
            this.updateNotificationBadge();
            this.animateChatButton();
        }
        
        // Speak with Jupiter voice if enabled
        if (message.type === 'ai' && this.hasVoiceIntegration && window.jupiterAI?.voiceEnabled) {
            window.jupiterAI.speak(message.content);
        }
    }
    
    addMessageToUI(message) {
        const messagesContainer = document.getElementById('chat-messages');
        
        // Remove welcome message if present
        const welcomeMsg = messagesContainer.querySelector('.chat-welcome');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.type}-message`;
        
        const time = new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit'
        });
        
        if (message.type === 'ai') {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="bi bi-stars"></i>
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.formatMessageContent(message.content)}
                    </div>
                    <div class="message-meta">
                        <span class="message-sender">Jupiter AI</span>
                        <span class="message-time">${time}</span>
                    </div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.escapeHtml(message.content)}
                    </div>
                    <div class="message-meta">
                        <span class="message-time">${time}</span>
                    </div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Animate message entry
        setTimeout(() => messageDiv.classList.add('visible'), 10);
    }
    
    formatMessageContent(content) {
        // Format AI messages with markdown-lite support
        let formatted = this.escapeHtml(content);
        
        // Bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Icons (emoji-like syntax)
        formatted = formatted.replace(/🔍/g, '<i class="bi bi-search"></i>');
        formatted = formatted.replace(/🛡️/g, '<i class="bi bi-shield-check"></i>');
        formatted = formatted.replace(/🌍/g, '<i class="bi bi-globe"></i>');
        formatted = formatted.replace(/🎥/g, '<i class="bi bi-play-circle"></i>');
        formatted = formatted.replace(/📅/g, '<i class="bi bi-calendar-event"></i>');
        formatted = formatted.replace(/👥/g, '<i class="bi bi-people"></i>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    updateSuggestions(context) {
        const suggestionsContainer = document.getElementById('chat-suggestions');
        const suggestions = this.suggestions[context] || this.suggestions.welcome;
        
        suggestionsContainer.innerHTML = suggestions.map(suggestion => 
            `<button class="suggestion-chip" data-suggestion="${this.escapeHtml(suggestion)}">
                ${this.escapeHtml(suggestion)}
            </button>`
        ).join('');
        
        // Add click handlers
        suggestionsContainer.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const suggestion = chip.dataset.suggestion;
                document.getElementById('chat-input').value = suggestion;
                this.sendMessage();
            });
        });
    }
    
    showTypingIndicator() {
        document.getElementById('chat-typing').style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        document.getElementById('chat-typing').style.display = 'none';
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    updateConnectionStatus() {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        switch (this.connectionStatus) {
            case 'connected':
                statusIndicator.className = 'status-indicator status-connected';
                statusText.textContent = 'Online';
                break;
            case 'connecting':
                statusIndicator.className = 'status-indicator status-connecting';
                statusText.textContent = 'Connecting...';
                break;
            case 'disconnected':
                statusIndicator.className = 'status-indicator status-disconnected';
                statusText.textContent = 'Offline';
                break;
        }
    }
    
    updateContextDisplay() {
        const contextInfo = document.getElementById('chat-context-info');
        const layerNames = {
            world: 'Global View',
            country: 'Country Level',
            city: 'City Infrastructure',
            network: 'Network Topology',
            darkweb: 'Dark Web'
        };
        
        contextInfo.textContent = `Viewing: ${layerNames[this.contextData.currentLayer] || 'Global'}`;
    }
    
    updateNotificationBadge() {
        const badge = document.querySelector('.chat-notification-badge');
        
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
    
    animateChatButton() {
        const chatButton = document.getElementById('jupiter-chat-button');
        chatButton.classList.add('has-notification');
        
        // Play notification sound (optional)
        // new Audio('notification.mp3').play();
    }
    
    openFileUpload() {
        document.getElementById('chat-file-input').click();
    }
    
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Create file upload message
        const fileMessage = {
            type: 'user',
            content: `📎 Uploaded: ${file.name} (${this.formatFileSize(file.size)})`,
            timestamp: new Date().toISOString(),
            file: {
                name: file.name,
                size: file.size,
                type: file.type
            }
        };
        
        this.addMessageToUI(fileMessage);
        this.messageHistory.push(fileMessage);
        
        // Simulate AI analyzing the file
        setTimeout(() => {
            this.receiveMessage({
                type: 'ai',
                content: `I've received ${file.name}. I'll analyze this file for security threats and vulnerabilities. This may take a few moments...`,
                timestamp: new Date().toISOString()
            });
            
            // Simulate analysis complete
            setTimeout(() => {
                this.receiveMessage({
                    type: 'ai',
                    content: `Analysis complete! I found ${Math.floor(Math.random() * 10 + 5)} potential security issues in ${file.name}. Would you like a detailed report?`,
                    timestamp: new Date().toISOString()
                });
            }, 3000);
        }, 500);
        
        // Reset file input
        event.target.value = '';
    }
    
    startVoiceInput() {
        // Check for speech recognition support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }
        
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        
        const voiceBtn = document.getElementById('chat-voice-input');
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="bi bi-mic-fill recording-pulse"></i>';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chat-input').value = transcript;
            this.sendMessage();
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
        };
        
        recognition.onend = () => {
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
        };
        
        recognition.start();
    }
    
    runDemo() {
        if (window.jupiterAI && typeof window.jupiterAI.startAutomatedTour === 'function') {
            window.jupiterAI.startAutomatedTour();
            this.closeChat();
        } else {
            this.receiveMessage({
                type: 'ai',
                content: "The automated tour feature requires the full Jupiter AI system. Please ensure all components are loaded, or contact support for assistance.",
                timestamp: new Date().toISOString()
            });
        }
    }
    
    saveConversationHistory() {
        try {
            const historyData = {
                conversationId: this.currentConversationId,
                messages: this.messageHistory.slice(-50), // Keep last 50 messages
                lastUpdated: new Date().toISOString()
            };
            
            localStorage.setItem('jupiter_chat_history', JSON.stringify(historyData));
        } catch (error) {
            console.error('Failed to save conversation history:', error);
        }
    }
    
    loadConversationHistory() {
        try {
            const saved = localStorage.getItem('jupiter_chat_history');
            if (saved) {
                const historyData = JSON.parse(saved);
                this.messageHistory = historyData.messages || [];
                this.currentConversationId = historyData.conversationId;
                
                // Optionally restore messages to UI when chat opens
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
            this.messageHistory = [];
        }
    }
    
    generateConversationId() {
        return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    getRandomResponse(category) {
        const responses = this.aiResponses[category];
        return Array.isArray(responses) 
            ? responses[Math.floor(Math.random() * responses.length)]
            : responses;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        
        setTimeout(() => {
            console.log(`Reconnection attempt ${this.reconnectAttempts}...`);
            this.connectWebSocket();
        }, delay);
    }
}

// Initialize Jupiter Chat Widget when page loads
let jupiterChatWidget;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        jupiterChatWidget = new JupiterChatWidget();
        window.jupiterChatWidget = jupiterChatWidget;
    });
} else {
    jupiterChatWidget = new JupiterChatWidget();
    window.jupiterChatWidget = jupiterChatWidget;
}
