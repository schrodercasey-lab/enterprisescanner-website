/**
 * Connection Monitor
 * ==================
 * 
 * Real-time connection status monitoring
 * Features: WebSocket status, auto-reconnect, visual indicators, connection health
 * 
 * Usage:
 *   const monitor = new ConnectionMonitor(socket);
 *   monitor.onStatusChange((status) => console.log(status));
 */

class ConnectionMonitor {
    constructor(socket) {
        this.socket = socket;
        this.status = 'disconnected';
        this.pingInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.lastPingTime = null;
        this.latency = null;
        this.statusCallbacks = [];
        this.indicator = null;
        
        this.init();
    }

    init() {
        this.createIndicator();
        this.attachSocketListeners();
        this.startPingMonitor();
    }

    createIndicator() {
        // Create connection status indicator
        this.indicator = document.createElement('div');
        this.indicator.id = 'connection-indicator';
        this.indicator.className = 'fixed bottom-4 left-4 z-50';
        this.indicator.innerHTML = `
            <div class="connection-status-card bg-slate-800/90 backdrop-blur-sm rounded-lg shadow-lg p-3 border border-slate-700 flex items-center space-x-3">
                <div class="status-dot"></div>
                <div class="flex-1">
                    <div class="status-text text-sm font-medium text-slate-200"></div>
                    <div class="status-detail text-xs text-slate-400 mt-0.5"></div>
                </div>
                <button class="status-action hidden text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors">
                    Reconnect
                </button>
            </div>
        `;

        document.body.appendChild(this.indicator);

        // Add reconnect button handler
        const actionBtn = this.indicator.querySelector('.status-action');
        actionBtn.addEventListener('click', () => this.reconnect());

        // Initially hide
        setTimeout(() => {
            this.indicator.style.display = 'none';
        }, 3000);
    }

    attachSocketListeners() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            this.onConnect();
        });

        this.socket.on('disconnect', (reason) => {
            this.onDisconnect(reason);
        });

        this.socket.on('connect_error', (error) => {
            this.onError(error);
        });

        this.socket.on('reconnect', (attemptNumber) => {
            this.onReconnect(attemptNumber);
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            this.onReconnectAttempt(attemptNumber);
        });

        this.socket.on('reconnect_error', (error) => {
            this.onReconnectError(error);
        });

        this.socket.on('reconnect_failed', () => {
            this.onReconnectFailed();
        });

        // Custom pong response
        this.socket.on('pong', (data) => {
            if (this.lastPingTime) {
                this.latency = Date.now() - this.lastPingTime;
                this.updateLatencyDisplay();
            }
        });
    }

    startPingMonitor() {
        this.pingInterval = setInterval(() => {
            if (this.status === 'connected') {
                this.lastPingTime = Date.now();
                this.socket.emit('ping');
            }
        }, 5000); // Ping every 5 seconds
    }

    onConnect() {
        console.log('✅ Connected to server');
        this.status = 'connected';
        this.reconnectAttempts = 0;
        this.updateIndicator();
        this.notifyStatusChange();
        showSuccess('Connected to server', 3000);
    }

    onDisconnect(reason) {
        console.log('❌ Disconnected:', reason);
        this.status = 'disconnected';
        this.updateIndicator();
        this.notifyStatusChange();
        
        if (reason === 'io server disconnect') {
            // Server initiated disconnect
            showError('Server disconnected. Please refresh the page.', 0, {
                action: () => window.location.reload(),
                actionLabel: 'Refresh'
            });
        } else {
            // Client disconnect or network issue
            showWarning('Connection lost. Attempting to reconnect...', 0);
        }
    }

    onError(error) {
        console.error('❌ Connection error:', error);
        this.status = 'error';
        this.updateIndicator();
        this.notifyStatusChange();
    }

    onReconnect(attemptNumber) {
        console.log('🔄 Reconnected after', attemptNumber, 'attempts');
        this.status = 'connected';
        this.reconnectAttempts = 0;
        this.updateIndicator();
        this.notifyStatusChange();
        showSuccess('Reconnected successfully!', 3000);
    }

    onReconnectAttempt(attemptNumber) {
        console.log('🔄 Reconnect attempt', attemptNumber);
        this.reconnectAttempts = attemptNumber;
        this.status = 'reconnecting';
        this.updateIndicator();
        this.notifyStatusChange();
    }

    onReconnectError(error) {
        console.error('❌ Reconnect error:', error);
        this.status = 'reconnecting';
        this.updateIndicator();
    }

    onReconnectFailed() {
        console.error('❌ Reconnect failed');
        this.status = 'failed';
        this.updateIndicator();
        this.notifyStatusChange();
        
        showError('Unable to reconnect. Please check your connection.', 0, {
            action: () => this.reconnect(),
            actionLabel: 'Try Again'
        });
    }

    reconnect() {
        console.log('🔄 Manual reconnect triggered');
        if (this.socket) {
            this.socket.disconnect();
            setTimeout(() => {
                this.socket.connect();
            }, 1000);
        }
    }

    updateIndicator() {
        if (!this.indicator) return;

        const dot = this.indicator.querySelector('.status-dot');
        const text = this.indicator.querySelector('.status-text');
        const detail = this.indicator.querySelector('.status-detail');
        const action = this.indicator.querySelector('.status-action');

        // Show indicator when not connected
        if (this.status !== 'connected') {
            this.indicator.style.display = 'block';
        }

        switch (this.status) {
            case 'connected':
                dot.className = 'status-dot w-2 h-2 rounded-full bg-green-500 animate-pulse';
                text.textContent = 'Connected';
                detail.textContent = this.latency ? `Latency: ${this.latency}ms` : 'Real-time updates active';
                action.classList.add('hidden');
                
                // Hide after 3 seconds if connected
                setTimeout(() => {
                    if (this.status === 'connected') {
                        this.indicator.style.display = 'none';
                    }
                }, 3000);
                break;

            case 'disconnected':
                dot.className = 'status-dot w-2 h-2 rounded-full bg-red-500';
                text.textContent = 'Disconnected';
                detail.textContent = 'Connection lost';
                action.classList.remove('hidden');
                break;

            case 'reconnecting':
                dot.className = 'status-dot w-2 h-2 rounded-full bg-yellow-500 animate-pulse';
                text.textContent = 'Reconnecting...';
                detail.textContent = `Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`;
                action.classList.add('hidden');
                break;

            case 'error':
                dot.className = 'status-dot w-2 h-2 rounded-full bg-red-500';
                text.textContent = 'Connection Error';
                detail.textContent = 'Unable to connect';
                action.classList.remove('hidden');
                break;

            case 'failed':
                dot.className = 'status-dot w-2 h-2 rounded-full bg-red-500';
                text.textContent = 'Connection Failed';
                detail.textContent = 'All reconnect attempts failed';
                action.classList.remove('hidden');
                break;
        }
    }

    updateLatencyDisplay() {
        if (!this.indicator || this.status !== 'connected') return;

        const detail = this.indicator.querySelector('.status-detail');
        if (detail && this.latency !== null) {
            detail.textContent = `Latency: ${this.latency}ms`;
        }
    }

    onStatusChange(callback) {
        if (typeof callback === 'function') {
            this.statusCallbacks.push(callback);
        }
    }

    notifyStatusChange() {
        const statusData = {
            status: this.status,
            latency: this.latency,
            reconnectAttempts: this.reconnectAttempts
        };

        this.statusCallbacks.forEach(callback => {
            try {
                callback(statusData);
            } catch (error) {
                console.error('Status callback error:', error);
            }
        });
    }

    getStatus() {
        return {
            status: this.status,
            latency: this.latency,
            reconnectAttempts: this.reconnectAttempts,
            connected: this.status === 'connected'
        };
    }

    destroy() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        if (this.indicator && this.indicator.parentNode) {
            this.indicator.parentNode.removeChild(this.indicator);
        }
    }
}

// Export for global use
window.ConnectionMonitor = ConnectionMonitor;
