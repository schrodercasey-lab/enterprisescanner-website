/**
 * Loading Indicator System - Ported from Jupiter Dashboard
 * Enterprise Scanner Website
 * Provides elegant loading indicators with multiple styles
 */

class LoadingIndicatorSystem {
    constructor(options = {}) {
        this.options = {
            style: options.style || 'spinner', // spinner, dots, pulse, bar
            size: options.size || 'medium', // small, medium, large
            color: options.color || 'primary',
            overlay: options.overlay !== false,
            message: options.message || 'Loading...',
            ...options
        };
        
        this.activeIndicators = new Map();
        this.init();
    }

    init() {
        this.injectStyles();
    }

    injectStyles() {
        if (document.getElementById('loading-indicator-styles')) return;

        const style = document.createElement('style');
        style.id = 'loading-indicator-styles';
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(5px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .loading-overlay.active {
                opacity: 1;
            }

            .loading-inline {
                display: inline-flex;
                align-items: center;
                gap: 12px;
            }

            .loading-container {
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 32px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
                min-width: 200px;
            }

            .loading-message {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                text-align: center;
                margin: 0;
            }

            /* Spinner Style */
            .loading-spinner {
                width: 48px;
                height: 48px;
                border: 4px solid rgba(59, 130, 246, 0.2);
                border-top-color: #3b82f6;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }

            .loading-spinner.size-small {
                width: 24px;
                height: 24px;
                border-width: 2px;
            }

            .loading-spinner.size-large {
                width: 64px;
                height: 64px;
                border-width: 5px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Dots Style */
            .loading-dots {
                display: flex;
                gap: 8px;
                align-items: center;
            }

            .loading-dot {
                width: 12px;
                height: 12px;
                background: #3b82f6;
                border-radius: 50%;
                animation: dotPulse 1.4s ease-in-out infinite;
            }

            .loading-dots.size-small .loading-dot {
                width: 8px;
                height: 8px;
            }

            .loading-dots.size-large .loading-dot {
                width: 16px;
                height: 16px;
            }

            .loading-dot:nth-child(1) { animation-delay: 0s; }
            .loading-dot:nth-child(2) { animation-delay: 0.2s; }
            .loading-dot:nth-child(3) { animation-delay: 0.4s; }

            @keyframes dotPulse {
                0%, 80%, 100% {
                    transform: scale(0.6);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            /* Pulse Style */
            .loading-pulse {
                width: 48px;
                height: 48px;
                background: #3b82f6;
                border-radius: 50%;
                animation: pulse 1.5s ease-in-out infinite;
            }

            .loading-pulse.size-small {
                width: 24px;
                height: 24px;
            }

            .loading-pulse.size-large {
                width: 64px;
                height: 64px;
            }

            @keyframes pulse {
                0%, 100% {
                    transform: scale(0.8);
                    opacity: 0.5;
                }
                50% {
                    transform: scale(1.2);
                    opacity: 1;
                }
            }

            /* Bar Style */
            .loading-bar-container {
                width: 240px;
                height: 4px;
                background: rgba(59, 130, 246, 0.2);
                border-radius: 2px;
                overflow: hidden;
            }

            .loading-bar-container.size-small {
                width: 160px;
                height: 3px;
            }

            .loading-bar-container.size-large {
                width: 320px;
                height: 6px;
            }

            .loading-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                border-radius: 2px;
                animation: barProgress 1.5s ease-in-out infinite;
            }

            @keyframes barProgress {
                0% {
                    transform: translateX(-100%);
                }
                100% {
                    transform: translateX(400%);
                }
            }

            /* Color Variants */
            .loading-spinner.color-success,
            .loading-dot.color-success,
            .loading-pulse.color-success {
                border-top-color: #10b981;
                background: #10b981;
            }

            .loading-bar.color-success {
                background: linear-gradient(90deg, #10b981, #34d399);
            }

            .loading-spinner.color-warning,
            .loading-dot.color-warning,
            .loading-pulse.color-warning {
                border-top-color: #fbbf24;
                background: #fbbf24;
            }

            .loading-bar.color-warning {
                background: linear-gradient(90deg, #fbbf24, #fcd34d);
            }

            .loading-spinner.color-error,
            .loading-dot.color-error,
            .loading-pulse.color-error {
                border-top-color: #ef4444;
                background: #ef4444;
            }

            .loading-bar.color-error {
                background: linear-gradient(90deg, #ef4444, #f87171);
            }

            /* Button Loading State */
            .btn-loading {
                position: relative;
                pointer-events: none;
                color: transparent !important;
            }

            .btn-loading::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.6s linear infinite;
            }

            /* Skeleton Loading */
            .skeleton {
                background: linear-gradient(90deg, 
                    rgba(30, 41, 59, 0.5) 0%, 
                    rgba(51, 65, 85, 0.5) 50%, 
                    rgba(30, 41, 59, 0.5) 100%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: 8px;
            }

            @keyframes shimmer {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .skeleton-text {
                height: 16px;
                margin: 8px 0;
            }

            .skeleton-heading {
                height: 24px;
                margin: 12px 0;
            }

            .skeleton-avatar {
                width: 48px;
                height: 48px;
                border-radius: 50%;
            }

            /* Mobile responsive */
            @media (max-width: 640px) {
                .loading-container {
                    min-width: 160px;
                    padding: 24px;
                }

                .loading-bar-container {
                    width: 200px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show(options = {}) {
        const config = { ...this.options, ...options };
        const id = config.id || Date.now().toString();

        // Remove existing indicator with same ID
        if (this.activeIndicators.has(id)) {
            this.hide(id);
        }

        const indicator = this.createIndicator(config);
        this.activeIndicators.set(id, indicator);

        if (config.target) {
            const target = typeof config.target === 'string' 
                ? document.querySelector(config.target)
                : config.target;
            
            if (target) {
                target.appendChild(indicator.element);
            }
        } else if (config.overlay) {
            document.body.appendChild(indicator.element);
            requestAnimationFrame(() => {
                indicator.element.classList.add('active');
            });
        }

        return id;
    }

    createIndicator(config) {
        const isOverlay = config.overlay && !config.target;
        const element = document.createElement('div');
        element.className = isOverlay ? 'loading-overlay' : 'loading-inline';

        let indicatorHTML = '';

        switch (config.style) {
            case 'spinner':
                indicatorHTML = `<div class="loading-spinner size-${config.size} color-${config.color}"></div>`;
                break;
            
            case 'dots':
                indicatorHTML = `
                    <div class="loading-dots size-${config.size}">
                        <div class="loading-dot color-${config.color}"></div>
                        <div class="loading-dot color-${config.color}"></div>
                        <div class="loading-dot color-${config.color}"></div>
                    </div>
                `;
                break;
            
            case 'pulse':
                indicatorHTML = `<div class="loading-pulse size-${config.size} color-${config.color}"></div>`;
                break;
            
            case 'bar':
                indicatorHTML = `
                    <div class="loading-bar-container size-${config.size}">
                        <div class="loading-bar color-${config.color}"></div>
                    </div>
                `;
                break;
        }

        if (isOverlay) {
            element.innerHTML = `
                <div class="loading-container">
                    ${indicatorHTML}
                    ${config.message ? `<p class="loading-message">${this.escapeHtml(config.message)}</p>` : ''}
                </div>
            `;
        } else {
            element.innerHTML = indicatorHTML;
        }

        return { element, config };
    }

    hide(id) {
        const indicator = this.activeIndicators.get(id);
        if (!indicator) return;

        const element = indicator.element;

        if (element.classList.contains('loading-overlay')) {
            element.classList.remove('active');
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            }, 300);
        } else {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }

        this.activeIndicators.delete(id);
    }

    hideAll() {
        this.activeIndicators.forEach((_, id) => this.hide(id));
    }

    showButtonLoading(button) {
        if (typeof button === 'string') {
            button = document.querySelector(button);
        }
        if (button) {
            button.classList.add('btn-loading');
            button.disabled = true;
        }
    }

    hideButtonLoading(button) {
        if (typeof button === 'string') {
            button = document.querySelector(button);
        }
        if (button) {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    createSkeleton(options = {}) {
        const element = document.createElement('div');
        element.className = 'skeleton';
        
        if (options.type === 'text') {
            element.classList.add('skeleton-text');
        } else if (options.type === 'heading') {
            element.classList.add('skeleton-heading');
        } else if (options.type === 'avatar') {
            element.classList.add('skeleton-avatar');
        }

        if (options.width) element.style.width = options.width;
        if (options.height) element.style.height = options.height;

        return element;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        this.hideAll();
        const styles = document.getElementById('loading-indicator-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Global instance
window.loadingIndicator = new LoadingIndicatorSystem();

// Convenience methods
window.showLoading = (message, options) => {
    return window.loadingIndicator.show({ message, ...options });
};

window.hideLoading = (id) => {
    window.loadingIndicator.hide(id);
};
