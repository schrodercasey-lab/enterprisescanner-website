/**
 * JUPITER AI INTEGRATION - Revolutionary 3D Threat Map Control
 * ============================================================
 * 
 * Features:
 * 1. AI-Narrated Threat Tours - Jupiter guides users through threats
 * 2. Multi-Layer Zoom System - World → Country → City → Network → Dark Web
 * 3. Globe-to-Face Morph - Transform map into Jupiter's face
 * 4. Admin Console Control - Remote control from Jupiter Dashboard
 * 5. Voice Synthesis - Jupiter speaks threat information
 * 
 * @version 2.0.0
 * @author Enterprise Scanner Team
 * @patent-pending Advanced AI Visualization Control
 */

(function() {
    'use strict';

    /**
     * ZOOM LAYER SYSTEM
     * Progressive depth levels from world view to dark web
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
                    particleDensity: 100,
                    dataFlowSpeed: 1.0
                },
                {
                    name: 'Country',
                    zoom: 150,
                    description: 'National infrastructure vulnerabilities',
                    threatDetail: 'city',
                    particleDensity: 200,
                    dataFlowSpeed: 1.5
                },
                {
                    name: 'City',
                    zoom: 80,
                    description: 'Urban network attack surfaces',
                    threatDetail: 'network',
                    particleDensity: 500,
                    dataFlowSpeed: 2.0
                },
                {
                    name: 'Network',
                    zoom: 40,
                    description: 'Enterprise network topology',
                    threatDetail: 'device',
                    particleDensity: 1000,
                    dataFlowSpeed: 3.0,
                    showConnections: true
                },
                {
                    name: 'Dark Web',
                    zoom: 20,
                    description: 'Underground threat actor activity',
                    threatDetail: 'actor',
                    particleDensity: 2000,
                    dataFlowSpeed: 5.0,
                    showConnections: true,
                    darkWebMode: true,
                    glitchEffect: true
                }
            ];
            
            this.zoomTransitionDuration = 2000; // ms
            this.isTransitioning = false;
        }

        /**
         * Zoom to next layer
         */
        zoomIn() {
            if (this.currentLayer < this.layers.length - 1 && !this.isTransitioning) {
                this.currentLayer++;
                this.transitionToLayer(this.currentLayer);
            }
        }

        /**
         * Zoom to previous layer
         */
        zoomOut() {
            if (this.currentLayer > 0 && !this.isTransitioning) {
                this.currentLayer--;
                this.transitionToLayer(this.currentLayer);
            }
        }

        /**
         * Jump to specific layer
         */
        jumpToLayer(layerIndex) {
            if (layerIndex >= 0 && layerIndex < this.layers.length && !this.isTransitioning) {
                this.currentLayer = layerIndex;
                this.transitionToLayer(layerIndex);
            }
        }

        /**
         * Smooth transition to target layer
         */
        transitionToLayer(layerIndex) {
            this.isTransitioning = true;
            const layer = this.layers[layerIndex];
            const startZoom = this.map.camera.position.z;
            const endZoom = layer.zoom;
            const startTime = Date.now();

            // Notify Jupiter AI
            if (window.jupiterAI) {
                window.jupiterAI.onLayerChange(layer);
            }

            // Display layer info
            this.showLayerTransition(layer);

            // Animate zoom
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / this.zoomTransitionDuration, 1);
                const easedProgress = this.easeInOutCubic(progress);

                // Update camera position
                this.map.camera.position.z = startZoom + (endZoom - startZoom) * easedProgress;

                // Update visual effects based on layer
                this.updateLayerEffects(layer, easedProgress);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    this.isTransitioning = false;
                    this.onLayerReached(layer);
                }
            };

            animate();
        }

        /**
         * Update visual effects for current layer
         */
        updateLayerEffects(layer, progress) {
            // Update particle density
            if (this.map.particleSystem) {
                this.map.particleSystem.density = layer.particleDensity * progress;
            }

            // Update data flow speed
            if (this.map.dataFlows) {
                this.map.dataFlows.forEach(flow => {
                    flow.speed = layer.dataFlowSpeed;
                });
            }

            // Enable dark web mode
            if (layer.darkWebMode) {
                this.enableDarkWebMode(progress);
            } else {
                this.disableDarkWebMode(progress);
            }

            // Add glitch effect for deep layers
            if (layer.glitchEffect && progress > 0.5) {
                this.applyGlitchEffect();
            }
        }

        /**
         * Enable dark web visual mode
         */
        enableDarkWebMode(progress) {
            // Change scene background to dark
            const darkColor = new THREE.Color(0x000000);
            const normalColor = new THREE.Color(0x0a0e1a);
            this.map.scene.background = normalColor.lerp(darkColor, progress);

            // Add red/purple glow to threats
            this.map.threats.forEach(threat => {
                if (threat.marker && threat.marker.material) {
                    const color = new THREE.Color(0xff0000);
                    threat.marker.material.emissive = color;
                    threat.marker.material.emissiveIntensity = 0.5 * progress;
                }
            });

            // Add matrix-style falling characters
            if (progress > 0.7 && !this.matrixEffect) {
                this.createMatrixEffect();
            }
        }

        /**
         * Disable dark web mode
         */
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

        /**
         * Create Matrix-style falling characters effect
         */
        createMatrixEffect() {
            // Create canvas texture with falling characters
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

        /**
         * Apply glitch/distortion effect
         */
        applyGlitchEffect() {
            if (Math.random() > 0.95) { // Random glitch
                const offset = (Math.random() - 0.5) * 2;
                this.map.globe.position.x += offset;
                
                setTimeout(() => {
                    this.map.globe.position.x -= offset;
                }, 50);
            }
        }

        /**
         * Show layer transition UI
         */
        showLayerTransition(layer) {
            const existingOverlay = document.querySelector('.layer-transition-overlay');
            if (existingOverlay) {
                existingOverlay.remove();
            }

            const overlay = document.createElement('div');
            overlay.className = 'layer-transition-overlay';
            overlay.innerHTML = `
                <div class="layer-transition-content">
                    <div class="layer-icon">
                        ${this.getLayerIcon(layer.name)}
                    </div>
                    <div class="layer-name">${layer.name}</div>
                    <div class="layer-description">${layer.description}</div>
                    <div class="layer-progress">
                        <div class="layer-progress-bar"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            // Animate progress bar
            const progressBar = overlay.querySelector('.layer-progress-bar');
            progressBar.style.width = '0%';
            
            setTimeout(() => {
                progressBar.style.width = '100%';
            }, 50);

            // Remove after transition
            setTimeout(() => {
                overlay.classList.add('fade-out');
                setTimeout(() => overlay.remove(), 500);
            }, this.zoomTransitionDuration);
        }

        /**
         * Get icon for layer
         */
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

        /**
         * Called when layer is reached
         */
        onLayerReached(layer) {
            console.log(`Reached layer: ${layer.name}`);
            
            // Show layer-specific threats
            this.showLayerThreats(layer);

            // Trigger Jupiter narration
            if (window.jupiterAI) {
                window.jupiterAI.narrateLayer(layer);
            }
        }

        /**
         * Show threats relevant to current layer
         */
        showLayerThreats(layer) {
            // Filter and highlight threats based on layer detail level
            this.map.threats.forEach(threat => {
                if (threat.marker) {
                    const shouldShow = this.isThreatRelevantToLayer(threat, layer);
                    threat.marker.visible = shouldShow;
                    
                    if (shouldShow) {
                        // Scale based on importance at this layer
                        const scale = layer.zoom < 100 ? 1.5 : 1.0;
                        threat.marker.scale.set(scale, scale, scale);
                    }
                }
            });
        }

        /**
         * Check if threat is relevant to current layer
         */
        isThreatRelevantToLayer(threat, layer) {
            // At world level, show all threats
            if (layer.name === 'World') return true;
            
            // At deeper levels, filter by severity and type
            if (layer.name === 'Dark Web') {
                return threat.severity === 'critical' || threat.type === 'darkweb';
            }
            
            return true; // Show all for now
        }

        /**
         * Easing function
         */
        easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }
    }

    /**
     * JUPITER FACE MORPH SYSTEM
     * Transform globe into Jupiter AI's face
     */
    class JupiterFaceMorph {
        constructor(map) {
            this.map = map;
            this.isFaceMode = false;
            this.morphProgress = 0;
            this.faceGeometry = null;
            this.faceMesh = null;
        }

        /**
         * Toggle between globe and face mode
         */
        toggle() {
            if (this.isFaceMode) {
                this.morphToGlobe();
            } else {
                this.morphToFace();
            }
        }

        /**
         * Morph globe into Jupiter's face
         */
        morphToFace() {
            this.isFaceMode = true;
            
            // Create face geometry if not exists
            if (!this.faceMesh) {
                this.createFaceMesh();
            }

            // Show transition message
            if (window.jupiterAI) {
                window.jupiterAI.speak("Initializing visual interface...");
            }

            // Animate morph
            this.animateMorph(0, 1, 3000);
        }

        /**
         * Morph face back to globe
         */
        morphToGlobe() {
            this.isFaceMode = false;
            
            if (window.jupiterAI) {
                window.jupiterAI.speak("Returning to global threat view...");
            }

            this.animateMorph(1, 0, 3000);
        }

        /**
         * Create Jupiter face mesh
         */
        createFaceMesh() {
            // Create face geometry (similar to globe but with face features)
            const geometry = new THREE.SphereGeometry(
                this.map.config.globeRadius,
                128, // Higher resolution for face details
                128
            );

            // Create face texture with animated matrix effect
            const canvas = document.createElement('canvas');
            canvas.width = 1024;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');

            // Create gradient background (Jupiter's "skin")
            const gradient = ctx.createRadialGradient(512, 512, 100, 512, 512, 512);
            gradient.addColorStop(0, '#00ff88');
            gradient.addColorStop(0.5, '#0088ff');
            gradient.addColorStop(1, '#0044ff');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 1024, 1024);

            // Draw face features with data streams
            this.drawFaceFeatures(ctx);

            const texture = new THREE.CanvasTexture(canvas);
            
            const material = new THREE.MeshPhongMaterial({
                map: texture,
                emissive: new THREE.Color(0x0088ff),
                emissiveIntensity: 0.3,
                shininess: 100,
                transparent: true,
                opacity: 0
            });

            this.faceMesh = new THREE.Mesh(geometry, material);
            this.faceMesh.position.copy(this.map.globe.position);
            this.map.scene.add(this.faceMesh);

            // Animate face texture (pulsing, data streams)
            this.animateFaceTexture(ctx, texture);
        }

        /**
         * Draw face features with cybernetic style
         */
        drawFaceFeatures(ctx) {
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 3;

            // Eyes (data visualization nodes)
            ctx.beginPath();
            ctx.arc(350, 400, 50, 0, Math.PI * 2);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.arc(674, 400, 50, 0, Math.PI * 2);
            ctx.stroke();

            // Eye centers (threat indicators)
            ctx.fillStyle = '#ff0000';
            ctx.beginPath();
            ctx.arc(350, 400, 20, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(674, 400, 20, 0, Math.PI * 2);
            ctx.fill();

            // Mouth (waveform/audio visualizer)
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(300, 650);
            for (let x = 300; x < 724; x += 20) {
                const y = 650 + Math.sin(x * 0.05) * 30;
                ctx.lineTo(x, y);
            }
            ctx.stroke();

            // Circuit board patterns
            ctx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
            ctx.lineWidth = 1;
            for (let i = 0; i < 100; i++) {
                const x1 = Math.random() * 1024;
                const y1 = Math.random() * 1024;
                const x2 = x1 + (Math.random() - 0.5) * 100;
                const y2 = y1 + (Math.random() - 0.5) * 100;
                
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }

            // Data points (threat nodes on face)
            ctx.fillStyle = '#ffff00';
            for (let i = 0; i < 50; i++) {
                const x = Math.random() * 1024;
                const y = Math.random() * 1024;
                const radius = Math.random() * 3 + 1;
                
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /**
         * Animate face texture continuously
         */
        animateFaceTexture(ctx, texture) {
            let frame = 0;
            
            const animate = () => {
                if (!this.isFaceMode && this.morphProgress === 0) {
                    return; // Stop animation when in globe mode
                }

                frame++;

                // Pulsing eyes
                const eyeGlow = 0.5 + Math.sin(frame * 0.1) * 0.5;
                ctx.fillStyle = `rgba(255, 0, 0, ${eyeGlow})`;
                ctx.beginPath();
                ctx.arc(350, 400, 20, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(674, 400, 20, 0, Math.PI * 2);
                ctx.fill();

                // Animated mouth waveform (speaking indicator)
                ctx.clearRect(280, 600, 464, 100);
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(300, 650);
                for (let x = 300; x < 724; x += 10) {
                    const y = 650 + Math.sin(x * 0.05 + frame * 0.1) * 30;
                    ctx.lineTo(x, y);
                }
                ctx.stroke();

                // Update texture
                texture.needsUpdate = true;

                requestAnimationFrame(animate);
            };

            animate();
        }

        /**
         * Animate morph transition
         */
        animateMorph(startProgress, endProgress, duration) {
            const startTime = Date.now();

            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easedProgress = this.easeInOutQuart(progress);

                this.morphProgress = startProgress + (endProgress - startProgress) * easedProgress;

                // Crossfade between globe and face
                if (this.map.globe && this.map.globe.material) {
                    this.map.globe.material.opacity = 1 - this.morphProgress;
                }
                
                if (this.faceMesh && this.faceMesh.material) {
                    this.faceMesh.material.opacity = this.morphProgress;
                }

                // Hide/show threats during morph
                this.map.threats.forEach(threat => {
                    if (threat.marker) {
                        threat.marker.visible = this.morphProgress < 0.5;
                    }
                });

                // Show data streams on face
                if (this.morphProgress > 0.5) {
                    this.showDataStreamsOnFace();
                }

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };

            animate();
        }

        /**
         * Show data streams flowing across face
         */
        showDataStreamsOnFace() {
            // Create particle streams from eyes to mouth (data processing visualization)
            if (!this.faceDataStreams) {
                this.faceDataStreams = [];
                
                for (let i = 0; i < 20; i++) {
                    const geometry = new THREE.SphereGeometry(0.5, 8, 8);
                    const material = new THREE.MeshBasicMaterial({
                        color: 0x00ffff,
                        transparent: true,
                        opacity: 0.6
                    });
                    const particle = new THREE.Mesh(geometry, material);
                    
                    this.faceDataStreams.push({
                        mesh: particle,
                        progress: Math.random()
                    });
                    
                    this.map.scene.add(particle);
                }
            }

            // Animate particles along face contours
            this.faceDataStreams.forEach(stream => {
                stream.progress += 0.01;
                if (stream.progress > 1) stream.progress = 0;

                // Path from eye to mouth
                const angle = stream.progress * Math.PI;
                const x = Math.cos(angle) * this.map.config.globeRadius * 0.8;
                const y = Math.sin(angle) * this.map.config.globeRadius * 0.8;
                const z = this.map.config.globeRadius + 2;

                stream.mesh.position.set(x, y, z);
                stream.mesh.visible = this.morphProgress > 0.5;
            });
        }

        /**
         * Easing function
         */
        easeInOutQuart(t) {
            return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2;
        }
    }

    /**
     * JUPITER AI CONTROLLER
     * AI narration and control system
     */
    class JupiterAI {
        constructor(map) {
            this.map = map;
            this.speaking = false;
            this.speechSynthesis = window.speechSynthesis;
            this.voice = null;
            this.isActive = false;
            this.narrativeMode = false;
            
            this.setupVoice();
            this.setupControlPanel();
        }

        /**
         * Setup voice synthesis
         */
        setupVoice() {
            if (this.speechSynthesis) {
                // Wait for voices to load
                if (this.speechSynthesis.getVoices().length === 0) {
                    this.speechSynthesis.addEventListener('voiceschanged', () => {
                        this.selectBestVoice();
                    });
                } else {
                    this.selectBestVoice();
                }
            }
        }

        /**
         * Select best voice for Jupiter
         */
        selectBestVoice() {
            const voices = this.speechSynthesis.getVoices();
            
            // Prefer UK English male voices for professional sound
            this.voice = voices.find(voice => 
                voice.name.includes('UK') && voice.name.includes('Male')
            ) || voices.find(voice => 
                voice.lang === 'en-GB'
            ) || voices[0];
        }

        /**
         * Speak text with Jupiter's voice
         */
        speak(text, options = {}) {
            if (!this.speechSynthesis || !this.voice) {
                console.log('Jupiter AI:', text);
                this.displaySubtitle(text);
                return;
            }

            // Cancel any ongoing speech
            this.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.voice = this.voice;
            utterance.rate = options.rate || 1.0;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || 1.0;

            utterance.onstart = () => {
                this.speaking = true;
                this.displaySubtitle(text);
            };

            utterance.onend = () => {
                this.speaking = false;
                this.hideSubtitle();
            };

            this.speechSynthesis.speak(utterance);
        }

        /**
         * Display subtitle for Jupiter's speech
         */
        displaySubtitle(text) {
            let subtitle = document.querySelector('.jupiter-subtitle');
            if (!subtitle) {
                subtitle = document.createElement('div');
                subtitle.className = 'jupiter-subtitle';
                document.body.appendChild(subtitle);
            }

            subtitle.textContent = text;
            subtitle.classList.add('visible');
        }

        /**
         * Hide subtitle
         */
        hideSubtitle() {
            const subtitle = document.querySelector('.jupiter-subtitle');
            if (subtitle) {
                subtitle.classList.remove('visible');
            }
        }

        /**
         * Start AI-narrated tour
         */
        startNarratedTour() {
            this.narrativeMode = true;
            this.speak("Welcome. I am Jupiter, your cybersecurity intelligence system. Let me guide you through the global threat landscape.");

            setTimeout(() => {
                this.narrateCurrentView();
            }, 5000);
        }

        /**
         * Stop narrated tour
         */
        stopNarratedTour() {
            this.narrativeMode = false;
            this.speechSynthesis.cancel();
            this.speak("Tour concluded. Feel free to explore manually.");
        }

        /**
         * Narrate current view
         */
        narrateCurrentView() {
            if (!this.narrativeMode) return;

            const layer = this.map.zoomLayers ? this.map.zoomLayers.layers[this.map.zoomLayers.currentLayer] : null;
            
            if (layer) {
                this.narrateLayer(layer);
            } else {
                const threatCount = this.map.threats.length;
                const criticalCount = this.map.threats.filter(t => t.severity === 'critical').length;
                
                this.speak(`Currently monitoring ${threatCount} threats globally, including ${criticalCount} critical incidents requiring immediate attention.`);
            }

            // Continue tour
            setTimeout(() => {
                if (this.narrativeMode && this.map.zoomLayers) {
                    this.map.zoomLayers.zoomIn();
                    setTimeout(() => this.narrateCurrentView(), 8000);
                }
            }, 6000);
        }

        /**
         * Narrate specific layer information
         */
        narrateLayer(layer) {
            const narratives = {
                'World': "At the global level, we observe threat distribution across continents. Notice the concentration of attacks in major technology hubs.",
                'Country': "Zooming to national infrastructure. Each nation faces unique vulnerabilities based on their digital footprint and geopolitical exposure.",
                'City': "At the urban level, we see enterprise networks and critical infrastructure. Metropolitan areas are prime targets for sophisticated attacks.",
                'Network': "Now examining enterprise network topology. These connections represent potential attack vectors and lateral movement paths.",
                'Dark Web': "Entering the dark web layer. This is where threat actors coordinate, where zero-day exploits are traded, and where attribution becomes nearly impossible."
            };

            const narrative = narratives[layer.name] || layer.description;
            this.speak(narrative);
        }

        /**
         * Called when layer changes
         */
        onLayerChange(layer) {
            if (this.narrativeMode) {
                setTimeout(() => {
                    this.narrateLayer(layer);
                }, 1000);
            }
        }

        /**
         * Highlight specific threat with narration
         */
        highlightThreat(threat) {
            this.speak(`Threat detected: ${threat.location}. Severity level ${threat.severity}. Attack type: ${threat.type}. Immediate investigation recommended.`);
            
            // Focus camera on threat
            if (this.map.camera && threat.marker) {
                this.focusOnPosition(threat.marker.position);
            }
        }

        /**
         * Focus camera on position
         */
        focusOnPosition(position) {
            const startPos = this.map.camera.position.clone();
            const endPos = new THREE.Vector3(
                position.x * 1.5,
                position.y * 1.5,
                position.z * 1.5
            );
            
            const duration = 2000;
            const startTime = Date.now();

            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easedProgress = this.easeInOutCubic(progress);

                this.map.camera.position.lerpVectors(startPos, endPos, easedProgress);
                this.map.camera.lookAt(position);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };

            animate();
        }

        /**
         * Setup Jupiter control panel UI
         */
        setupControlPanel() {
            const panel = document.createElement('div');
            panel.className = 'jupiter-control-panel';
            panel.innerHTML = `
                <div class="jupiter-header">
                    <div class="jupiter-avatar">
                        <i class="bi bi-cpu"></i>
                    </div>
                    <div class="jupiter-status">
                        <div class="jupiter-name">JUPITER AI</div>
                        <div class="jupiter-state">Standby</div>
                    </div>
                </div>
                <div class="jupiter-controls">
                    <button class="jupiter-btn" data-action="activate">
                        <i class="bi bi-power"></i> Activate
                    </button>
                    <button class="jupiter-btn" data-action="tour" disabled>
                        <i class="bi bi-play-circle"></i> Start Tour
                    </button>
                    <button class="jupiter-btn" data-action="morph" disabled>
                        <i class="bi bi-person"></i> Face Mode
                    </button>
                    <button class="jupiter-btn" data-action="layer-up" disabled>
                        <i class="bi bi-zoom-in"></i> Zoom In
                    </button>
                    <button class="jupiter-btn" data-action="layer-down" disabled>
                        <i class="bi bi-zoom-out"></i> Zoom Out
                    </button>
                </div>
                <div class="jupiter-info">
                    <div class="jupiter-layer">Layer: <span id="current-layer">World</span></div>
                    <div class="jupiter-mode">Mode: <span id="current-mode">Globe</span></div>
                </div>
            `;

            document.body.appendChild(panel);

            // Setup event listeners
            panel.querySelector('[data-action="activate"]').addEventListener('click', () => {
                this.toggleActivation();
            });

            panel.querySelector('[data-action="tour"]').addEventListener('click', () => {
                if (this.narrativeMode) {
                    this.stopNarratedTour();
                } else {
                    this.startNarratedTour();
                }
                this.updateControlPanel();
            });

            panel.querySelector('[data-action="morph"]').addEventListener('click', () => {
                if (this.map.faceMorph) {
                    this.map.faceMorph.toggle();
                    this.updateControlPanel();
                }
            });

            panel.querySelector('[data-action="layer-up"]').addEventListener('click', () => {
                if (this.map.zoomLayers) {
                    this.map.zoomLayers.zoomIn();
                    this.updateControlPanel();
                }
            });

            panel.querySelector('[data-action="layer-down"]').addEventListener('click', () => {
                if (this.map.zoomLayers) {
                    this.map.zoomLayers.zoomOut();
                    this.updateControlPanel();
                }
            });
        }

        /**
         * Toggle Jupiter activation
         */
        toggleActivation() {
            this.isActive = !this.isActive;
            
            if (this.isActive) {
                this.speak("Jupiter AI systems online. All threat monitoring capabilities activated.");
            } else {
                this.speak("Entering standby mode.");
                this.stopNarratedTour();
            }

            this.updateControlPanel();
        }

        /**
         * Update control panel UI
         */
        updateControlPanel() {
            const panel = document.querySelector('.jupiter-control-panel');
            if (!panel) return;

            const stateElement = panel.querySelector('.jupiter-state');
            const activateBtn = panel.querySelector('[data-action="activate"]');
            const tourBtn = panel.querySelector('[data-action="tour"]');
            const morphBtn = panel.querySelector('[data-action="morph"]');
            const layerUpBtn = panel.querySelector('[data-action="layer-up"]');
            const layerDownBtn = panel.querySelector('[data-action="layer-down"]');
            const currentLayerSpan = panel.querySelector('#current-layer');
            const currentModeSpan = panel.querySelector('#current-mode');

            // Update state
            if (this.isActive) {
                stateElement.textContent = 'Active';
                stateElement.classList.add('active');
                activateBtn.innerHTML = '<i class="bi bi-power"></i> Deactivate';
                tourBtn.disabled = false;
                morphBtn.disabled = false;
                layerUpBtn.disabled = false;
                layerDownBtn.disabled = false;
            } else {
                stateElement.textContent = 'Standby';
                stateElement.classList.remove('active');
                activateBtn.innerHTML = '<i class="bi bi-power"></i> Activate';
                tourBtn.disabled = true;
                morphBtn.disabled = true;
                layerUpBtn.disabled = true;
                layerDownBtn.disabled = true;
            }

            // Update tour button
            if (this.narrativeMode) {
                tourBtn.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Tour';
                tourBtn.classList.add('active');
            } else {
                tourBtn.innerHTML = '<i class="bi bi-play-circle"></i> Start Tour';
                tourBtn.classList.remove('active');
            }

            // Update morph button
            if (this.map.faceMorph && this.map.faceMorph.isFaceMode) {
                morphBtn.innerHTML = '<i class="bi bi-globe"></i> Globe Mode';
                morphBtn.classList.add('active');
                currentModeSpan.textContent = 'Face';
            } else {
                morphBtn.innerHTML = '<i class="bi bi-person"></i> Face Mode';
                morphBtn.classList.remove('active');
                currentModeSpan.textContent = 'Globe';
            }

            // Update layer info
            if (this.map.zoomLayers) {
                const layer = this.map.zoomLayers.layers[this.map.zoomLayers.currentLayer];
                currentLayerSpan.textContent = layer.name;
            }
        }

        /**
         * Easing function
         */
        easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }
    }

    /**
     * ADMIN CONSOLE INTEGRATION
     * Allow Jupiter Dashboard to control the 3D map remotely
     */
    class AdminConsoleIntegration {
        constructor(map) {
            this.map = map;
            this.websocket = null;
            this.connected = false;
            this.messageQueue = [];
            
            this.setupWebSocket();
            this.setupMessageHandlers();
        }

        /**
         * Setup WebSocket connection to admin console
         */
        setupWebSocket() {
            // Mock WebSocket for demo (replace with real URL in production)
            const wsUrl = 'ws://localhost:8765/jupiter-control';
            
            try {
                this.websocket = new WebSocket(wsUrl);
                
                this.websocket.onopen = () => {
                    this.connected = true;
                    console.log('Connected to Jupiter Admin Console');
                    this.sendMessage({ type: 'handshake', client: '3d-threat-map' });
                    
                    // Process queued messages
                    while (this.messageQueue.length > 0) {
                        const msg = this.messageQueue.shift();
                        this.sendMessage(msg);
                    }
                };

                this.websocket.onmessage = (event) => {
                    this.handleMessage(JSON.parse(event.data));
                };

                this.websocket.onerror = (error) => {
                    console.log('WebSocket connection not available (expected in demo mode)');
                };

                this.websocket.onclose = () => {
                    this.connected = false;
                    console.log('Disconnected from Admin Console');
                    
                    // Attempt reconnect
                    setTimeout(() => this.setupWebSocket(), 5000);
                };
            } catch (error) {
                console.log('Admin Console integration in demo mode');
                this.setupMockConsole();
            }
        }

        /**
         * Setup mock console for demo
         */
        setupMockConsole() {
            // Create mock console commands
            window.jupiterConsole = {
                zoomIn: () => this.handleMessage({ type: 'zoom', direction: 'in' }),
                zoomOut: () => this.handleMessage({ type: 'zoom', direction: 'out' }),
                startTour: () => this.handleMessage({ type: 'tour', action: 'start' }),
                stopTour: () => this.handleMessage({ type: 'tour', action: 'stop' }),
                morphFace: () => this.handleMessage({ type: 'morph', mode: 'face' }),
                morphGlobe: () => this.handleMessage({ type: 'morph', mode: 'globe' }),
                highlightThreat: (id) => this.handleMessage({ type: 'highlight', threatId: id }),
                jumpToLayer: (layer) => this.handleMessage({ type: 'layer', name: layer })
            };

            console.log('Jupiter Console Commands available:');
            console.log('  window.jupiterConsole.zoomIn()');
            console.log('  window.jupiterConsole.zoomOut()');
            console.log('  window.jupiterConsole.startTour()');
            console.log('  window.jupiterConsole.morphFace()');
            console.log('  window.jupiterConsole.highlightThreat("THR-000001")');
        }

        /**
         * Setup message handlers
         */
        setupMessageHandlers() {
            this.handlers = {
                'zoom': this.handleZoomCommand.bind(this),
                'tour': this.handleTourCommand.bind(this),
                'morph': this.handleMorphCommand.bind(this),
                'highlight': this.handleHighlightCommand.bind(this),
                'layer': this.handleLayerCommand.bind(this),
                'speak': this.handleSpeakCommand.bind(this)
            };
        }

        /**
         * Handle incoming message
         */
        handleMessage(message) {
            const handler = this.handlers[message.type];
            if (handler) {
                handler(message);
            } else {
                console.log('Unknown command:', message);
            }
        }

        /**
         * Handle zoom command
         */
        handleZoomCommand(message) {
            if (this.map.zoomLayers) {
                if (message.direction === 'in') {
                    this.map.zoomLayers.zoomIn();
                } else if (message.direction === 'out') {
                    this.map.zoomLayers.zoomOut();
                }
            }
        }

        /**
         * Handle tour command
         */
        handleTourCommand(message) {
            if (window.jupiterAI) {
                if (message.action === 'start') {
                    window.jupiterAI.startNarratedTour();
                } else if (message.action === 'stop') {
                    window.jupiterAI.stopNarratedTour();
                }
            }
        }

        /**
         * Handle morph command
         */
        handleMorphCommand(message) {
            if (this.map.faceMorph) {
                if (message.mode === 'face') {
                    this.map.faceMorph.morphToFace();
                } else if (message.mode === 'globe') {
                    this.map.faceMorph.morphToGlobe();
                }
            }
        }

        /**
         * Handle highlight command
         */
        handleHighlightCommand(message) {
            const threat = this.map.threats.find(t => t.id === message.threatId);
            if (threat && window.jupiterAI) {
                window.jupiterAI.highlightThreat(threat);
            }
        }

        /**
         * Handle layer command
         */
        handleLayerCommand(message) {
            if (this.map.zoomLayers) {
                const layerIndex = this.map.zoomLayers.layers.findIndex(l => 
                    l.name.toLowerCase() === message.name.toLowerCase()
                );
                if (layerIndex >= 0) {
                    this.map.zoomLayers.jumpToLayer(layerIndex);
                }
            }
        }

        /**
         * Handle speak command
         */
        handleSpeakCommand(message) {
            if (window.jupiterAI) {
                window.jupiterAI.speak(message.text, message.options);
            }
        }

        /**
         * Send message to admin console
         */
        sendMessage(message) {
            if (this.connected && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify(message));
            } else {
                this.messageQueue.push(message);
            }
        }

        /**
         * Send status update
         */
        sendStatus(status) {
            this.sendMessage({
                type: 'status',
                timestamp: Date.now(),
                ...status
            });
        }
    }

    /**
     * INITIALIZE JUPITER INTEGRATION
     * Add all systems to existing 3D threat map
     */
    window.addEventListener('DOMContentLoaded', () => {
        // Wait for base threat map to initialize
        setTimeout(() => {
            const map = window.threatMap3D;
            if (!map) {
                console.error('3D Threat Map not found. Jupiter AI integration disabled.');
                return;
            }

            console.log('Initializing Jupiter AI Integration...');

            // Create zoom layer system
            map.zoomLayers = new ZoomLayerSystem(map);

            // Create face morph system
            map.faceMorph = new JupiterFaceMorph(map);

            // Create Jupiter AI controller
            window.jupiterAI = new JupiterAI(map);

            // Create admin console integration
            map.adminConsole = new AdminConsoleIntegration(map);

            // Expose for testing
            window.jupiterSystems = {
                zoomLayers: map.zoomLayers,
                faceMorph: map.faceMorph,
                ai: window.jupiterAI,
                adminConsole: map.adminConsole
            };

            console.log('✅ Jupiter AI Integration complete!');
            console.log('Try: window.jupiterAI.startNarratedTour()');
            console.log('Try: window.jupiterSystems.faceMorph.toggle()');
            console.log('Try: window.jupiterSystems.zoomLayers.zoomIn()');
            
        }, 2000); // Wait 2 seconds for base map
    });

})();
