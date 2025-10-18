/**
 * Loading Indicator System
 * =========================
 * 
 * Elegant loading states for async operations
 * Features: Inline spinners, overlay loaders, progress bars, skeleton screens
 * 
 * Usage:
 *   const loader = showLoader('#chat-container');
 *   // ... async operation ...
 *   hideLoader(loader);
 */

class LoadingIndicator {
    constructor() {
        this.activeLoaders = new Map();
    }

    /**
     * Show inline spinner in element
     */
    showInline(target, text = 'Loading...') {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (!element) return null;

        const loader = document.createElement('div');
        loader.className = 'loading-inline flex items-center justify-center p-4';
        loader.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="loading-spinner"></div>
                <span class="text-sm text-gray-400">${text}</span>
            </div>
        `;

        element.appendChild(loader);
        this.activeLoaders.set(loader, { element, type: 'inline' });
        return loader;
    }

    /**
     * Show overlay loader (covers entire element)
     */
    showOverlay(target, text = 'Loading...') {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (!element) return null;

        // Make element position relative if not already
        const position = window.getComputedStyle(element).position;
        if (position === 'static') {
            element.style.position = 'relative';
        }

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-40 rounded-lg';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="loading-spinner-large mb-4"></div>
                <p class="text-sm text-gray-300">${text}</p>
            </div>
        `;

        element.appendChild(overlay);
        this.activeLoaders.set(overlay, { element, type: 'overlay' });
        return overlay;
    }

    /**
     * Show full page loader
     */
    showFullPage(text = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-fullpage fixed inset-0 bg-slate-900/95 backdrop-blur-md flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="loading-spinner-xl mb-6"></div>
                <p class="text-lg text-gray-200 mb-2">${text}</p>
                <p class="text-sm text-gray-400">Please wait...</p>
            </div>
        `;

        document.body.appendChild(overlay);
        this.activeLoaders.set(overlay, { element: document.body, type: 'fullpage' });
        return overlay;
    }

    /**
     * Show progress bar
     */
    showProgress(target, text = 'Processing...') {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (!element) return null;

        const progress = document.createElement('div');
        progress.className = 'loading-progress p-4';
        progress.innerHTML = `
            <div class="mb-2 flex justify-between items-center">
                <span class="text-sm text-gray-400">${text}</span>
                <span class="text-sm text-blue-400 progress-percentage">0%</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                <div class="progress-bar bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-300" style="width: 0%"></div>
            </div>
        `;

        element.appendChild(progress);
        this.activeLoaders.set(progress, { element, type: 'progress' });
        return progress;
    }

    /**
     * Update progress bar
     */
    updateProgress(loader, percentage) {
        if (!loader) return;
        
        const bar = loader.querySelector('.progress-bar');
        const text = loader.querySelector('.progress-percentage');
        
        if (bar) {
            bar.style.width = `${percentage}%`;
        }
        if (text) {
            text.textContent = `${percentage}%`;
        }
    }

    /**
     * Show skeleton loader (placeholder for content)
     */
    showSkeleton(target, rows = 3) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (!element) return null;

        const skeleton = document.createElement('div');
        skeleton.className = 'loading-skeleton space-y-3 p-4';
        
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('div');
            row.className = 'skeleton-row animate-pulse';
            row.innerHTML = `
                <div class="h-4 bg-slate-700 rounded mb-2"></div>
                <div class="h-4 bg-slate-700 rounded w-5/6"></div>
            `;
            skeleton.appendChild(row);
        }

        element.appendChild(skeleton);
        this.activeLoaders.set(skeleton, { element, type: 'skeleton' });
        return skeleton;
    }

    /**
     * Show button loading state
     */
    showButtonLoading(button, text = 'Loading...') {
        if (!button) return null;

        const originalContent = button.innerHTML;
        button.disabled = true;
        button.classList.add('loading-button');
        button.innerHTML = `
            <span class="inline-flex items-center">
                <span class="loading-spinner-small mr-2"></span>
                ${text}
            </span>
        `;

        this.activeLoaders.set(button, { 
            element: button, 
            type: 'button', 
            originalContent 
        });
        return button;
    }

    /**
     * Hide any loader
     */
    hide(loader) {
        if (!loader) return;

        const loaderData = this.activeLoaders.get(loader);
        if (!loaderData) return;

        if (loaderData.type === 'button') {
            // Restore button
            loader.disabled = false;
            loader.classList.remove('loading-button');
            loader.innerHTML = loaderData.originalContent;
        } else {
            // Remove element
            if (loader.parentNode) {
                loader.parentNode.removeChild(loader);
            }
        }

        this.activeLoaders.delete(loader);
    }

    /**
     * Hide all loaders
     */
    hideAll() {
        this.activeLoaders.forEach((data, loader) => {
            this.hide(loader);
        });
    }
}

// Global instance
const loadingManager = new LoadingIndicator();

// Convenience functions
function showLoader(target, text = 'Loading...') {
    return loadingManager.showOverlay(target, text);
}

function showInlineLoader(target, text = 'Loading...') {
    return loadingManager.showInline(target, text);
}

function showFullPageLoader(text = 'Loading...') {
    return loadingManager.showFullPage(text);
}

function showProgress(target, text = 'Processing...') {
    return loadingManager.showProgress(target, text);
}

function updateProgress(loader, percentage) {
    loadingManager.updateProgress(loader, percentage);
}

function showSkeleton(target, rows = 3) {
    return loadingManager.showSkeleton(target, rows);
}

function showButtonLoading(button, text = 'Loading...') {
    return loadingManager.showButtonLoading(button, text);
}

function hideLoader(loader) {
    loadingManager.hide(loader);
}

function hideAllLoaders() {
    loadingManager.hideAll();
}

// Add CSS for loading indicators
const style = document.createElement('style');
style.textContent = `
    /* Spinner animations */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-top-color: #3b82f6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    .loading-spinner-small {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: inline-block;
    }
    
    .loading-spinner-large {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-top-color: #3b82f6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 0 auto;
    }
    
    .loading-spinner-xl {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(59, 130, 246, 0.3);
        border-top-color: #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    /* Skeleton pulse */
    @keyframes skeleton-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .skeleton-row {
        animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Button loading state */
    .loading-button {
        opacity: 0.7;
        cursor: not-allowed;
    }
`;
document.head.appendChild(style);
