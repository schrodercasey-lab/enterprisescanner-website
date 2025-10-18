/**
 * Animated Hero Section with Particle System
 * Enterprise Scanner Website
 * Features: Particle network, typing animation, parallax effects, gradient animation
 */

class AnimatedHero {
    constructor(options = {}) {
        this.options = {
            particleCount: options.particleCount || 80,
            particleColor: options.particleColor || 'rgba(59, 130, 246, 0.6)',
            lineColor: options.lineColor || 'rgba(59, 130, 246, 0.2)',
            particleSize: options.particleSize || 2,
            lineDistance: options.lineDistance || 120,
            particleSpeed: options.particleSpeed || 0.3,
            mouseRadius: options.mouseRadius || 150,
            typingSpeed: options.typingSpeed || 80,
            typingDeleteSpeed: options.typingDeleteSpeed || 40,
            typingPauseDuration: options.typingPauseDuration || 2000,
            parallaxEnabled: options.parallaxEnabled !== false,
            gradientAnimation: options.gradientAnimation !== false,
            ...options
        };

        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.mouse = { x: null, y: null, radius: this.options.mouseRadius };
        this.animationFrame = null;
        this.heroSection = null;
        
        // Typing animation state
        this.typingElement = null;
        this.typingPhrases = [];
        this.currentPhraseIndex = 0;
        this.currentText = '';
        this.isDeleting = false;
        this.typingTimer = null;

        // Gradient animation state
        this.gradientOffset = 0;

        this.init();
    }

    init() {
        this.heroSection = document.querySelector('.hero-section, [data-hero-animated]');
        if (!this.heroSection) {
            console.warn('AnimatedHero: No hero section found');
            return;
        }

        this.injectStyles();
        this.createCanvas();
        this.createParticles();
        this.setupEventListeners();
        this.startAnimation();
        
        if (this.options.parallaxEnabled) {
            this.setupParallax();
        }
        
        if (this.options.gradientAnimation) {
            this.animateGradient();
        }

        // Setup typing animation
        this.setupTypingAnimation();
    }

    injectStyles() {
        if (document.getElementById('animated-hero-styles')) return;

        const style = document.createElement('style');
        style.id = 'animated-hero-styles';
        style.textContent = `
            .hero-animated {
                position: relative;
                overflow: hidden;
            }

            .hero-canvas {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                pointer-events: none;
            }

            .hero-content {
                position: relative;
                z-index: 2;
            }

            .hero-parallax-layer {
                transition: transform 0.3s ease-out;
                will-change: transform;
            }

            .hero-typing-text {
                display: inline-block;
                position: relative;
            }

            .hero-typing-text::after {
                content: '|';
                position: absolute;
                right: -12px;
                animation: blink 1s infinite;
                color: #3b82f6;
            }

            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }

            .hero-gradient-animated {
                background: linear-gradient(
                    135deg,
                    #0f172a 0%,
                    #1e293b 25%,
                    #0f172a 50%,
                    #1e293b 75%,
                    #0f172a 100%
                );
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
            }

            @keyframes gradientShift {
                0%, 100% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
            }

            /* Floating animation for hero elements */
            .hero-float {
                animation: heroFloat 3s ease-in-out infinite;
            }

            @keyframes heroFloat {
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-10px);
                }
            }

            /* Fade in animation */
            .hero-fade-in {
                opacity: 0;
                animation: heroFadeIn 1s ease-out forwards;
            }

            @keyframes heroFadeIn {
                to {
                    opacity: 1;
                }
            }

            .hero-fade-in-up {
                opacity: 0;
                transform: translateY(20px);
                animation: heroFadeInUp 1s ease-out forwards;
            }

            @keyframes heroFadeInUp {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Stagger animation delays */
            .hero-fade-in-up:nth-child(1) { animation-delay: 0.2s; }
            .hero-fade-in-up:nth-child(2) { animation-delay: 0.4s; }
            .hero-fade-in-up:nth-child(3) { animation-delay: 0.6s; }
            .hero-fade-in-up:nth-child(4) { animation-delay: 0.8s; }

            /* Glow effect */
            .hero-glow {
                position: relative;
            }

            .hero-glow::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 100%;
                height: 100%;
                background: radial-gradient(
                    circle,
                    rgba(59, 130, 246, 0.3),
                    transparent 70%
                );
                filter: blur(40px);
                opacity: 0;
                transition: opacity 0.3s;
                z-index: -1;
            }

            .hero-glow:hover::before {
                opacity: 1;
            }

            /* Mobile optimization */
            @media (max-width: 768px) {
                .hero-typing-text::after {
                    right: -8px;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                .hero-animated *,
                .hero-gradient-animated {
                    animation: none !important;
                    transition: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }

    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'hero-canvas';
        this.ctx = this.canvas.getContext('2d');
        
        this.heroSection.classList.add('hero-animated');
        if (this.options.gradientAnimation) {
            this.heroSection.classList.add('hero-gradient-animated');
        }
        
        this.heroSection.insertBefore(this.canvas, this.heroSection.firstChild);
        
        this.resizeCanvas();
    }

    resizeCanvas() {
        const rect = this.heroSection.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        
        // Recreate particles on resize
        if (this.particles.length > 0) {
            this.createParticles();
        }
    }

    createParticles() {
        this.particles = [];
        const area = this.canvas.width * this.canvas.height;
        const particleCount = Math.min(
            this.options.particleCount,
            Math.floor(area / 10000)
        );

        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.options.particleSpeed,
                vy: (Math.random() - 0.5) * this.options.particleSpeed,
                size: Math.random() * this.options.particleSize + 1
            });
        }
    }

    setupEventListeners() {
        // Mouse move for particle interaction
        this.heroSection.addEventListener('mousemove', (e) => {
            const rect = this.heroSection.getBoundingClientRect();
            this.mouse.x = e.clientX - rect.left;
            this.mouse.y = e.clientY - rect.top;
        });

        this.heroSection.addEventListener('mouseleave', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });

        // Resize handling
        window.addEventListener('resize', () => {
            this.resizeCanvas();
        });
    }

    updateParticles() {
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Bounce off edges
            if (particle.x < 0 || particle.x > this.canvas.width) {
                particle.vx *= -1;
            }
            if (particle.y < 0 || particle.y > this.canvas.height) {
                particle.vy *= -1;
            }

            // Mouse interaction
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = this.mouse.x - particle.x;
                const dy = this.mouse.y - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.mouse.radius) {
                    const force = (this.mouse.radius - distance) / this.mouse.radius;
                    const angle = Math.atan2(dy, dx);
                    particle.vx -= Math.cos(angle) * force * 0.5;
                    particle.vy -= Math.sin(angle) * force * 0.5;
                }
            }

            // Apply velocity damping
            particle.vx *= 0.99;
            particle.vy *= 0.99;

            // Ensure minimum velocity
            if (Math.abs(particle.vx) < 0.1) {
                particle.vx = (Math.random() - 0.5) * this.options.particleSpeed;
            }
            if (Math.abs(particle.vy) < 0.1) {
                particle.vy = (Math.random() - 0.5) * this.options.particleSpeed;
            }
        });
    }

    drawParticles() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw connections
        this.particles.forEach((particle, i) => {
            for (let j = i + 1; j < this.particles.length; j++) {
                const other = this.particles[j];
                const dx = particle.x - other.x;
                const dy = particle.y - other.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.options.lineDistance) {
                    const opacity = (1 - distance / this.options.lineDistance) * 0.5;
                    this.ctx.strokeStyle = this.options.lineColor.replace(/[\d.]+\)$/, `${opacity})`);
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(other.x, other.y);
                    this.ctx.stroke();
                }
            }
        });

        // Draw particles
        this.particles.forEach(particle => {
            this.ctx.fillStyle = this.options.particleColor;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    startAnimation() {
        const animate = () => {
            this.updateParticles();
            this.drawParticles();
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }

    setupParallax() {
        const parallaxLayers = this.heroSection.querySelectorAll('[data-parallax]');
        
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            
            parallaxLayers.forEach(layer => {
                const speed = parseFloat(layer.getAttribute('data-parallax')) || 0.5;
                const yPos = -(scrollY * speed);
                layer.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    setupTypingAnimation() {
        this.typingElement = this.heroSection.querySelector('[data-typing]');
        if (!this.typingElement) return;

        // Get phrases from data attribute or default
        const phrasesData = this.typingElement.getAttribute('data-typing');
        this.typingPhrases = phrasesData 
            ? phrasesData.split('|') 
            : ['Enterprise Security', 'Fortune 500 Ready', 'AI-Powered Protection'];

        this.typingElement.classList.add('hero-typing-text');
        this.typeText();
    }

    typeText() {
        const currentPhrase = this.typingPhrases[this.currentPhraseIndex];
        
        if (!this.isDeleting) {
            // Typing
            this.currentText = currentPhrase.substring(0, this.currentText.length + 1);
            this.typingElement.textContent = this.currentText;

            if (this.currentText === currentPhrase) {
                // Finished typing, pause then start deleting
                this.typingTimer = setTimeout(() => {
                    this.isDeleting = true;
                    this.typeText();
                }, this.options.typingPauseDuration);
                return;
            }

            this.typingTimer = setTimeout(() => {
                this.typeText();
            }, this.options.typingSpeed);
        } else {
            // Deleting
            this.currentText = currentPhrase.substring(0, this.currentText.length - 1);
            this.typingElement.textContent = this.currentText;

            if (this.currentText === '') {
                // Finished deleting, move to next phrase
                this.isDeleting = false;
                this.currentPhraseIndex = (this.currentPhraseIndex + 1) % this.typingPhrases.length;
                
                this.typingTimer = setTimeout(() => {
                    this.typeText();
                }, 500);
                return;
            }

            this.typingTimer = setTimeout(() => {
                this.typeText();
            }, this.options.typingDeleteSpeed);
        }
    }

    animateGradient() {
        // Gradient animation is handled by CSS
        // This method can be used for custom gradient animations if needed
    }

    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
        
        this.heroSection.classList.remove('hero-animated', 'hero-gradient-animated');
        
        const styles = document.getElementById('animated-hero-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Auto-initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.animatedHero = new AnimatedHero({
        particleCount: 80,
        particleSpeed: 0.3,
        lineDistance: 120,
        mouseRadius: 150,
        typingSpeed: 80,
        typingPauseDuration: 2000
    });
});
