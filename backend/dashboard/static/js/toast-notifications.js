/**
 * Toast Notification System
 * =========================
 * 
 * Beautiful, non-intrusive notifications for user feedback
 * Supports: success, error, warning, info types
 * Features: Auto-dismiss, manual close, progress bar, icons
 * 
 * Usage:
 *   showToast('Operation successful!', 'success');
 *   showToast('Connection lost', 'error', 0); // No auto-dismiss
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-50 space-y-3';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', duration = 5000, options = {}) {
        const toast = this.createToast(message, type, duration, options);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        }, 10);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(toast);
            }, duration);
        }

        return toast;
    }

    createToast(message, type, duration, options) {
        const toast = document.createElement('div');
        toast.className = `toast transform translate-x-full opacity-0 transition-all duration-300 ease-out 
                          flex items-start p-4 rounded-lg shadow-2xl max-w-md backdrop-blur-lg
                          ${this.getTypeClasses(type)}`;
        
        const icon = this.getIcon(type);
        const hasAction = options.action && options.actionLabel;

        toast.innerHTML = `
            <div class="flex-shrink-0 mt-0.5">
                ${icon}
            </div>
            <div class="ml-3 flex-1">
                ${options.title ? `<p class="text-sm font-semibold mb-1">${options.title}</p>` : ''}
                <p class="text-sm ${options.title ? 'opacity-90' : ''}">${message}</p>
                ${hasAction ? `
                    <button class="mt-2 text-sm font-medium underline hover:no-underline toast-action">
                        ${options.actionLabel}
                    </button>
                ` : ''}
            </div>
            <button class="ml-4 flex-shrink-0 inline-flex text-current opacity-70 hover:opacity-100 transition-opacity toast-close">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </button>
            ${duration > 0 ? `
                <div class="absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg toast-progress"
                     style="animation: toast-progress ${duration}ms linear;"></div>
            ` : ''}
        `;

        // Add event listeners
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.dismiss(toast));

        if (hasAction) {
            const actionBtn = toast.querySelector('.toast-action');
            actionBtn.addEventListener('click', () => {
                options.action();
                this.dismiss(toast);
            });
        }

        return toast;
    }

    getTypeClasses(type) {
        const classes = {
            success: 'bg-green-900/90 text-green-50 border-l-4 border-green-400',
            error: 'bg-red-900/90 text-red-50 border-l-4 border-red-400',
            warning: 'bg-yellow-900/90 text-yellow-50 border-l-4 border-yellow-400',
            info: 'bg-blue-900/90 text-blue-50 border-l-4 border-blue-400'
        };
        return classes[type] || classes.info;
    }

    getIcon(type) {
        const icons = {
            success: `
                <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `,
            error: `
                <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `,
            warning: `
                <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
            `,
            info: `
                <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `
        };
        return icons[type] || icons.info;
    }

    dismiss(toast) {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            const index = this.toasts.indexOf(toast);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
        }, 300);
    }

    dismissAll() {
        this.toasts.forEach(toast => this.dismiss(toast));
    }
}

// Global instance
const toastManager = new ToastNotification();

// Convenience functions
function showToast(message, type = 'info', duration = 5000, options = {}) {
    return toastManager.show(message, type, duration, options);
}

function showSuccess(message, duration = 5000) {
    return toastManager.show(message, 'success', duration);
}

function showError(message, duration = 0, options = {}) {
    return toastManager.show(message, 'error', duration, options);
}

function showWarning(message, duration = 5000) {
    return toastManager.show(message, 'warning', duration);
}

function showInfo(message, duration = 5000) {
    return toastManager.show(message, 'info', duration);
}

function dismissAllToasts() {
    toastManager.dismissAll();
}

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes toast-progress {
        from { width: 100%; }
        to { width: 0%; }
    }
    
    .toast {
        min-width: 300px;
        max-width: 500px;
    }
    
    @media (max-width: 640px) {
        .toast {
            min-width: auto;
            max-width: calc(100vw - 2rem);
        }
        
        #toast-container {
            left: 1rem;
            right: 1rem;
        }
    }
`;
document.head.appendChild(style);
