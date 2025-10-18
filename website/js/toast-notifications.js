/**
 * Toast Notification System - Ported from Jupiter Dashboard
 * Enterprise Scanner Website
 * Provides elegant toast notifications with animations
 */

class ToastNotificationSystem {
    constructor(options = {}) {
        this.options = {
            position: options.position || 'top-right',
            duration: options.duration || 5000,
            maxToasts: options.maxToasts || 5,
            animation: options.animation || 'slide',
            pauseOnHover: options.pauseOnHover !== false,
            showProgress: options.showProgress !== false,
            ...options
        };
        
        this.toasts = [];
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.injectStyles();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = `toast-container toast-${this.options.position}`;
        this.container.setAttribute('role', 'region');
        this.container.setAttribute('aria-label', 'Notifications');
        document.body.appendChild(this.container);
    }

    injectStyles() {
        if (document.getElementById('toast-notification-styles')) return;

        const style = document.createElement('style');
        style.id = 'toast-notification-styles';
        style.textContent = `
            .toast-container {
                position: fixed;
                z-index: 10000;
                pointer-events: none;
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-width: 420px;
                padding: 20px;
            }

            .toast-top-right { top: 0; right: 0; }
            .toast-top-left { top: 0; left: 0; }
            .toast-bottom-right { bottom: 0; right: 0; flex-direction: column-reverse; }
            .toast-bottom-left { bottom: 0; left: 0; flex-direction: column-reverse; }
            .toast-top-center { top: 0; left: 50%; transform: translateX(-50%); }
            .toast-bottom-center { bottom: 0; left: 50%; transform: translateX(-50%); flex-direction: column-reverse; }

            .toast {
                pointer-events: auto;
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: flex-start;
                gap: 12px;
                position: relative;
                overflow: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                max-width: 100%;
            }

            .toast:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            }

            .toast.toast-success {
                border-left: 3px solid #10b981;
            }

            .toast.toast-error {
                border-left: 3px solid #ef4444;
            }

            .toast.toast-warning {
                border-left: 3px solid #fbbf24;
            }

            .toast.toast-info {
                border-left: 3px solid #3b82f6;
            }

            .toast-icon {
                flex-shrink: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }

            .toast-success .toast-icon { color: #10b981; }
            .toast-error .toast-icon { color: #ef4444; }
            .toast-warning .toast-icon { color: #fbbf24; }
            .toast-info .toast-icon { color: #3b82f6; }

            .toast-content {
                flex: 1;
                min-width: 0;
            }

            .toast-title {
                color: #ffffff;
                font-weight: 600;
                font-size: 14px;
                margin: 0 0 4px 0;
                line-height: 1.4;
            }

            .toast-message {
                color: rgba(255, 255, 255, 0.8);
                font-size: 13px;
                margin: 0;
                line-height: 1.5;
                word-wrap: break-word;
            }

            .toast-close {
                flex-shrink: 0;
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                transition: color 0.2s;
                line-height: 1;
            }

            .toast-close:hover {
                color: rgba(255, 255, 255, 0.9);
            }

            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                transform-origin: left;
                transition: transform linear;
            }

            /* Animations */
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideInLeft {
                from {
                    transform: translateX(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideInDown {
                from {
                    transform: translateY(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            @keyframes slideInUp {
                from {
                    transform: translateY(100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }

            .toast.toast-enter {
                animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .toast-top-left .toast.toast-enter,
            .toast-bottom-left .toast.toast-enter {
                animation: slideInLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .toast-top-center .toast.toast-enter {
                animation: slideInDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .toast-bottom-center .toast.toast-enter {
                animation: slideInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .toast.toast-exit {
                animation: fadeOut 0.2s ease-out forwards;
            }

            /* Mobile responsive */
            @media (max-width: 640px) {
                .toast-container {
                    left: 0 !important;
                    right: 0 !important;
                    max-width: 100%;
                    padding: 16px;
                    transform: none !important;
                }

                .toast {
                    max-width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show(type, title, message, options = {}) {
        // Remove oldest toast if at max capacity
        if (this.toasts.length >= this.options.maxToasts) {
            this.remove(this.toasts[0]);
        }

        const toast = this.createToast(type, title, message, options);
        this.toasts.push(toast);
        this.container.appendChild(toast.element);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.element.classList.add('toast-enter');
        });

        // Auto dismiss
        if (options.duration !== 0) {
            const duration = options.duration || this.options.duration;
            toast.timer = setTimeout(() => this.remove(toast), duration);

            // Progress bar animation
            if (this.options.showProgress && toast.progressBar) {
                toast.progressBar.style.transition = `transform ${duration}ms linear`;
                requestAnimationFrame(() => {
                    toast.progressBar.style.transform = 'scaleX(0)';
                });
            }
        }

        // Pause on hover
        if (this.options.pauseOnHover) {
            toast.element.addEventListener('mouseenter', () => {
                if (toast.timer) {
                    clearTimeout(toast.timer);
                    if (toast.progressBar) {
                        const computedStyle = window.getComputedStyle(toast.progressBar);
                        const matrix = computedStyle.transform;
                        toast.progressBar.style.transition = 'none';
                        toast.progressBar.style.transform = matrix;
                    }
                }
            });

            toast.element.addEventListener('mouseleave', () => {
                const remainingTime = toast.remainingTime || (options.duration || this.options.duration);
                toast.timer = setTimeout(() => this.remove(toast), remainingTime);
                
                if (toast.progressBar) {
                    toast.progressBar.style.transition = `transform ${remainingTime}ms linear`;
                    toast.progressBar.style.transform = 'scaleX(0)';
                }
            });
        }

        return toast;
    }

    createToast(type, title, message, options) {
        const element = document.createElement('div');
        element.className = `toast toast-${type}`;
        element.setAttribute('role', 'alert');
        element.setAttribute('aria-live', 'polite');

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        element.innerHTML = `
            <div class="toast-icon">${icons[type] || 'ℹ'}</div>
            <div class="toast-content">
                <div class="toast-title">${this.escapeHtml(title)}</div>
                ${message ? `<div class="toast-message">${this.escapeHtml(message)}</div>` : ''}
            </div>
            <button class="toast-close" aria-label="Close notification">×</button>
            ${this.options.showProgress ? '<div class="toast-progress"></div>' : ''}
        `;

        const closeBtn = element.querySelector('.toast-close');
        const progressBar = element.querySelector('.toast-progress');

        const toast = {
            id: Date.now(),
            type,
            title,
            message,
            element,
            progressBar,
            timer: null,
            remainingTime: options.duration || this.options.duration
        };

        closeBtn.addEventListener('click', () => this.remove(toast));

        return toast;
    }

    remove(toast) {
        if (toast.timer) {
            clearTimeout(toast.timer);
        }

        toast.element.classList.remove('toast-enter');
        toast.element.classList.add('toast-exit');

        setTimeout(() => {
            if (toast.element.parentNode) {
                toast.element.parentNode.removeChild(toast.element);
            }
            this.toasts = this.toasts.filter(t => t.id !== toast.id);
        }, 200);
    }

    success(title, message, options) {
        return this.show('success', title, message, options);
    }

    error(title, message, options) {
        return this.show('error', title, message, options);
    }

    warning(title, message, options) {
        return this.show('warning', title, message, options);
    }

    info(title, message, options) {
        return this.show('info', title, message, options);
    }

    clear() {
        this.toasts.forEach(toast => this.remove(toast));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        this.clear();
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        const styles = document.getElementById('toast-notification-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Global instance
window.toastNotifications = new ToastNotificationSystem();

// Convenience methods
window.showToast = {
    success: (title, message, options) => window.toastNotifications.success(title, message, options),
    error: (title, message, options) => window.toastNotifications.error(title, message, options),
    warning: (title, message, options) => window.toastNotifications.warning(title, message, options),
    info: (title, message, options) => window.toastNotifications.info(title, message, options)
};
