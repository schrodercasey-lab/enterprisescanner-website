/**
 * AI COPILOT - CHAT WIDGET
 * Enterprise Scanner AI Security Assistant
 * 
 * Features:
 * - Real-time chat interface
 * - WebSocket streaming
 * - Quick reply buttons
 * - Source citations
 * - Typing indicators
 * - Message history
 * - Access level badges
 */

class AICopilotWidget {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/copilot';
        this.wsUrl = options.wsUrl || window.location.origin;
        this.sessionId = this.generateSessionId();
        this.socket = null;
        this.currentMessage = '';
        this.messageHistory = [];
        this.isTyping = false;
        
        this.init();
    }
    
    /**
     * Initialize widget
     */
    init() {
        this.injectStyles();
        this.createWidget();
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadHistory();
    }
    
    /**
     * Inject CSS styles
     */
    injectStyles() {
        if (document.getElementById('ai-copilot-styles')) return;
        
        const link = document.createElement('link');
        link.id = 'ai-copilot-styles';
        link.rel = 'stylesheet';
        link.href = '/css/ai_copilot.css';
        document.head.appendChild(link);
    }
    
    /**
     * Create widget HTML
     */
    createWidget() {
        const widgetHTML = `
            <div id="ai-copilot-widget" class="copilot-widget collapsed">
                <!-- Header -->
                <div class="copilot-header">
                    <div class="copilot-title">
                        <span class="copilot-icon">🤖</span>
                        <span class="copilot-name">AI Security Assistant</span>
                        <span class="copilot-status" id="copilot-status">●</span>
                    </div>
                    <div class="copilot-actions">
                        <button class="copilot-btn-minimize" id="copilot-minimize">−</button>
                        <button class="copilot-btn-close" id="copilot-close">×</button>
                    </div>
                </div>
                
                <!-- Access Level Badge -->
                <div class="copilot-badge" id="copilot-badge">
                    <span class="badge-icon">🔐</span>
                    <span class="badge-text">Customer Access</span>
                </div>
                
                <!-- Messages Container -->
                <div class="copilot-messages" id="copilot-messages">
                    <div class="copilot-welcome">
                        <h3>👋 Welcome!</h3>
                        <p>I'm your AI security assistant. I can help you:</p>
                        <ul>
                            <li>Analyze scan results</li>
                            <li>Explain vulnerabilities</li>
                            <li>Provide remediation guidance</li>
                            <li>Answer security questions</li>
                        </ul>
                        <p class="welcome-cta">Try asking: <em>"What are my critical vulnerabilities?"</em></p>
                    </div>
                </div>
                
                <!-- Typing Indicator -->
                <div class="copilot-typing" id="copilot-typing" style="display: none;">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-text">AI is thinking...</span>
                </div>
                
                <!-- Quick Replies -->
                <div class="copilot-quick-replies" id="copilot-quick-replies"></div>
                
                <!-- Input Area -->
                <div class="copilot-input-area">
                    <textarea 
                        id="copilot-input" 
                        class="copilot-input"
                        placeholder="Ask me anything..."
                        rows="1"
                        maxlength="2000"
                    ></textarea>
                    <button id="copilot-send" class="copilot-btn-send" disabled>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M2 10L18 2L10 18L8 11L2 10Z"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Character Count -->
                <div class="copilot-char-count" id="copilot-char-count">
                    <span id="copilot-char-current">0</span> / 2000
                </div>
            </div>
            
            <!-- Floating Button (when collapsed) -->
            <button id="copilot-fab" class="copilot-fab">
                <span class="fab-icon">🤖</span>
                <span class="fab-badge" id="copilot-unread" style="display: none;">1</span>
            </button>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }
    
    /**
     * Connect to WebSocket
     */
    connectWebSocket() {
        this.socket = io(this.wsUrl, {
            path: '/socket.io',
            transports: ['websocket', 'polling']
        });
        
        this.socket.on('connect', () => {
            this.updateStatus('connected');
            console.log('AI Copilot connected');
        });
        
        this.socket.on('disconnect', () => {
            this.updateStatus('disconnected');
            console.log('AI Copilot disconnected');
        });
        
        this.socket.on('chunk', (data) => {
            this.handleChunk(data);
        });
        
        this.socket.on('complete', (data) => {
            this.handleComplete(data);
        });
        
        this.socket.on('error', (error) => {
            this.handleError(error);
        });
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // FAB button
        document.getElementById('copilot-fab').addEventListener('click', () => {
            this.toggleWidget();
        });
        
        // Minimize button
        document.getElementById('copilot-minimize').addEventListener('click', () => {
            this.toggleWidget();
        });
        
        // Close button
        document.getElementById('copilot-close').addEventListener('click', () => {
            this.closeWidget();
        });
        
        // Input textarea
        const input = document.getElementById('copilot-input');
        input.addEventListener('input', (e) => {
            this.handleInput(e);
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button
        document.getElementById('copilot-send').addEventListener('click', () => {
            this.sendMessage();
        });
    }
    
    /**
     * Toggle widget visibility
     */
    toggleWidget() {
        const widget = document.getElementById('ai-copilot-widget');
        const fab = document.getElementById('copilot-fab');
        
        if (widget.classList.contains('collapsed')) {
            widget.classList.remove('collapsed');
            fab.style.display = 'none';
            document.getElementById('copilot-input').focus();
            this.markAsRead();
        } else {
            widget.classList.add('collapsed');
            fab.style.display = 'flex';
        }
    }
    
    /**
     * Close widget
     */
    closeWidget() {
        document.getElementById('ai-copilot-widget').style.display = 'none';
        document.getElementById('copilot-fab').style.display = 'flex';
    }
    
    /**
     * Handle input changes
     */
    handleInput(e) {
        const input = e.target;
        const sendBtn = document.getElementById('copilot-send');
        const charCount = document.getElementById('copilot-char-current');
        
        // Update character count
        charCount.textContent = input.value.length;
        
        // Enable/disable send button
        sendBtn.disabled = input.value.trim().length === 0;
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }
    
    /**
     * Send message
     */
    sendMessage() {
        const input = document.getElementById('copilot-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to UI
        this.addMessage('user', message);
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        document.getElementById('copilot-char-current').textContent = '0';
        document.getElementById('copilot-send').disabled = true;
        
        // Show typing indicator
        this.showTyping();
        
        // Send to server
        this.socket.emit('chat', {
            message: message,
            user_id: this.getUserId(),
            session_id: this.sessionId,
            access_level: this.getAccessLevel(),
            stream: true
        });
        
        // Save to history
        this.messageHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date()
        });
        this.saveHistory();
    }
    
    /**
     * Handle streaming chunk
     */
    handleChunk(data) {
        if (!this.currentMessage) {
            this.hideTyping();
            this.currentMessage = this.createMessageElement('assistant', '');
        }
        
        const content = this.currentMessage.querySelector('.message-content');
        content.textContent += data.content;
        
        // Auto-scroll
        this.scrollToBottom();
    }
    
    /**
     * Handle complete message
     */
    handleComplete(data) {
        this.hideTyping();
        
        if (this.currentMessage) {
            // Update with final content
            const content = this.currentMessage.querySelector('.message-content');
            content.innerHTML = this.formatMessage(data.response);
            
            // Add metadata
            this.addMessageMetadata(this.currentMessage, data);
            
            this.currentMessage = null;
        } else {
            // Fallback: create new message
            this.addMessage('assistant', data.response, data);
        }
        
        // Show quick replies
        if (data.quick_replies && data.quick_replies.length > 0) {
            this.showQuickReplies(data.quick_replies);
        }
        
        // Save to history
        this.messageHistory.push({
            role: 'assistant',
            content: data.response,
            timestamp: new Date(),
            metadata: data
        });
        this.saveHistory();
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    /**
     * Handle error
     */
    handleError(error) {
        this.hideTyping();
        this.currentMessage = null;
        
        this.addMessage('system', `Error: ${error.message || 'Something went wrong. Please try again.'}`);
    }
    
    /**
     * Add message to UI
     */
    addMessage(role, content, metadata = null) {
        const messagesContainer = document.getElementById('copilot-messages');
        const messageEl = this.createMessageElement(role, content, metadata);
        
        messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
        
        return messageEl;
    }
    
    /**
     * Create message element
     */
    createMessageElement(role, content, metadata = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `copilot-message copilot-message-${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? '👤' : role === 'assistant' ? '🤖' : '⚠️';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessage(content);
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestamp);
        
        if (metadata) {
            this.addMessageMetadata(messageDiv, metadata);
        }
        
        return messageDiv;
    }
    
    /**
     * Add metadata to message
     */
    addMessageMetadata(messageEl, metadata) {
        // Confidence score
        if (metadata.confidence_score) {
            const confidence = document.createElement('div');
            confidence.className = 'message-confidence';
            confidence.innerHTML = `<span>Confidence: ${Math.round(metadata.confidence_score * 100)}%</span>`;
            messageEl.appendChild(confidence);
        }
        
        // Sources
        if (metadata.sources && metadata.sources.length > 0) {
            const sources = document.createElement('div');
            sources.className = 'message-sources';
            sources.innerHTML = '<strong>Sources:</strong><ul>' +
                metadata.sources.map(s => `<li>${s}</li>`).join('') +
                '</ul>';
            messageEl.appendChild(sources);
        }
    }
    
    /**
     * Format message content (basic markdown)
     */
    formatMessage(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    /**
     * Show typing indicator
     */
    showTyping() {
        document.getElementById('copilot-typing').style.display = 'flex';
        this.isTyping = true;
        this.scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    hideTyping() {
        document.getElementById('copilot-typing').style.display = 'none';
        this.isTyping = false;
    }
    
    /**
     * Show quick replies
     */
    showQuickReplies(replies) {
        const container = document.getElementById('copilot-quick-replies');
        container.innerHTML = '';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = reply;
            button.addEventListener('click', () => {
                document.getElementById('copilot-input').value = reply;
                this.sendMessage();
                container.innerHTML = '';
            });
            container.appendChild(button);
        });
    }
    
    /**
     * Update connection status
     */
    updateStatus(status) {
        const statusEl = document.getElementById('copilot-status');
        statusEl.className = `copilot-status status-${status}`;
        statusEl.title = status === 'connected' ? 'Connected' : 'Disconnected';
    }
    
    /**
     * Scroll to bottom
     */
    scrollToBottom() {
        const messages = document.getElementById('copilot-messages');
        messages.scrollTop = messages.scrollHeight;
    }
    
    /**
     * Mark as read (clear badge)
     */
    markAsRead() {
        document.getElementById('copilot-unread').style.display = 'none';
    }
    
    /**
     * Generate session ID
     */
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Get current user ID
     */
    getUserId() {
        // TODO: Integrate with your auth system
        return window.currentUserId || 'anonymous';
    }
    
    /**
     * Get user access level
     */
    getAccessLevel() {
        // TODO: Integrate with your auth system
        return window.userAccessLevel || 'public';
    }
    
    /**
     * Load message history
     */
    loadHistory() {
        const history = localStorage.getItem(`copilot_history_${this.sessionId}`);
        if (history) {
            this.messageHistory = JSON.parse(history);
            // TODO: Optionally restore messages to UI
        }
    }
    
    /**
     * Save message history
     */
    saveHistory() {
        localStorage.setItem(
            `copilot_history_${this.sessionId}`,
            JSON.stringify(this.messageHistory.slice(-50)) // Keep last 50 messages
        );
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aiCopilot = new AICopilotWidget({
        apiUrl: '/api/copilot',
        wsUrl: window.location.origin
    });
});
