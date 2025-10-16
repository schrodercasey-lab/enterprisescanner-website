/**
 * Enterprise Scanner Live Chat Widget
 * Real-time chat for Fortune 500 prospects with executive-level support
 */

class EnterpriseChat {
    constructor() {
        this.isOpen = false;
        this.socket = null;
        this.chatId = null;
        this.userId = null;
        this.messages = [];
        this.userInfo = null;
        this.isConnected = false;
        this.typingTimeout = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
        this.loadUserInfo();
        this.initializeWebSocket();
        this.loadExecutiveTemplates();
        this.startHeartbeat();
    }

    createChatWidget() {
        // Create chat button
        const chatButton = document.createElement('div');
        chatButton.id = 'enterprise-chat-button';
        chatButton.innerHTML = `
            <div class="chat-pulse"></div>
            <div class="chat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            </div>
            <span class="chat-label">Enterprise Support</span>
            <div class="chat-notification" id="chat-notification" style="display: none;">
                <span class="notification-count">1</span>
            </div>
        `;
        
        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'enterprise-chat-window';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="header-info">
                    <div class="status-indicator" id="connection-status"></div>
                    <div class="header-text">
                        <h4>Enterprise Security Consultant</h4>
                        <span class="status-text" id="status-text">Connecting...</span>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="header-btn" id="minimize-chat" title="Minimize">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19,13H5V11H19V13Z"/>
                        </svg>
                    </button>
                    <button class="header-btn" id="close-chat" title="Close">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="welcome-message">
                    <div class="consultant-avatar">
                        <div class="avatar-circle">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="message-content">
                        <div class="consultant-name">Enterprise Security Consultant</div>
                        <div class="welcome-text">
                            <strong>Welcome to Enterprise Scanner!</strong><br>
                            I'm here to help with your cybersecurity assessment needs. 
                            As a Fortune 500 focused platform, we provide enterprise-grade 
                            vulnerability management solutions.<br><br>
                            <strong>How can I assist you today?</strong>
                        </div>
                        <div class="message-time">${this.formatTime(new Date())}</div>
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typing-indicator" style="display: none;">
                <div class="consultant-avatar">
                    <div class="avatar-circle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                        </svg>
                    </div>
                </div>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span class="typing-text">Consultant is typing...</span>
            </div>
            
            <div class="quick-actions" id="quick-actions">
                <div class="quick-actions-header">Quick Actions:</div>
                <div class="quick-buttons">
                    <button class="quick-btn" data-action="demo">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M15,7V3H9V7H3V21H21V7H15M11,5H13V7H11V5M7,10H9V12H7V10M15,10H17V12H15V10M7,14H9V16H7V14M15,14H17V16H15V14M7,18H9V20H7V18M11,18H13V20H11V18M15,18H17V20H15V18M11,10H13V12H11V10M11,14H13V16H11V14Z"/>
                        </svg>
                        Schedule Demo
                    </button>
                    <button class="quick-btn" data-action="roi">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M7,10H12V15H7V10M19,19H5V8H19M19,3H18V1H16V3H8V1H6V3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3Z"/>
                        </svg>
                        ROI Calculator
                    </button>
                    <button class="quick-btn" data-action="assessment">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/>
                        </svg>
                        Security Assessment
                    </button>
                    <button class="quick-btn" data-action="pricing">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M7,15H9C9,16.08 10.37,17 12,17C13.63,17 15,16.08 15,15C15,13.9 13.96,13.5 11.76,12.97C9.64,12.44 7,11.78 7,9C7,7.21 8.47,5.69 10.5,5.18V3H13.5V5.18C15.53,5.69 17,7.21 17,9H15C15,7.92 13.63,7 12,7C10.37,7 9,7.92 9,9C9,10.1 10.04,10.5 12.24,11.03C14.36,11.56 17,12.22 17,15C17,16.79 15.53,18.31 13.5,18.82V21H10.5V18.82C8.47,18.31 7,16.79 7,15Z"/>
                        </svg>
                        Enterprise Pricing
                    </button>
                </div>
            </div>
            
            <div class="chat-input-area">
                <div class="file-upload" id="file-upload" style="display: none;">
                    <input type="file" id="file-input" accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg">
                    <label for="file-input" class="file-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                        </svg>
                    </label>
                </div>
                <div class="input-container">
                    <input type="text" id="chat-input" placeholder="Type your message..." maxlength="1000" autocomplete="off">
                    <button id="send-message" class="send-btn" disabled>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="chat-footer">
                <div class="security-notice">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,7.6 15.8,8.6C16.8,9.6 17.4,11 17.4,12.4C17.4,13.8 16.8,15.2 15.8,16.2C14.8,17.2 13.4,17.8 12,17.8C10.6,17.8 9.2,17.2 8.2,16.2C7.2,15.2 6.6,13.8 6.6,12.4C6.6,11 7.2,9.6 8.2,8.6C9.2,7.6 10.6,7 12,7Z"/>
                    </svg>
                    <small>Powered by Enterprise Scanner • End-to-end encrypted</small>
                </div>
                <div class="powered-by">
                    <a href="https://enterprisescanner.com" target="_blank">Enterprise Scanner</a>
                </div>
            </div>
        `;

        // Create satisfaction survey modal
        const surveyModal = document.createElement('div');
        surveyModal.id = 'chat-survey-modal';
        surveyModal.innerHTML = `
            <div class="survey-overlay"></div>
            <div class="survey-content">
                <h4>How was your experience?</h4>
                <p>Please rate our enterprise support service:</p>
                <div class="rating-stars">
                    <span class="star" data-rating="1">⭐</span>
                    <span class="star" data-rating="2">⭐</span>
                    <span class="star" data-rating="3">⭐</span>
                    <span class="star" data-rating="4">⭐</span>
                    <span class="star" data-rating="5">⭐</span>
                </div>
                <textarea id="feedback-text" placeholder="Additional feedback (optional)"></textarea>
                <div class="survey-actions">
                    <button id="skip-survey" class="btn-secondary">Skip</button>
                    <button id="submit-survey" class="btn-primary">Submit</button>
                </div>
            </div>
        `;

        document.body.appendChild(chatButton);
        document.body.appendChild(chatWindow);
        document.body.appendChild(surveyModal);
    }

    attachEventListeners() {
        // Chat button toggle
        document.getElementById('enterprise-chat-button').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.getElementById('close-chat').addEventListener('click', () => {
            this.showSatisfactionSurvey();
        });

        // Minimize chat
        document.getElementById('minimize-chat').addEventListener('click', () => {
            this.minimizeChat();
        });

        // Send message
        document.getElementById('send-message').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input validation and typing indicator
        const chatInput = document.getElementById('chat-input');
        chatInput.addEventListener('input', () => {
            this.validateInput();
            this.handleTyping();
        });

        chatInput.addEventListener('focus', () => {
            this.hideQuickActions();
        });

        // Quick actions
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.dataset.action);
            });
        });

        // File upload
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Satisfaction survey
        document.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', (e) => {
                this.setRating(parseInt(e.target.dataset.rating));
            });
        });

        document.getElementById('submit-survey').addEventListener('click', () => {
            this.submitSurvey();
        });

        document.getElementById('skip-survey').addEventListener('click', () => {
            this.closeChatFinal();
        });

        // Prevent accidental page unload during active chat
        window.addEventListener('beforeunload', (e) => {
            if (this.isOpen && this.messages.length > 1) {
                e.preventDefault();
                e.returnValue = 'You have an active chat session. Are you sure you want to leave?';
            }
        });
    }

    loadUserInfo() {
        // Detect user information from page context
        this.userInfo = {
            page_url: window.location.href,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            screen_resolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };

        // Try to extract user info from forms or existing data
        const emailInputs = document.querySelectorAll('input[type="email"]');
        const nameInputs = document.querySelectorAll('input[name*="name"], input[id*="name"]');
        const companyInputs = document.querySelectorAll('input[name*="company"], input[id*="company"]');

        if (emailInputs.length > 0 && emailInputs[0].value) {
            this.userInfo.email = emailInputs[0].value;
        }
        if (nameInputs.length > 0 && nameInputs[0].value) {
            this.userInfo.name = nameInputs[0].value;
        }
        if (companyInputs.length > 0 && companyInputs[0].value) {
            this.userInfo.company = companyInputs[0].value;
        }
    }

    async initializeWebSocket() {
        try {
            // Try to establish WebSocket connection
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('Chat WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
            };
            
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleServerMessage(data);
            };
            
            this.socket.onclose = () => {
                console.log('Chat WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.attemptReconnect();
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.log('WebSocket not available, using HTTP fallback');
            this.updateConnectionStatus('http_fallback');
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts && this.isOpen) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, Math.pow(2, this.reconnectAttempts) * 1000); // Exponential backoff
        }
    }

    updateConnectionStatus(status) {
        const statusIndicator = document.getElementById('connection-status');
        const statusText = document.getElementById('status-text');
        
        switch (status) {
            case 'connected':
                statusIndicator.className = 'status-indicator online';
                statusText.textContent = 'Online - Avg response: 2 min';
                break;
            case 'disconnected':
                statusIndicator.className = 'status-indicator offline';
                statusText.textContent = 'Reconnecting...';
                break;
            case 'error':
                statusIndicator.className = 'status-indicator error';
                statusText.textContent = 'Connection issues';
                break;
            case 'http_fallback':
                statusIndicator.className = 'status-indicator warning';
                statusText.textContent = 'Online (HTTP mode)';
                break;
        }
    }

    startHeartbeat() {
        // Send periodic heartbeat to maintain connection
        setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                }));
            }
        }, 30000); // Every 30 seconds
    }

    toggleChat() {
        if (this.isOpen) {
            this.minimizeChat();
        } else {
            this.openChat();
        }
    }

    async openChat() {
        const chatWindow = document.getElementById('enterprise-chat-window');
        const chatButton = document.getElementById('enterprise-chat-button');
        
        chatWindow.classList.add('open');
        chatButton.classList.add('active');
        this.isOpen = true;
        
        // Start chat session if not already started
        if (!this.chatId) {
            await this.startChatSession();
        }
        
        // Track engagement
        this.trackEvent('chat_opened', {
            page_url: window.location.href,
            user_type: this.detectUserType()
        });
        
        // Focus input after animation
        setTimeout(() => {
            const input = document.getElementById('chat-input');
            if (input) {
                input.focus();
            }
        }, 300);

        // Mark notifications as read
        this.clearNotifications();
    }

    minimizeChat() {
        const chatWindow = document.getElementById('enterprise-chat-window');
        const chatButton = document.getElementById('enterprise-chat-button');
        
        chatWindow.classList.remove('open');
        chatButton.classList.remove('active');
        this.isOpen = false;
        
        this.trackEvent('chat_minimized');
    }

    showSatisfactionSurvey() {
        if (this.messages.length > 1) {
            document.getElementById('chat-survey-modal').style.display = 'flex';
        } else {
            this.closeChatFinal();
        }
    }

    async startChatSession() {
        try {
            const response = await fetch('/api/chat/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.userInfo)
            });
            
            if (!response.ok) {
                throw new Error('Failed to start chat session');
            }
            
            const data = await response.json();
            this.chatId = data.chat_id;
            this.userId = data.user_id;
            
            // Join WebSocket room if connected
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'join_chat',
                    chat_id: this.chatId
                }));
            }
            
            console.log('Chat session started:', this.chatId);
            
        } catch (error) {
            console.error('Failed to start chat session:', error);
            this.addMessage(
                "I'm having trouble connecting right now. Please email us at <a href='mailto:sales@enterprisescanner.com'>sales@enterprisescanner.com</a> for immediate assistance.",
                'consultant'
            );
        }
    }

    validateInput() {
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-message');
        const message = input.value.trim();
        
        sendBtn.disabled = message.length === 0;
        
        // Character count warning
        if (message.length > 800) {
            input.style.borderColor = '#f39c12';
        } else {
            input.style.borderColor = '';
        }
    }

    handleTyping() {
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Send typing indicator
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'typing',
                chat_id: this.chatId,
                typing: true
            }));
        }
        
        // Stop typing after 3 seconds
        this.typingTimeout = setTimeout(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'typing',
                    chat_id: this.chatId,
                    typing: false
                }));
            }
        }, 3000);
    }

    hideQuickActions() {
        const quickActions = document.getElementById('quick-actions');
        if (this.messages.length > 0) {
            quickActions.style.display = 'none';
        }
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && this.chatId) {
            this.addMessage(message, 'user');
            input.value = '';
            this.validateInput();
            
            // Send via WebSocket if available, otherwise HTTP
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'send_message',
                    chat_id: this.chatId,
                    message: message
                }));
            } else {
                this.sendViaAPI(message);
            }
            
            // Hide quick actions after first message
            this.hideQuickActions();
            
            // Show typing indicator
            this.showTypingIndicator();
        }
    }

    addMessage(content, sender, isTemplate = false, timestamp = null) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-bubble user-bubble">
                    <div class="message-content">${this.escapeHtml(content)}</div>
                    <div class="message-time">${this.formatTime(timestamp || new Date())}</div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="consultant-avatar">
                    <div class="avatar-circle">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                        </svg>
                    </div>
                </div>
                <div class="message-bubble consultant-bubble">
                    <div class="consultant-name">Security Consultant</div>
                    <div class="message-content">${content}</div>
                    <div class="message-time">${this.formatTime(timestamp || new Date())}</div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Hide typing indicator when new message arrives
        this.hideTypingIndicator();
        
        // Show notification if chat is minimized
        if (!this.isOpen && sender === 'consultant') {
            this.showNotification();
        }
        
        this.messages.push({
            content,
            sender,
            timestamp: timestamp || new Date(),
            isTemplate
        });
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'flex';
        
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'none';
    }

    showNotification() {
        const notification = document.getElementById('chat-notification');
        notification.style.display = 'block';
        
        // Play notification sound if available
        if (this.notificationSound) {
            this.notificationSound.play().catch(() => {
                // Ignore autoplay restrictions
            });
        }
    }

    clearNotifications() {
        const notification = document.getElementById('chat-notification');
        notification.style.display = 'none';
    }

    handleQuickAction(action) {
        const actionMessages = {
            demo: "I'd like to schedule a demo to see how Enterprise Scanner can help secure our organization.",
            roi: "Can you help me calculate the ROI for implementing Enterprise Scanner?",
            assessment: "I'd like to start a security assessment for our organization.",
            pricing: "What are your enterprise pricing options for large organizations?"
        };

        if (actionMessages[action]) {
            this.addMessage(actionMessages[action], 'user');
            this.sendToServer(`QUICK_ACTION_${action.toUpperCase()}`);
            this.hideQuickActions();
        }
    }

    async handleFileUpload(file) {
        if (!file) return;

        // Validate file
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['application/pdf', 'text/plain', 'image/png', 'image/jpeg'];

        if (file.size > maxSize) {
            alert('File size must be less than 10MB');
            return;
        }

        if (!allowedTypes.includes(file.type)) {
            alert('Only PDF, text, and image files are allowed');
            return;
        }

        try {
            // Show upload progress
            this.addMessage(`📎 Uploading ${file.name}...`, 'user');

            const formData = new FormData();
            formData.append('file', file);
            formData.append('chat_id', this.chatId);

            const response = await fetch('/api/chat/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.addMessage(`📎 File uploaded: ${file.name}`, 'user');
                
                // Send notification to consultant
                this.sendToServer(`FILE_UPLOADED: ${file.name}`);
            } else {
                throw new Error('Upload failed');
            }

        } catch (error) {
            console.error('File upload error:', error);
            this.addMessage('❌ File upload failed. Please try again.', 'consultant');
        }
    }

    setRating(rating) {
        this.satisfactionRating = rating;
        
        // Update star display
        document.querySelectorAll('.star').forEach((star, index) => {
            star.style.opacity = index < rating ? '1' : '0.3';
        });
    }

    async submitSurvey() {
        try {
            const feedback = document.getElementById('feedback-text').value;
            
            const response = await fetch('/api/chat/close', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    chat_id: this.chatId,
                    satisfaction_rating: this.satisfactionRating,
                    feedback: feedback
                })
            });

            if (response.ok) {
                this.addMessage('Thank you for your feedback! 🙏', 'consultant');
            }

        } catch (error) {
            console.error('Failed to submit survey:', error);
        }

        this.closeChatFinal();
    }

    closeChatFinal() {
        document.getElementById('chat-survey-modal').style.display = 'none';
        this.minimizeChat();
        
        // Show thank you message
        setTimeout(() => {
            this.addMessage(
                'Thank you for chatting with Enterprise Scanner! For continued support, email us at <a href="mailto:sales@enterprisescanner.com">sales@enterprisescanner.com</a>',
                'consultant'
            );
        }, 500);
    }

    async sendToServer(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'message',
                content: message,
                chat_id: this.chatId,
                timestamp: new Date().toISOString(),
                user_info: this.userInfo
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
                    chat_id: this.chatId,
                    user_info: this.userInfo
                })
            });
            
            const data = await response.json();
            
            if (data.response) {
                // Simulate human response time
                setTimeout(() => {
                    this.addMessage(data.response, 'consultant', true);
                }, 1000 + Math.random() * 2000);
            }
            
            if (data.escalate) {
                this.escalateToHuman(data.escalate_reason);
            }
            
        } catch (error) {
            console.error('Chat API error:', error);
            this.addMessage(
                "I'm having trouble connecting right now. Please email us at <a href='mailto:sales@enterprisescanner.com'>sales@enterprisescanner.com</a> for immediate assistance.",
                'consultant'
            );
        }
    }

    handleServerMessage(data) {
        switch (data.type) {
            case 'new_message':
                if (data.message.sender_type !== 'visitor') {
                    this.addMessage(
                        data.message.content,
                        'consultant',
                        false,
                        new Date(data.message.timestamp)
                    );
                }
                break;
                
            case 'user_typing':
                if (data.typing) {
                    this.showTypingIndicator();
                } else {
                    this.hideTypingIndicator();
                }
                break;
                
            case 'agent_joined':
                this.addMessage(
                    '👋 A security consultant has joined the chat and will assist you shortly.',
                    'consultant'
                );
                break;
                
            case 'escalated':
                this.addMessage(
                    '🔄 Your inquiry has been escalated to our senior security team. They will respond within 2 minutes.',
                    'consultant'
                );
                break;
                
            case 'connected':
                console.log('WebSocket connected to chat:', data.chat_id);
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    escalateToHuman(reason) {
        this.addMessage(
            `🔄 I'm connecting you with a senior security consultant who specializes in ${reason}. 
            They'll be with you shortly. In the meantime, you can also reach our enterprise team 
            directly at <a href="mailto:sales@enterprisescanner.com">sales@enterprisescanner.com</a>.`,
            'consultant'
        );
        
        // Send escalation notification
        fetch('/api/chat/escalate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: this.chatId,
                reason: reason,
                messages: this.messages,
                user_info: this.userInfo
            })
        });
    }

    detectUserType() {
        const url = window.location.href.toLowerCase();
        const email = this.userInfo.email || '';
        
        if (email.includes('gmail') || email.includes('yahoo') || email.includes('hotmail')) {
            return 'personal';
        } else if (email && email.includes('@')) {
            return 'business';
        } else if (url.includes('enterprise') || url.includes('pricing')) {
            return 'enterprise_prospect';
        } else {
            return 'visitor';
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

        // Load notification sound
        try {
            this.notificationSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmUiBlat4+6OU');
        } catch (e) {
            // Ignore if audio creation fails
        }
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
                event_category: 'enterprise_chat',
                ...data
            });
        }

        // Custom analytics
        if (typeof analytics !== 'undefined') {
            analytics.track(event, {
                category: 'enterprise_chat',
                chat_id: this.chatId,
                user_type: this.detectUserType(),
                ...data
            });
        }
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enterpriseChat = new EnterpriseChat();
});