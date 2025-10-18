/**
 * Enterprise Scanner Live Chat Widget
 * Real-time chat for Fortune 500 prospects with executive-level support
 */

class EnterpriseChat {
    constructor() {
        this.isOpen = false;
        this.socket = null;
        this.chatId = null;
        this.messages = [];
        this.userInfo = null;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
        this.initializeWebSocket();
        this.loadExecutiveTemplates();
    }

    createChatWidget() {
        // Create chat button
        const chatButton = document.createElement('div');
        chatButton.id = 'enterprise-chat-button';
        chatButton.innerHTML = `
            <div class="chat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            </div>
            <span class="chat-label">Enterprise Support</span>
        `;
        
        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'enterprise-chat-window';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="header-info">
                    <div class="status-indicator online"></div>
                    <div class="header-text">
                        <h4>Enterprise Security Consultant</h4>
                        <span class="status-text">Online - Avg response: 2 min</span>
                    </div>
                </div>
                <button class="close-chat" id="close-chat">&times;</button>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="welcome-message">
                    <div class="consultant-avatar">
                        <img src="/assets/consultant-avatar.png" alt="Security Consultant">
                    </div>
                    <div class="message-content">
                        <strong>Welcome to Enterprise Scanner</strong><br>
                        I'm here to help with your cybersecurity assessment needs. 
                        As a Fortune 500 focused platform, we provide enterprise-grade 
                        vulnerability management solutions.<br><br>
                        <strong>How can I assist you today?</strong>
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <button class="quick-btn" data-action="demo">Schedule Demo</button>
                <button class="quick-btn" data-action="roi">ROI Calculator</button>
                <button class="quick-btn" data-action="assessment">Security Assessment</button>
            </div>
            
            <div class="chat-input-area">
                <input type="text" id="chat-input" placeholder="Type your message..." maxlength="500">
                <button id="send-message" class="send-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                    </svg>
                </button>
            </div>
            
            <div class="chat-footer">
                <small>Powered by Enterprise Scanner • End-to-end encrypted</small>
            </div>
        `;

        document.body.appendChild(chatButton);
        document.body.appendChild(chatWindow);
    }

    attachEventListeners() {
        // Chat button toggle
        document.getElementById('enterprise-chat-button').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.getElementById('close-chat').addEventListener('click', () => {
            this.closeChat();
        });

        // Send message
        document.getElementById('send-message').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Quick actions
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.dataset.action);
            });
        });
    }

    toggleChat() {
        const chatWindow = document.getElementById('enterprise-chat-window');
        const chatButton = document.getElementById('enterprise-chat-button');
        
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const chatWindow = document.getElementById('enterprise-chat-window');
        const chatButton = document.getElementById('enterprise-chat-button');
        
        chatWindow.classList.add('open');
        chatButton.classList.add('active');
        this.isOpen = true;
        
        // Track engagement
        this.trackEvent('chat_opened');
        
        // Focus input
        setTimeout(() => {
            document.getElementById('chat-input').focus();
        }, 300);
    }

    closeChat() {
        const chatWindow = document.getElementById('enterprise-chat-window');
        const chatButton = document.getElementById('enterprise-chat-button');
        
        chatWindow.classList.remove('open');
        chatButton.classList.remove('active');
        this.isOpen = false;
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            input.value = '';
            
            // Send to backend
            this.sendToServer(message);
        }
    }

    addMessage(content, sender, isTemplate = false) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${this.escapeHtml(content)}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="consultant-avatar">
                    <img src="/assets/consultant-avatar.png" alt="Consultant">
                </div>
                <div class="message-bubble">
                    <div class="message-content">${content}</div>
                    <div class="message-time">${this.formatTime(new Date())}</div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.messages.push({
            content,
            sender,
            timestamp: new Date(),
            isTemplate
        });
    }

    handleQuickAction(action) {
        switch (action) {
            case 'demo':
                this.addMessage(
                    "I'd like to schedule a demo to see how Enterprise Scanner can help secure our organization.", 
                    'user'
                );
                this.sendToServer('REQUEST_DEMO');
                break;
            case 'roi':
                this.addMessage(
                    "Can you help me calculate the ROI for implementing Enterprise Scanner?", 
                    'user'
                );
                this.sendToServer('ROI_CALCULATOR');
                break;
            case 'assessment':
                this.addMessage(
                    "I'd like to start a security assessment for our organization.", 
                    'user'
                );
                this.sendToServer('SECURITY_ASSESSMENT');
                break;
        }
    }

    sendToServer(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'message',
                content: message,
                chatId: this.chatId,
                timestamp: new Date().toISOString(),
                userInfo: this.userInfo
            }));
        } else {
            // Fallback to HTTP API
            this.sendViaAPI(message);
        }
    }

    async sendViaAPI(message) {
        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    chatId: this.chatId,
                    userInfo: this.userInfo
                })
            });
            
            const data = await response.json();
            
            if (data.response) {
                setTimeout(() => {
                    this.addMessage(data.response, 'consultant', true);
                }, 1000 + Math.random() * 2000); // Simulate human response time
            }
            
            if (data.escalate) {
                this.escalateToHuman(data.reason);
            }
            
        } catch (error) {
            console.error('Chat API error:', error);
            this.addMessage(
                "I'm having trouble connecting right now. Please email us at <a href='mailto:sales@enterprisescanner.com'>sales@enterprisescanner.com</a> for immediate assistance.",
                'consultant'
            );
        }
    }

    initializeWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            this.socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);
            
            this.socket.onopen = () => {
                console.log('Chat WebSocket connected');
                this.chatId = this.generateChatId();
            };
            
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleServerMessage(data);
            };
            
            this.socket.onclose = () => {
                console.log('Chat WebSocket disconnected');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.initializeWebSocket(), 5000);
            };
            
        } catch (error) {
            console.log('WebSocket not available, using HTTP fallback');
        }
    }

    loadExecutiveTemplates() {
        this.templates = {
            greeting: "Thank you for your interest in Enterprise Scanner. How can I help you evaluate our cybersecurity platform for your organization?",
            demo: "I'd be happy to arrange a personalized demo. Our enterprise solutions have helped Fortune 500 companies save millions in breach prevention. What's the best time to connect?",
            roi: "Our ROI calculator shows most enterprises see 300-800% ROI within the first year. What's your current annual revenue so I can provide accurate projections?",
            pricing: "Enterprise Scanner offers flexible licensing for organizations of your scale. Our Fortune 500 clients typically see $2-5M in annual savings. Would you like me to prepare a custom proposal?",
            security: "Security is our top priority. We maintain SOC 2 Type II compliance, end-to-end encryption, and have helped organizations achieve NIST framework compliance. What specific security concerns can I address?",
            escalation: "Let me connect you with our enterprise security specialist who can provide detailed technical information. You'll hear from our team within 2 hours."
        };
    }

    generateChatId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    trackEvent(event, data = {}) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', event, {
                event_category: 'chat',
                ...data
            });
        }
    }

    escalateToHuman(reason) {
        this.addMessage(
            `I'm connecting you with a senior security consultant who specializes in ${reason}. 
            They'll be with you shortly. In the meantime, you can also reach our enterprise team 
            directly at <a href="mailto:sales@enterprisescanner.com">sales@enterprisescanner.com</a>.`,
            'consultant'
        );
        
        // Send escalation notification to sales team
        fetch('/api/chat/escalate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chatId: this.chatId,
                reason: reason,
                messages: this.messages,
                userInfo: this.userInfo
            })
        });
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enterpriseChat = new EnterpriseChat();
});