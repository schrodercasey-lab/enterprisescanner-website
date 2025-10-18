/**
 * Counter Animations - Animated number counting
 * Enterprise Scanner Website
 * Creates engaging counter animations for statistics
 */

class CounterAnimations {
    constructor(options = {}) {
        this.options = {
            duration: options.duration || 2000,
            easing: options.easing || 'easeOutExpo',
            separator: options.separator || ',',
            decimal: options.decimal || '.',
            prefix: options.prefix || '',
            suffix: options.suffix || '',
            observerThreshold: options.observerThreshold || 0.5,
            ...options
        };

        this.counters = new Map();
        this.observer = null;
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.findAndRegisterCounters();
    }

    setupIntersectionObserver() {
        this.observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const counter = this.counters.get(entry.target);
                        if (counter && !counter.animated) {
                            this.animateCounter(entry.target, counter);
                        }
                    }
                });
            },
            { threshold: this.options.observerThreshold }
        );
    }

    findAndRegisterCounters() {
        // Find all elements with data-counter attribute
        const counterElements = document.querySelectorAll('[data-counter]');
        
        counterElements.forEach(element => {
            this.registerCounter(element);
        });
    }

    registerCounter(element, options = {}) {
        const target = parseFloat(element.getAttribute('data-counter'));
        const duration = parseInt(element.getAttribute('data-duration')) || this.options.duration;
        const prefix = element.getAttribute('data-prefix') || this.options.prefix;
        const suffix = element.getAttribute('data-suffix') || this.options.suffix;
        const decimals = parseInt(element.getAttribute('data-decimals')) || 0;
        const separator = element.getAttribute('data-separator') || this.options.separator;

        const counter = {
            target,
            current: 0,
            duration,
            prefix,
            suffix,
            decimals,
            separator,
            animated: false,
            ...options
        };

        this.counters.set(element, counter);
        this.observer.observe(element);

        // Store original value
        element.setAttribute('data-original', element.textContent);
    }

    animateCounter(element, counter) {
        counter.animated = true;
        
        const startTime = performance.now();
        const startValue = counter.current;
        const endValue = counter.target;
        const change = endValue - startValue;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / counter.duration, 1);

            // Apply easing
            const easedProgress = this.easing[this.options.easing](progress);
            
            // Calculate current value
            counter.current = startValue + (change * easedProgress);

            // Format and update display
            element.textContent = this.formatNumber(counter.current, counter);

            // Continue animation or complete
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                counter.current = endValue;
                element.textContent = this.formatNumber(endValue, counter);
                
                // Trigger completion event
                element.dispatchEvent(new CustomEvent('counterComplete', {
                    detail: { value: endValue }
                }));
            }
        };

        requestAnimationFrame(animate);
    }

    formatNumber(value, counter) {
        // Round to specified decimals
        let formatted = value.toFixed(counter.decimals);

        // Split into integer and decimal parts
        const parts = formatted.split('.');
        
        // Add thousand separators
        if (counter.separator) {
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, counter.separator);
        }

        // Rejoin with decimal
        formatted = parts.join(this.options.decimal);

        // Add prefix and suffix
        return `${counter.prefix}${formatted}${counter.suffix}`;
    }

    // Easing functions
    easing = {
        linear: (t) => t,
        
        easeInQuad: (t) => t * t,
        easeOutQuad: (t) => t * (2 - t),
        easeInOutQuad: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
        
        easeInCubic: (t) => t * t * t,
        easeOutCubic: (t) => (--t) * t * t + 1,
        easeInOutCubic: (t) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
        
        easeInQuart: (t) => t * t * t * t,
        easeOutQuart: (t) => 1 - (--t) * t * t * t,
        easeInOutQuart: (t) => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t,
        
        easeInQuint: (t) => t * t * t * t * t,
        easeOutQuint: (t) => 1 + (--t) * t * t * t * t,
        easeInOutQuint: (t) => t < 0.5 ? 16 * t * t * t * t * t : 1 + 16 * (--t) * t * t * t * t,
        
        easeInExpo: (t) => t === 0 ? 0 : Math.pow(2, 10 * (t - 1)),
        easeOutExpo: (t) => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
        easeInOutExpo: (t) => {
            if (t === 0 || t === 1) return t;
            if (t < 0.5) return Math.pow(2, 20 * t - 10) / 2;
            return (2 - Math.pow(2, -20 * t + 10)) / 2;
        },
        
        easeInCirc: (t) => 1 - Math.sqrt(1 - t * t),
        easeOutCirc: (t) => Math.sqrt(1 - (--t) * t),
        easeInOutCirc: (t) => {
            if (t < 0.5) return (1 - Math.sqrt(1 - 4 * t * t)) / 2;
            return (Math.sqrt(1 - (-2 * t + 2) * (-2 * t + 2)) + 1) / 2;
        },
        
        easeInBack: (t) => {
            const c1 = 1.70158;
            const c3 = c1 + 1;
            return c3 * t * t * t - c1 * t * t;
        },
        easeOutBack: (t) => {
            const c1 = 1.70158;
            const c3 = c1 + 1;
            return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
        },
        easeInOutBack: (t) => {
            const c1 = 1.70158;
            const c2 = c1 * 1.525;
            if (t < 0.5) {
                return (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2;
            }
            return (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
        }
    };

    // Public methods
    reset(element) {
        const counter = this.counters.get(element);
        if (counter) {
            counter.current = 0;
            counter.animated = false;
            const original = element.getAttribute('data-original');
            if (original) {
                element.textContent = original;
            }
        }
    }

    resetAll() {
        this.counters.forEach((counter, element) => {
            this.reset(element);
        });
    }

    animateAll() {
        this.counters.forEach((counter, element) => {
            if (!counter.animated) {
                this.animateCounter(element, counter);
            }
        });
    }

    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.counters.clear();
    }
}

// Helper function to create counter elements
function createCounter(value, options = {}) {
    const element = document.createElement('span');
    element.setAttribute('data-counter', value);
    
    if (options.duration) element.setAttribute('data-duration', options.duration);
    if (options.prefix) element.setAttribute('data-prefix', options.prefix);
    if (options.suffix) element.setAttribute('data-suffix', options.suffix);
    if (options.decimals !== undefined) element.setAttribute('data-decimals', options.decimals);
    if (options.separator) element.setAttribute('data-separator', options.separator);
    
    element.textContent = options.prefix || '';
    element.textContent += '0';
    element.textContent += options.suffix || '';
    
    return element;
}

// Global instance
window.counterAnimations = new CounterAnimations();

// Convenience function
window.animateCounter = function(element, value, options = {}) {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (element) {
        element.setAttribute('data-counter', value);
        if (options.duration) element.setAttribute('data-duration', options.duration);
        if (options.prefix) element.setAttribute('data-prefix', options.prefix);
        if (options.suffix) element.setAttribute('data-suffix', options.suffix);
        
        window.counterAnimations.registerCounter(element, options);
        
        // Immediately animate if in viewport
        const rect = element.getBoundingClientRect();
        if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
            const counter = window.counterAnimations.counters.get(element);
            if (counter) {
                window.counterAnimations.animateCounter(element, counter);
            }
        }
    }
};

// Auto-initialize counters on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.counterAnimations.findAndRegisterCounters();
});
