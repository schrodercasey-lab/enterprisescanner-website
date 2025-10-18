/**
 * 3D Card Effects - Interactive tilt and hover effects
 * Enterprise Scanner Website
 * Creates engaging 3D card interactions with parallax
 */

class Card3DEffects {
    constructor(options = {}) {
        this.options = {
            tiltEnabled: options.tiltEnabled !== false,
            glareEnabled: options.glareEnabled !== false,
            maxTilt: options.maxTilt || 15,
            perspective: options.perspective || 1000,
            scale: options.scale || 1.05,
            speed: options.speed || 400,
            easing: options.easing || 'cubic-bezier(0.03, 0.98, 0.52, 0.99)',
            glareMaxOpacity: options.glareMaxOpacity || 0.3,
            ...options
        };

        this.cards = [];
        this.init();
    }

    init() {
        this.injectStyles();
        this.findAndRegisterCards();
    }

    injectStyles() {
        if (document.getElementById('card-3d-styles')) return;

        const style = document.createElement('style');
        style.id = 'card-3d-styles';
        style.textContent = `
            .card-3d {
                position: relative;
                transform-style: preserve-3d;
                transition: all ${this.options.speed}ms ${this.options.easing};
                will-change: transform;
            }

            .card-3d:hover {
                transform: scale(${this.options.scale});
            }

            .card-3d-wrapper {
                position: relative;
                width: 100%;
                height: 100%;
                transition: all ${this.options.speed}ms ${this.options.easing};
                transform-style: preserve-3d;
            }

            .card-3d-glare {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border-radius: inherit;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.4), transparent);
                opacity: 0;
                mix-blend-mode: overlay;
                pointer-events: none;
                transition: opacity ${this.options.speed}ms ease;
            }

            .card-3d:hover .card-3d-glare {
                opacity: 1;
            }

            .card-3d-inner {
                position: relative;
                width: 100%;
                height: 100%;
                transform-style: preserve-3d;
            }

            .card-3d-layer {
                transition: transform ${this.options.speed}ms ${this.options.easing};
            }

            .card-3d-layer-1 {
                transform: translateZ(20px);
            }

            .card-3d-layer-2 {
                transform: translateZ(40px);
            }

            .card-3d-layer-3 {
                transform: translateZ(60px);
            }

            /* Floating animation */
            @keyframes float {
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-10px);
                }
            }

            .card-3d.float {
                animation: float 3s ease-in-out infinite;
            }

            /* Shimmer effect */
            @keyframes shimmer {
                0% {
                    background-position: -1000px 0;
                }
                100% {
                    background-position: 1000px 0;
                }
            }

            .card-3d-shimmer {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.1),
                    transparent
                );
                background-size: 1000px 100%;
                animation: shimmer 3s infinite;
                pointer-events: none;
                border-radius: inherit;
            }

            /* Glow effect */
            .card-3d-glow {
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-radius: inherit;
                opacity: 0;
                filter: blur(20px);
                transition: opacity 0.3s ease;
                z-index: -1;
            }

            .card-3d:hover .card-3d-glow {
                opacity: 0.6;
            }

            /* Reveal animation */
            .card-3d-reveal {
                opacity: 0;
                transform: translateY(30px);
                transition: all 0.6s ease;
            }

            .card-3d-reveal.visible {
                opacity: 1;
                transform: translateY(0);
            }

            /* Stagger animation delays */
            .card-3d-reveal:nth-child(1) { transition-delay: 0.1s; }
            .card-3d-reveal:nth-child(2) { transition-delay: 0.2s; }
            .card-3d-reveal:nth-child(3) { transition-delay: 0.3s; }
            .card-3d-reveal:nth-child(4) { transition-delay: 0.4s; }
            .card-3d-reveal:nth-child(5) { transition-delay: 0.5s; }
            .card-3d-reveal:nth-child(6) { transition-delay: 0.6s; }

            /* Interactive elements */
            .card-3d-button {
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .card-3d-button::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.2);
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }

            .card-3d-button:hover::before {
                width: 300px;
                height: 300px;
            }

            /* Mobile optimization */
            @media (max-width: 768px) {
                .card-3d {
                    transform: none !important;
                }

                .card-3d:hover {
                    transform: scale(1.02) !important;
                }

                .card-3d-wrapper {
                    transform: none !important;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                .card-3d,
                .card-3d-wrapper,
                .card-3d-layer,
                .card-3d-glare,
                .card-3d-reveal {
                    transition: none !important;
                    animation: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }

    findAndRegisterCards() {
        const cardElements = document.querySelectorAll('[data-card-3d]');
        cardElements.forEach(element => {
            this.registerCard(element);
        });
    }

    registerCard(element, options = {}) {
        const config = { ...this.options, ...options };

        // Wrap card content if not already wrapped
        if (!element.querySelector('.card-3d-wrapper')) {
            const content = element.innerHTML;
            element.innerHTML = `
                <div class="card-3d-wrapper">
                    <div class="card-3d-inner">
                        ${content}
                    </div>
                    ${config.glareEnabled ? '<div class="card-3d-glare"></div>' : ''}
                    ${config.glow ? '<div class="card-3d-glow"></div>' : ''}
                </div>
            `;
        }

        element.classList.add('card-3d');
        if (config.float) element.classList.add('float');
        if (config.shimmer) {
            const shimmer = document.createElement('div');
            shimmer.className = 'card-3d-shimmer';
            element.appendChild(shimmer);
        }

        const wrapper = element.querySelector('.card-3d-wrapper');
        const glare = element.querySelector('.card-3d-glare');

        const card = {
            element,
            wrapper,
            glare,
            config,
            width: 0,
            height: 0,
            centerX: 0,
            centerY: 0
        };

        this.updateCardDimensions(card);

        // Event listeners
        if (config.tiltEnabled && !this.isMobile()) {
            element.addEventListener('mouseenter', (e) => this.handleMouseEnter(e, card));
            element.addEventListener('mousemove', (e) => this.handleMouseMove(e, card));
            element.addEventListener('mouseleave', (e) => this.handleMouseLeave(e, card));
        }

        // Touch events for mobile
        element.addEventListener('touchstart', (e) => this.handleTouchStart(e, card));

        // Resize observer
        const resizeObserver = new ResizeObserver(() => {
            this.updateCardDimensions(card);
        });
        resizeObserver.observe(element);

        this.cards.push(card);
        return card;
    }

    updateCardDimensions(card) {
        const rect = card.element.getBoundingClientRect();
        card.width = rect.width;
        card.height = rect.height;
        card.centerX = card.width / 2;
        card.centerY = card.height / 2;
    }

    handleMouseEnter(e, card) {
        card.wrapper.style.transition = 'none';
    }

    handleMouseMove(e, card) {
        const rect = card.element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Calculate tilt angles
        const tiltX = ((y - card.centerY) / card.centerY) * card.config.maxTilt;
        const tiltY = ((card.centerX - x) / card.centerX) * card.config.maxTilt;

        // Apply 3D transform
        card.wrapper.style.transform = `
            perspective(${card.config.perspective}px)
            rotateX(${tiltX}deg)
            rotateY(${tiltY}deg)
            scale3d(1, 1, 1)
        `;

        // Update glare position
        if (card.glare) {
            const glareX = (x / card.width) * 100;
            const glareY = (y / card.height) * 100;
            card.glare.style.background = `
                radial-gradient(
                    circle at ${glareX}% ${glareY}%,
                    rgba(255, 255, 255, ${card.config.glareMaxOpacity}),
                    transparent 50%
                )
            `;
        }
    }

    handleMouseLeave(e, card) {
        card.wrapper.style.transition = `all ${card.config.speed}ms ${card.config.easing}`;
        card.wrapper.style.transform = `
            perspective(${card.config.perspective}px)
            rotateX(0deg)
            rotateY(0deg)
            scale3d(1, 1, 1)
        `;

        if (card.glare) {
            card.glare.style.opacity = '0';
        }
    }

    handleTouchStart(e, card) {
        // Simple scale effect on touch
        card.element.style.transform = `scale(${card.config.scale * 0.98})`;
        setTimeout(() => {
            card.element.style.transform = '';
        }, 200);
    }

    // Reveal animation on scroll
    enableRevealAnimation() {
        const cards = document.querySelectorAll('.card-3d');
        
        cards.forEach(card => {
            card.classList.add('card-3d-reveal');
        });

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 }
        );

        cards.forEach(card => observer.observe(card));
    }

    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            || window.innerWidth < 768;
    }

    destroy() {
        this.cards.forEach(card => {
            card.element.classList.remove('card-3d', 'float');
            // Remove event listeners would go here
        });
        this.cards = [];

        const styles = document.getElementById('card-3d-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Global instance
window.card3DEffects = new Card3DEffects();

// Convenience function
window.make3DCard = function(element, options = {}) {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (element) {
        element.setAttribute('data-card-3d', 'true');
        return window.card3DEffects.registerCard(element, options);
    }
};

// Auto-initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.card3DEffects.findAndRegisterCards();
    
    // Enable reveal animations
    setTimeout(() => {
        window.card3DEffects.enableRevealAnimation();
    }, 100);
});
