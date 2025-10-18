/**
 * Error Modal System
 * ==================
 * 
 * Modal dialogs for detailed error information and recovery
 * Features: Error details, stack traces, suggested actions, retry functionality
 * 
 * Usage:
 *   showErrorModal({
 *     title: 'Operation Failed',
 *     message: 'Unable to fetch data',
 *     details: error.stack,
 *     actions: [{ label: 'Retry', handler: () => retry() }]
 *   });
 */

class ErrorModal {
    constructor() {
        this.modal = null;
        this.isOpen = false;
    }

    show(options = {}) {
        const {
            title = 'Error',
            message = 'An unexpected error occurred',
            details = null,
            type = 'error', // error, warning, info
            actions = [],
            dismissible = true
        } = options;

        // Close existing modal
        if (this.isOpen) {
            this.close();
        }

        // Create modal
        this.modal = document.createElement('div');
        this.modal.className = 'error-modal fixed inset-0 z-50 flex items-center justify-center p-4';
        this.modal.innerHTML = `
            <!-- Backdrop -->
            <div class="modal-backdrop absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
            
            <!-- Modal Container -->
            <div class="modal-container relative bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-slate-700 animate-modal-in">
                <!-- Header -->
                <div class="modal-header flex items-start justify-between p-6 border-b border-slate-700 ${this.getHeaderColor(type)}">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0 mt-1">
                            ${this.getIcon(type)}
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-white">${title}</h3>
                            <p class="text-sm text-slate-300 mt-1">${message}</p>
                        </div>
                    </div>
                    ${dismissible ? `
                        <button class="modal-close text-slate-400 hover:text-white transition-colors ml-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    ` : ''}
                </div>
                
                <!-- Body -->
                <div class="modal-body p-6 overflow-y-auto max-h-96">
                    ${details ? `
                        <div class="mb-4">
                            <button class="text-sm text-blue-400 hover:text-blue-300 flex items-center mb-2 error-details-toggle">
                                <svg class="w-4 h-4 mr-1 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                </svg>
                                Show Technical Details
                            </button>
                            <div class="error-details hidden bg-slate-900 rounded-lg p-4 border border-slate-700">
                                <pre class="text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap">${this.escapeHtml(details)}</pre>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="space-y-3">
                        ${this.getSuggestions(type, options)}
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="modal-footer flex items-center justify-end space-x-3 px-6 py-4 bg-slate-900/50 border-t border-slate-700">
                    ${this.renderActions(actions, dismissible)}
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.isOpen = true;

        // Add event listeners
        this.attachEventListeners(actions, dismissible);

        // Animate in
        setTimeout(() => {
            this.modal.querySelector('.modal-container').classList.add('opacity-100');
        }, 10);
    }

    getHeaderColor(type) {
        const colors = {
            error: 'bg-red-900/20',
            warning: 'bg-yellow-900/20',
            info: 'bg-blue-900/20'
        };
        return colors[type] || colors.error;
    }

    getIcon(type) {
        const icons = {
            error: `
                <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `,
            warning: `
                <svg class="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
            `,
            info: `
                <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `
        };
        return icons[type] || icons.error;
    }

    getSuggestions(type, options) {
        if (options.suggestions && options.suggestions.length > 0) {
            return `
                <div class="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <h4 class="text-sm font-semibold text-slate-200 mb-2">💡 Suggestions:</h4>
                    <ul class="space-y-2">
                        ${options.suggestions.map(s => `
                            <li class="text-sm text-slate-300 flex items-start">
                                <svg class="w-4 h-4 mr-2 mt-0.5 text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                </svg>
                                ${s}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        return '';
    }

    renderActions(actions, dismissible) {
        let html = '';
        
        if (actions && actions.length > 0) {
            actions.forEach((action, index) => {
                const isPrimary = action.primary || index === 0;
                html += `
                    <button class="modal-action px-4 py-2 rounded-lg font-medium transition-colors ${
                        isPrimary 
                            ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                            : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
                    }" data-action="${index}">
                        ${action.label}
                    </button>
                `;
            });
        }
        
        if (dismissible) {
            html += `
                <button class="modal-dismiss px-4 py-2 rounded-lg font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors">
                    Close
                </button>
            `;
        }
        
        return html;
    }

    attachEventListeners(actions, dismissible) {
        if (!this.modal) return;

        // Close button
        if (dismissible) {
            const closeBtn = this.modal.querySelector('.modal-close');
            const dismissBtn = this.modal.querySelector('.modal-dismiss');
            const backdrop = this.modal.querySelector('.modal-backdrop');

            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.close());
            }
            if (dismissBtn) {
                dismissBtn.addEventListener('click', () => this.close());
            }
            if (backdrop) {
                backdrop.addEventListener('click', () => this.close());
            }
        }

        // Details toggle
        const detailsToggle = this.modal.querySelector('.error-details-toggle');
        if (detailsToggle) {
            detailsToggle.addEventListener('click', () => {
                const details = this.modal.querySelector('.error-details');
                const arrow = detailsToggle.querySelector('svg');
                
                if (details.classList.contains('hidden')) {
                    details.classList.remove('hidden');
                    arrow.classList.add('rotate-180');
                    detailsToggle.textContent = 'Hide Technical Details';
                    detailsToggle.prepend(arrow);
                } else {
                    details.classList.add('hidden');
                    arrow.classList.remove('rotate-180');
                    detailsToggle.textContent = 'Show Technical Details';
                    detailsToggle.prepend(arrow);
                }
            });
        }

        // Action buttons
        if (actions && actions.length > 0) {
            const actionBtns = this.modal.querySelectorAll('.modal-action');
            actionBtns.forEach((btn, index) => {
                btn.addEventListener('click', () => {
                    if (actions[index].handler) {
                        actions[index].handler();
                    }
                    if (actions[index].closeAfter !== false) {
                        this.close();
                    }
                });
            });
        }

        // Keyboard escape
        if (dismissible) {
            this.escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    this.close();
                }
            };
            document.addEventListener('keydown', this.escapeHandler);
        }
    }

    close() {
        if (!this.modal || !this.isOpen) return;

        // Animate out
        this.modal.querySelector('.modal-container').classList.add('opacity-0', 'scale-95');
        this.modal.querySelector('.modal-backdrop').classList.add('opacity-0');

        setTimeout(() => {
            if (this.modal && this.modal.parentNode) {
                this.modal.parentNode.removeChild(this.modal);
            }
            this.modal = null;
            this.isOpen = false;

            // Remove escape listener
            if (this.escapeHandler) {
                document.removeEventListener('keydown', this.escapeHandler);
                this.escapeHandler = null;
            }
        }, 200);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
const errorModalManager = new ErrorModal();

// Convenience function
function showErrorModal(options) {
    return errorModalManager.show(options);
}

// Add CSS for modal animations
const style = document.createElement('style');
style.textContent = `
    @keyframes modal-in {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .animate-modal-in {
        animation: modal-in 0.2s ease-out;
    }
    
    .error-modal {
        animation: fadeIn 0.2s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);
