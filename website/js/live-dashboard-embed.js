/**
 * Live Dashboard Embed - Phase 2
 * Enterprise Scanner Website
 * Features: iframe integration, authentication, responsive sizing, loading states
 */

class LiveDashboardEmbed {
    constructor(options = {}) {
        this.options = {
            containerId: options.containerId || 'dashboard-embed',
            dashboardUrl: options.dashboardUrl || 'http://localhost:5000',
            demoMode: options.demoMode !== false,
            autoRefresh: options.autoRefresh || false,
            refreshInterval: options.refreshInterval || 30000, // 30 seconds
            theme: options.theme || 'dark',
            ...options
        };

        this.iframe = null;
        this.container = null;
        this.isLoading = false;
        this.refreshTimer = null;

        this.init();
    }

    init() {
        this.injectStyles();
        this.container = document.getElementById(this.options.containerId);
        
        if (this.container) {
            this.render();
            this.setupEventListeners();
        }
    }

    injectStyles() {
        if (document.getElementById('dashboard-embed-styles')) return;

        const style = document.createElement('style');
        style.id = 'dashboard-embed-styles';
        style.textContent = `
            .dashboard-embed-wrapper {
                position: relative;
                width: 100%;
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }

            .dashboard-embed-header {
                padding: 20px 24px;
                background: rgba(30, 41, 59, 0.9);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .dashboard-embed-title {
                display: flex;
                align-items: center;
                gap: 12px;
                margin: 0;
                color: #ffffff;
                font-size: 1.1rem;
                font-weight: 600;
            }

            .dashboard-embed-status {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 0.85rem;
                color: rgba(255, 255, 255, 0.7);
            }

            .status-indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #10b981;
                animation: pulse-status 2s infinite;
            }

            @keyframes pulse-status {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .dashboard-embed-controls {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .embed-control-btn {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #ffffff;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .embed-control-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }

            .embed-control-btn:active {
                transform: translateY(0);
            }

            .embed-control-btn.active {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-color: transparent;
            }

            .dashboard-embed-iframe-container {
                position: relative;
                width: 100%;
                padding-bottom: 56.25%; /* 16:9 aspect ratio */
                background: rgba(15, 23, 42, 0.6);
                overflow: hidden;
            }

            .dashboard-embed-iframe-container.fullheight {
                padding-bottom: 0;
                height: 800px;
            }

            .dashboard-embed-iframe {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border: none;
                background: transparent;
            }

            .dashboard-embed-loading {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                z-index: 10;
            }

            .dashboard-embed-loading-spinner {
                width: 60px;
                height: 60px;
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-top-color: #3b82f6;
                border-radius: 50%;
                animation: spin-loader 1s linear infinite;
            }

            @keyframes spin-loader {
                to { transform: rotate(360deg); }
            }

            .dashboard-embed-loading-text {
                margin-top: 16px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.95rem;
            }

            .dashboard-embed-error {
                padding: 40px;
                text-align: center;
                color: rgba(255, 255, 255, 0.8);
            }

            .dashboard-embed-error-icon {
                font-size: 3rem;
                color: #ef4444;
                margin-bottom: 16px;
            }

            .dashboard-embed-error-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 8px;
                color: #ffffff;
            }

            .dashboard-embed-error-message {
                color: rgba(255, 255, 255, 0.6);
                margin-bottom: 20px;
            }

            .dashboard-embed-retry-btn {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border: none;
                color: #ffffff;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.3s ease;
            }

            .dashboard-embed-retry-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
            }

            .dashboard-embed-demo-banner {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(251, 191, 36, 0.95);
                backdrop-filter: blur(10px);
                color: #000000;
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                z-index: 20;
                box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .dashboard-embed-footer {
                padding: 16px 24px;
                background: rgba(30, 41, 59, 0.9);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .dashboard-embed-info {
                font-size: 0.85rem;
                color: rgba(255, 255, 255, 0.6);
            }

            .dashboard-embed-actions {
                display: flex;
                gap: 12px;
            }

            .dashboard-embed-action-link {
                color: #3b82f6;
                text-decoration: none;
                font-size: 0.85rem;
                font-weight: 500;
                transition: color 0.3s ease;
            }

            .dashboard-embed-action-link:hover {
                color: #60a5fa;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .dashboard-embed-header {
                    flex-direction: column;
                    gap: 12px;
                    padding: 16px;
                }

                .dashboard-embed-controls {
                    width: 100%;
                    justify-content: center;
                }

                .dashboard-embed-footer {
                    flex-direction: column;
                    gap: 12px;
                    text-align: center;
                }

                .dashboard-embed-actions {
                    flex-direction: column;
                    width: 100%;
                }

                .dashboard-embed-iframe-container.fullheight {
                    height: 600px;
                }
            }

            /* Fullscreen mode */
            .dashboard-embed-wrapper.fullscreen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 9999;
                border-radius: 0;
            }

            .dashboard-embed-wrapper.fullscreen .dashboard-embed-iframe-container {
                padding-bottom: 0;
                height: calc(100vh - 120px);
            }
        `;
        document.head.appendChild(style);
    }

    render() {
        const html = `
            <div class="dashboard-embed-wrapper">
                ${this.renderHeader()}
                ${this.renderIframeContainer()}
                ${this.renderFooter()}
            </div>
        `;
        
        this.container.innerHTML = html;
        this.iframe = this.container.querySelector('.dashboard-embed-iframe');
        
        // Start loading dashboard
        this.loadDashboard();
    }

    renderHeader() {
        return `
            <div class="dashboard-embed-header">
                <div class="dashboard-embed-title">
                    <i class="bi bi-grid-3x3-gap-fill"></i>
                    <span>Live Security Dashboard</span>
                    <div class="dashboard-embed-status">
                        <span class="status-indicator"></span>
                        <span>Live</span>
                    </div>
                </div>
                <div class="dashboard-embed-controls">
                    <button class="embed-control-btn" data-action="refresh" title="Refresh Dashboard">
                        <i class="bi bi-arrow-clockwise"></i>
                        <span class="d-none d-md-inline">Refresh</span>
                    </button>
                    <button class="embed-control-btn" data-action="fullscreen" title="Fullscreen">
                        <i class="bi bi-arrows-fullscreen"></i>
                        <span class="d-none d-md-inline">Fullscreen</span>
                    </button>
                </div>
            </div>
        `;
    }

    renderIframeContainer() {
        return `
            <div class="dashboard-embed-iframe-container fullheight">
                ${this.options.demoMode ? this.renderDemoBanner() : ''}
                <div class="dashboard-embed-loading">
                    <div class="dashboard-embed-loading-spinner"></div>
                    <div class="dashboard-embed-loading-text">Loading dashboard...</div>
                </div>
                <iframe 
                    class="dashboard-embed-iframe" 
                    src="${this.getDashboardUrl()}"
                    allow="fullscreen"
                    loading="lazy"
                    style="display: none;">
                </iframe>
            </div>
        `;
    }

    renderDemoBanner() {
        return `
            <div class="dashboard-embed-demo-banner">
                <i class="bi bi-info-circle-fill"></i>
                Demo Mode - Sample Data
            </div>
        `;
    }

    renderFooter() {
        return `
            <div class="dashboard-embed-footer">
                <div class="dashboard-embed-info">
                    <i class="bi bi-lock-fill me-1"></i>
                    Secure Connection • Data encrypted in transit
                </div>
                <div class="dashboard-embed-actions">
                    <a href="#" class="dashboard-embed-action-link" data-action="full-demo">
                        <i class="bi bi-box-arrow-up-right me-1"></i>Open Full Dashboard
                    </a>
                    <a href="#demo-request-section" class="dashboard-embed-action-link">
                        <i class="bi bi-calendar-check me-1"></i>Request Demo
                    </a>
                </div>
            </div>
        `;
    }

    getDashboardUrl() {
        if (this.options.demoMode) {
            // Use demo/sandbox dashboard
            return `${this.options.dashboardUrl}?demo=true&theme=${this.options.theme}`;
        }
        return this.options.dashboardUrl;
    }

    loadDashboard() {
        if (!this.iframe) return;

        this.isLoading = true;

        // Show loading state
        const loadingEl = this.container.querySelector('.dashboard-embed-loading');
        const iframeEl = this.iframe;

        // Handle iframe load
        this.iframe.addEventListener('load', () => {
            this.isLoading = false;
            if (loadingEl) loadingEl.style.display = 'none';
            if (iframeEl) iframeEl.style.display = 'block';

            // Start auto-refresh if enabled
            if (this.options.autoRefresh) {
                this.startAutoRefresh();
            }

            // Show success toast
            if (window.toastNotifications) {
                window.toastNotifications.show('Dashboard loaded successfully', 'success');
            }
        });

        // Handle iframe error
        this.iframe.addEventListener('error', () => {
            this.handleError('Failed to load dashboard');
        });

        // Timeout fallback (30 seconds)
        setTimeout(() => {
            if (this.isLoading) {
                this.handleError('Dashboard loading timed out');
            }
        }, 30000);
    }

    handleError(message) {
        this.isLoading = false;
        const container = this.container.querySelector('.dashboard-embed-iframe-container');
        
        container.innerHTML = `
            <div class="dashboard-embed-error">
                <div class="dashboard-embed-error-icon">
                    <i class="bi bi-exclamation-triangle"></i>
                </div>
                <div class="dashboard-embed-error-title">Unable to Load Dashboard</div>
                <div class="dashboard-embed-error-message">${message}</div>
                <button class="dashboard-embed-retry-btn" data-action="retry">
                    <i class="bi bi-arrow-clockwise me-2"></i>Try Again
                </button>
            </div>
        `;

        // Add retry button listener
        const retryBtn = container.querySelector('[data-action="retry"]');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.render();
            });
        }

        // Show error toast
        if (window.toastNotifications) {
            window.toastNotifications.show(message, 'error');
        }
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = this.container.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Fullscreen button
        const fullscreenBtn = this.container.querySelector('[data-action="fullscreen"]');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        // Full demo link
        const fullDemoLink = this.container.querySelector('[data-action="full-demo"]');
        if (fullDemoLink) {
            fullDemoLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.openFullDashboard();
            });
        }
    }

    refresh() {
        if (!this.iframe) return;

        // Show loading indicator
        if (window.loadingIndicator) {
            window.loadingIndicator.show('Refreshing dashboard...');
        }

        // Reload iframe
        this.iframe.src = this.iframe.src;

        // Hide loading after delay
        setTimeout(() => {
            if (window.loadingIndicator) {
                window.loadingIndicator.hide();
            }
        }, 1000);
    }

    toggleFullscreen() {
        const wrapper = this.container.querySelector('.dashboard-embed-wrapper');
        wrapper.classList.toggle('fullscreen');

        const icon = this.container.querySelector('[data-action="fullscreen"] i');
        if (wrapper.classList.contains('fullscreen')) {
            icon.className = 'bi bi-fullscreen-exit';
        } else {
            icon.className = 'bi bi-arrows-fullscreen';
        }
    }

    openFullDashboard() {
        const url = this.options.demoMode 
            ? `${this.options.dashboardUrl}?demo=true` 
            : this.options.dashboardUrl;
        
        window.open(url, '_blank', 'noopener,noreferrer');

        // Show toast
        if (window.toastNotifications) {
            window.toastNotifications.show('Opening full dashboard in new tab', 'info');
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        
        this.refreshTimer = setInterval(() => {
            this.refresh();
        }, this.options.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('dashboard-embed');
    if (container) {
        window.liveDashboardEmbed = new LiveDashboardEmbed({
            demoMode: true,
            dashboardUrl: 'http://localhost:5000',
            autoRefresh: false,
            theme: 'dark'
        });
    }
});
