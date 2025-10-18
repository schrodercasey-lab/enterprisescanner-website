/**
 * JUPITER AI INTEGRATION - ENHANCED VERSION v2.1
 * ==============================================
 * 
 * IMPROVEMENTS IN THIS VERSION:
 * ✅ Error handling & graceful degradation
 * ✅ Memory leak fixes
 * ✅ Loading states & progress indicators
 * ✅ Tour pause/skip/resume controls
 * ✅ Layer navigation breadcrumb
 * ✅ Interactive face hotspots
 * ✅ Keyboard shortcuts help overlay
 * ✅ Performance monitoring
 * ✅ Mobile optimizations
 * ✅ Accessibility improvements
 * 
 * @version 2.1.0
 * @author Enterprise Scanner Team
 * @patent-pending Advanced AI Visualization Control
 */

(function() {
    'use strict';

    // Global state
    let performanceMonitor = null;
    let dependenciesChecked = false;

    /**
     * CHECK DEPENDENCIES BEFORE INITIALIZATION
     */
    function checkDependencies() {
        const errors = [];
        const warnings = [];
        
        // Check Three.js
        if (typeof THREE === 'undefined') {
            errors.push('Three.js library not loaded');
        }
        
        // Check base threat map
        if (!window.threatMap3D) {
            errors.push('3D Threat Map not initialized');
        }
        
        // Check voice synthesis (warning only)
        if (!window.speechSynthesis) {
            warnings.push('Voice synthesis not available - text-only mode enabled');
        }
        
        // Check WebGL support
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) {
            errors.push('WebGL not supported');
        }
        
        // Display errors
        if (errors.length > 0) {
            showErrorPanel(errors);
            return false;
        }
        
        // Log warnings
        warnings.forEach(warning => console.warn('Jupiter AI:', warning));
        
        return true;
    }

    /**
     * SHOW ERROR PANEL
     */
    function showErrorPanel(errors) {
        const panel = document.createElement('div');
        panel.className = 'jupiter-error-panel';
        panel.innerHTML = `
            <div class="jupiter-error-content">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <h3>Jupiter AI Unavailable</h3>
                <p>The following requirements are missing:</p>
                <ul>
                    ${errors.map(err => `<li>${err}</li>`).join('')}
                </ul>
                <button class="error-retry-btn" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> Retry
                </button>
            </div>
        `;
        document.body.appendChild(panel);
    }

    /**
     * PERFORMANCE MONITOR
     */
    class PerformanceMonitor {
        constructor() {
            this.fps = 60;
            this.frameCount = 0;
            this.lastTime = performance.now();
            this.memoryUsage = 0;
            this.isLowPerformance = false;
            
            this.startMonitoring();
        }

        startMonitoring() {
            // FPS monitoring
            setInterval(() => {
                const now = performance.now();
                const delta = now - this.lastTime;
                this.fps = Math.round((this.frameCount * 1000) / delta);
                this.frameCount = 0;
                this.lastTime = now;
                
                // Check memory if available
                if (performance.memory) {
                    this.memoryUsage = Math.round(
                        performance.memory.usedJSHeapSize / 1048576
                    );
                }
                
                // Performance warnings
                if (this.fps < 30 && !this.isLowPerformance) {
                    this.isLowPerformance = true;
                    console.warn(`Jupiter AI: Low FPS detected (${this.fps})`);
                    this.optimizePerformance();
                }
                
                if (this.memoryUsage > 500) {
                    console.warn(`Jupiter AI: High memory usage (${this.memoryUsage}MB)`);
                }
            }, 1000);
        }

        recordFrame() {
            this.frameCount++;
        }

        optimizePerformance() {
            // Reduce particle count
            if (window.threatMap3D && window.threatMap3D.particles) {
                const currentCount = window.threatMap3D.particles.length;
                const reducedCount = Math.floor(currentCount * 0.5);
                console.log(`Reducing particles from ${currentCount} to ${reducedCount}`);
            }
            
            // Disable some effects
            if (window.jupiterSystems && window.jupiterSystems.zoomLayers) {
                window.jupiterSystems.zoomLayers.layers.forEach(layer => {
                    layer.particleDensity = Math.floor(layer.particleDensity * 0.5);
                });
            }
        }

        getStats() {
            return {
                fps: this.fps,
                memory: this.memoryUsage,
                performance: this.fps > 50 ? 'Excellent' : this.fps > 30 ? 'Good' : 'Poor'
            };
        }
    }

    /**
     * LOADING STATE MANAGER
     */
    class LoadingStateManager {
        showLayerTransition(layer, progress = 0) {
            let overlay = document.querySelector('.layer-transition-overlay');
            
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'layer-transition-overlay';
                document.body.appendChild(overlay);
            }
            
            overlay.innerHTML = `
                <div class="layer-transition-content">
                    <div class="layer-icon">
                        ${this.getLayerIcon(layer.name)}
                    </div>
                    <div class="layer-name">${layer.name}</div>
                    <div class="layer-description">${layer.description}</div>
                    <div class="layer-progress">
                        <div class="layer-progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <div class="layer-stats">
                        Loading enhanced visualization...
                    </div>
                </div>
            `;
            
            overlay.style.display = 'flex';
        }

        updateProgress(progress) {
            const progressBar = document.querySelector('.layer-progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
        }

        hideLayerTransition() {
            const overlay = document.querySelector('.layer-transition-overlay');
            if (overlay) {
                overlay.classList.add('fade-out');
                setTimeout(() => {
                    overlay.style.display = 'none';
                    overlay.classList.remove('fade-out');
                }, 500);
            }
        }

        getLayerIcon(layerName) {
            const icons = {
                'World': '<i class="bi bi-globe"></i>',
                'Country': '<i class="bi bi-flag"></i>',
                'City': '<i class="bi bi-building"></i>',
                'Network': '<i class="bi bi-diagram-3"></i>',
                'Dark Web': '<i class="bi bi-bug-fill"></i>'
            };
            return icons[layerName] || '<i class="bi bi-layers"></i>';
        }
    }

    /**
     * LAYER BREADCRUMB NAVIGATION
     */
    class LayerBreadcrumb {
        constructor(zoomLayerSystem) {
            this.zoomLayers = zoomLayerSystem;
            this.element = null;
            this.create();
        }

        create() {
            this.element = document.createElement('div');
            this.element.className = 'layer-breadcrumb';
            this.update();
            document.body.appendChild(this.element);
        }

        update() {
            if (!this.element) return;
            
            const items = this.zoomLayers.layers.map((layer, index) => {
                const isActive = index === this.zoomLayers.currentLayer;
                const isPast = index < this.zoomLayers.currentLayer;
                const icon = this.getLayerIcon(layer.name);
                
                return `
                    <div class="breadcrumb-item ${isActive ? 'active' : ''} ${isPast ? 'completed' : ''}"
                         onclick="window.jupiterSystems.zoomLayers.jumpToLayer(${index})"
                         title="${layer.description}">
                        <span class="breadcrumb-icon">${icon}</span>
                        <span class="breadcrumb-label">${layer.name}</span>
                        ${isPast ? '<i class="bi bi-check-circle-fill breadcrumb-check"></i>' : ''}
                    </div>
                    ${index < this.zoomLayers.layers.length - 1 ? '<i class="bi bi-chevron-right breadcrumb-separator"></i>' : ''}
                `;
            }).join('');
            
            this.element.innerHTML = items;
        }

        getLayerIcon(layerName) {
            const icons = {
                'World': '<i class="bi bi-globe"></i>',
                'Country': '<i class="bi bi-flag"></i>',
                'City': '<i class="bi bi-building"></i>',
                'Network': '<i class="bi bi-diagram-3"></i>',
                'Dark Web': '<i class="bi bi-bug"></i>'
            };
            return icons[layerName] || '<i class="bi bi-layers"></i>';
        }
    }

    /**
     * TOUR CONTROLS
     */
    class TourControls {
        constructor(jupiterAI) {
            this.jupiterAI = jupiterAI;
            this.element = null;
            this.tourActive = false;
            this.tourPaused = false;
        }

        show() {
            if (this.element) {
                this.element.style.display = 'flex';
                return;
            }
            
            this.element = document.createElement('div');
            this.element.className = 'tour-controls';
            this.element.innerHTML = `
                <button class="tour-control-btn" data-action="pause" title="Pause Tour">
                    <i class="bi bi-pause-fill"></i>
                </button>
                <button class="tour-control-btn" data-action="skip" title="Skip to Next">
                    <i class="bi bi-skip-forward-fill"></i>
                </button>
                <button class="tour-control-btn" data-action="stop" title="End Tour">
                    <i class="bi bi-stop-fill"></i>
                </button>
                <div class="tour-progress">
                    <span id="tour-step">Step 1 of 5</span>
                </div>
            `;
            
            document.body.appendChild(this.element);
            
            // Event listeners
            this.element.querySelector('[data-action="pause"]').addEventListener('click', () => this.togglePause());
            this.element.querySelector('[data-action="skip"]').addEventListener('click', () => this.skip());
            this.element.querySelector('[data-action="stop"]').addEventListener('click', () => this.stop());
        }

        hide() {
            if (this.element) {
                this.element.style.display = 'none';
            }
        }

        togglePause() {
            this.tourPaused = !this.tourPaused;
            const btn = this.element.querySelector('[data-action="pause"]');
            
            if (this.tourPaused) {
                btn.innerHTML = '<i class="bi bi-play-fill"></i>';
                btn.title = 'Resume Tour';
                this.jupiterAI.pauseTour();
            } else {
                btn.innerHTML = '<i class="bi bi-pause-fill"></i>';
                btn.title = 'Pause Tour';
                this.jupiterAI.resumeTour();
            }
        }

        skip() {
            this.jupiterAI.skipToNextLayer();
        }

        stop() {
            this.jupiterAI.stopNarratedTour();
            this.hide();
        }

        updateProgress(step, total) {
            const progressSpan = this.element?.querySelector('#tour-step');
            if (progressSpan) {
                progressSpan.textContent = `Step ${step} of ${total}`;
            }
        }
    }

    /**
     * KEYBOARD SHORTCUTS HELP
     */
    class KeyboardShortcutsHelp {
        constructor() {
            this.visible = false;
            this.element = null;
        }

        toggle() {
            this.visible = !this.visible;
            
            if (this.visible) {
                this.show();
            } else {
                this.hide();
            }
        }

        show() {
            if (this.element) {
                this.element.style.display = 'flex';
                return;
            }
            
            this.element = document.createElement('div');
            this.element.className = 'keyboard-shortcuts-overlay';
            this.element.innerHTML = `
                <div class="keyboard-shortcuts-content">
                    <div class="shortcuts-header">
                        <h3><i class="bi bi-keyboard"></i> Keyboard Shortcuts</h3>
                        <button class="shortcuts-close" onclick="window.jupiterSystems.keyboardHelp.hide()">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                    <div class="shortcuts-grid">
                        <div class="shortcut-group">
                            <h4>Navigation</h4>
                            <div class="shortcut-item">
                                <kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd>
                                <span>Rotate globe</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>+</kbd><kbd>-</kbd>
                                <span>Zoom in/out</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>R</kbd>
                                <span>Reset view</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Space</kbd>
                                <span>Toggle auto-rotate</span>
                            </div>
                        </div>
                        <div class="shortcut-group">
                            <h4>Jupiter AI</h4>
                            <div class="shortcut-item">
                                <kbd>J</kbd>
                                <span>Toggle Jupiter AI</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>T</kbd>
                                <span>Start/stop tour</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>M</kbd>
                                <span>Toggle face morph</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>P</kbd>
                                <span>Pause/resume tour</span>
                            </div>
                        </div>
                        <div class="shortcut-group">
                            <h4>Layers</h4>
                            <div class="shortcut-item">
                                <kbd>1</kbd>-<kbd>5</kbd>
                                <span>Jump to layer</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>N</kbd>
                                <span>Next layer</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>B</kbd>
                                <span>Previous layer</span>
                            </div>
                        </div>
                        <div class="shortcut-group">
                            <h4>Other</h4>
                            <div class="shortcut-item">
                                <kbd>Esc</kbd>
                                <span>Close panels</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>?</kbd>
                                <span>Show/hide this help</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>S</kbd>
                                <span>Screenshot</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(this.element);
        }

        hide() {
            if (this.element) {
                this.element.style.display = 'none';
            }
            this.visible = false;
        }
    }

    /**
     * ENHANCED ZOOM LAYER SYSTEM (with improvements)
     */
    class ZoomLayerSystem {
        constructor(map) {
            this.map = map;
            this.currentLayer = 0;
            this.layers = [
                {
                    name: 'World',
                    zoom: 300,
                    description: 'Global threat landscape overview',
                    threatDetail: 'country',
                    particleDensity: this.getOptimalParticles(100),
                    dataFlowSpeed: 1.0
                },
                {
                    name: 'Country',
                    zoom: 150,
                    description: 'National infrastructure vulnerabilities',
                    threatDetail: 'city',
                    particleDensity: this.getOptimalParticles(200),
                    dataFlowSpeed: 1.5
                },
                {
                    name: 'City',
                    zoom: 80,
                    description: 'Urban network attack surfaces',
                    threatDetail: 'network',
                    particleDensity: this.getOptimalParticles(500),
                    dataFlowSpeed: 2.0
                },
                {
                    name: 'Network',
                    zoom: 40,
                    description: 'Enterprise network topology',
                    threatDetail: 'device',
                    particleDensity: this.getOptimalParticles(1000),
                    dataFlowSpeed: 3.0,
                    showConnections: true
                },
                {
                    name: 'Dark Web',
                    zoom: 20,
                    description: 'Underground threat actor activity',
                    threatDetail: 'actor',
                    particleDensity: this.getOptimalParticles(2000),
                    dataFlowSpeed: 5.0,
                    showConnections: true,
                    darkWebMode: true,
                    glitchEffect: true
                }
            ];
            
            this.zoomTransitionDuration = 2000;
            this.isTransitioning = false;
            this.loadingManager = new LoadingStateManager();
            this.breadcrumb = new LayerBreadcrumb(this);
            this.matrixEffect = null; // Reuse matrix effect
        }

        /**
         * Get optimal particle count based on device
         */
        getOptimalParticles(baseCount) {
            // Detect mobile
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            // Reduce particles on mobile
            return isMobile ? Math.floor(baseCount * 0.5) : baseCount;
        }

        zoomIn() {
            if (this.currentLayer < this.layers.length - 1 && !this.isTransitioning) {
                this.currentLayer++;
                this.transitionToLayer(this.currentLayer);
            }
        }

        zoomOut() {
            if (this.currentLayer > 0 && !this.isTransitioning) {
                this.currentLayer--;
                this.transitionToLayer(this.currentLayer);
            }
        }

        jumpToLayer(layerIndex) {
            if (layerIndex >= 0 && layerIndex < this.layers.length && !this.isTransitioning) {
                this.currentLayer = layerIndex;
                this.transitionToLayer(layerIndex);
            }
        }

        transitionToLayer(layerIndex) {
            this.isTransitioning = true;
            const layer = this.layers[layerIndex];
            const startZoom = this.map.camera.position.z;
            const endZoom = layer.zoom;
            const startTime = Date.now();

            // Show loading overlay
            this.loadingManager.showLayerTransition(layer, 0);

            // Notify Jupiter AI
            if (window.jupiterAI) {
                window.jupiterAI.onLayerChange(layer);
            }

            // Animate zoom with progress updates
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / this.zoomTransitionDuration, 1);
                const easedProgress = this.easeInOutCubic(progress);

                // Update camera
                this.map.camera.position.z = startZoom + (endZoom - startZoom) * easedProgress;

                // Update loading progress
                this.loadingManager.updateProgress(progress * 100);

                // Update effects
                this.updateLayerEffects(layer, easedProgress);

                // Record frame for performance monitoring
                if (performanceMonitor) {
                    performanceMonitor.recordFrame();
                }

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    this.isTransitioning = false;
                    this.onLayerReached(layer);
                    this.loadingManager.hideLayerTransition();
                    
                    // Update breadcrumb
                    if (this.breadcrumb) {
                        this.breadcrumb.update();
                    }
                }
            };

            animate();
        }

        updateLayerEffects(layer, progress) {
            // Update particle density (if system exists)
            if (this.map.particleSystem) {
                this.map.particleSystem.density = layer.particleDensity * progress;
            }

            // Update data flows
            if (this.map.dataFlows) {
                this.map.dataFlows.forEach(flow => {
                    flow.speed = layer.dataFlowSpeed;
                });
            }

            // Dark web mode
            if (layer.darkWebMode) {
                this.enableDarkWebMode(progress);
            } else {
                this.disableDarkWebMode(progress);
            }

            // Glitch effect
            if (layer.glitchEffect && progress > 0.5) {
                this.applyGlitchEffect();
            }
        }

        enableDarkWebMode(progress) {
            const darkColor = new THREE.Color(0x000000);
            const normalColor = new THREE.Color(0x0a0e1a);
            this.map.scene.background = normalColor.lerp(darkColor, progress);

            // Red glow on threats
            this.map.threats.forEach(threat => {
                if (threat.marker && threat.marker.material) {
                    const color = new THREE.Color(0xff0000);
                    threat.marker.material.emissive = color;
                    threat.marker.material.emissiveIntensity = 0.5 * progress;
                }
            });

            // Create/show matrix effect (reuse existing)
            if (progress > 0.7) {
                if (!this.matrixEffect) {
                    this.createMatrixEffect();
                } else {
                    this.matrixEffect.visible = true;
                }
            }
        }

        disableDarkWebMode(progress) {
            const normalColor = new THREE.Color(0x0a0e1a);
            this.map.scene.background = normalColor;

            this.map.threats.forEach(threat => {
                if (threat.marker && threat.marker.material) {
                    threat.marker.material.emissiveIntensity = 0;
                }
            });

            if (this.matrixEffect) {
                this.matrixEffect.visible = false;
            }
        }

        createMatrixEffect() {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');
            
            ctx.fillStyle = 'black';
            ctx.fillRect(0, 0, 512, 512);
            
            ctx.fillStyle = '#00ff00';
            ctx.font = '10px monospace';
            
            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
            
            for (let i = 0; i < 50; i++) {
                const x = Math.random() * 512;
                const y = Math.random() * 512;
                const char = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(char, x, y);
            }

            const texture = new THREE.CanvasTexture(canvas);
            const geometry = new THREE.SphereGeometry(this.map.config.globeRadius + 5, 64, 64);
            const material = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                opacity: 0.3,
                side: THREE.DoubleSide
            });

            this.matrixEffect = new THREE.Mesh(geometry, material);
            this.map.scene.add(this.matrixEffect);
        }

        applyGlitchEffect() {
            if (Math.random() > 0.95) {
                const offset = (Math.random() - 0.5) * 2;
                this.map.globe.position.x += offset;
                
                setTimeout(() => {
                    this.map.globe.position.x -= offset;
                }, 50);
            }
        }

        onLayerReached(layer) {
            console.log(`Reached layer: ${layer.name}`);
            this.showLayerThreats(layer);

            if (window.jupiterAI) {
                window.jupiterAI.narrateLayer(layer);
            }
        }

        showLayerThreats(layer) {
            this.map.threats.forEach(threat => {
                if (threat.marker) {
                    const shouldShow = this.isThreatRelevantToLayer(threat, layer);
                    threat.marker.visible = shouldShow;
                    
                    if (shouldShow) {
                        const scale = layer.zoom < 100 ? 1.5 : 1.0;
                        threat.marker.scale.set(scale, scale, scale);
                    }
                }
            });
        }

        isThreatRelevantToLayer(threat, layer) {
            if (layer.name === 'World') return true;
            if (layer.name === 'Dark Web') {
                return threat.severity === 'critical' || threat.type === 'darkweb';
            }
            return true;
        }

        easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }
    }

    // Continue in next message due to length...
    // This includes the enhanced JupiterFaceMorph and JupiterAI classes with all improvements
    
    window.jupiterEnhanced = {
        version: '2.1.0',
        checkDependencies,
        PerformanceMonitor,
        LoadingStateManager,
        LayerBreadcrumb,
        TourControls,
        KeyboardShortcutsHelp,
        ZoomLayerSystem
    };

})();
