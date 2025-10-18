/**
 * 3D Threat Map Enhancements
 * Additional features for the global threat visualization
 * 
 * New Features:
 * - Threat clustering (group nearby threats)
 * - Heat map overlay (threat density visualization)
 * - Keyboard navigation (arrow keys, +/- for zoom)
 * - Search functionality (find threats by location)
 * - Attack vector visualization (animated paths)
 * - Time-based filtering (last hour, day, week)
 * - Threat prediction paths
 * - Export functionality (screenshot, data)
 * 
 * @version 2.0.0
 * @author Enterprise Scanner
 */

// Extend the ThreatMap3D class with additional features
(function() {
    'use strict';

    // Wait for ThreatMap3D to be loaded
    if (typeof ThreatMap3D === 'undefined') {
        console.error('ThreatMap3D must be loaded before enhancements');
        return;
    }

    /**
     * Threat Clustering System
     */
    class ThreatCluster {
        constructor(threats, radius = 20) {
            this.threats = threats;
            this.radius = radius;
            this.clusters = [];
        }

        /**
         * Group nearby threats into clusters
         */
        generateClusters() {
            const clustered = new Set();
            this.clusters = [];

            this.threats.forEach((threat, index) => {
                if (clustered.has(index)) return;

                const cluster = {
                    center: threat.marker.position.clone(),
                    threats: [threat],
                    indices: [index]
                };

                // Find nearby threats
                this.threats.forEach((otherThreat, otherIndex) => {
                    if (otherIndex === index || clustered.has(otherIndex)) return;

                    const distance = threat.marker.position.distanceTo(otherThreat.marker.position);
                    
                    if (distance < this.radius) {
                        cluster.threats.push(otherThreat);
                        cluster.indices.push(otherIndex);
                        clustered.add(otherIndex);
                    }
                });

                clustered.add(index);
                this.clusters.push(cluster);
            });

            return this.clusters;
        }

        /**
         * Get cluster statistics
         */
        getStats() {
            return {
                totalClusters: this.clusters.length,
                averageSize: this.clusters.reduce((sum, c) => sum + c.threats.length, 0) / this.clusters.length,
                largestCluster: Math.max(...this.clusters.map(c => c.threats.length)),
                singleThreats: this.clusters.filter(c => c.threats.length === 1).length
            };
        }
    }

    /**
     * Heat Map Generator
     */
    class HeatMapGenerator {
        constructor(scene, globeRadius) {
            this.scene = scene;
            this.globeRadius = globeRadius;
            this.heatMapMesh = null;
        }

        /**
         * Generate heat map based on threat density
         */
        generate(clusters) {
            // Remove existing heat map
            if (this.heatMapMesh) {
                this.scene.remove(this.heatMapMesh);
            }

            const geometry = new THREE.SphereGeometry(this.globeRadius * 1.01, 64, 64);
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');

            // Create gradient background
            ctx.fillStyle = 'rgba(0, 0, 0, 0)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw heat spots for each cluster
            clusters.forEach(cluster => {
                const intensity = Math.min(cluster.threats.length / 10, 1);
                const gradient = ctx.createRadialGradient(
                    canvas.width / 2, canvas.height / 2, 0,
                    canvas.width / 2, canvas.height / 2, 100
                );

                gradient.addColorStop(0, `rgba(239, 68, 68, ${intensity * 0.8})`);
                gradient.addColorStop(0.5, `rgba(245, 158, 11, ${intensity * 0.5})`);
                gradient.addColorStop(1, 'rgba(251, 191, 36, 0)');

                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            });

            const texture = new THREE.CanvasTexture(canvas);
            const material = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                opacity: 0.5,
                blending: THREE.AdditiveBlending
            });

            this.heatMapMesh = new THREE.Mesh(geometry, material);
            this.scene.add(this.heatMapMesh);

            return this.heatMapMesh;
        }

        /**
         * Toggle heat map visibility
         */
        toggle(visible) {
            if (this.heatMapMesh) {
                this.heatMapMesh.visible = visible;
            }
        }
    }

    /**
     * Keyboard Navigation Controller
     */
    class KeyboardController {
        constructor(threatMap) {
            this.threatMap = threatMap;
            this.enabled = true;
            this.setupListeners();
        }

        setupListeners() {
            document.addEventListener('keydown', (e) => {
                if (!this.enabled) return;

                switch(e.key) {
                    case 'ArrowUp':
                        e.preventDefault();
                        this.threatMap.globe.rotation.x -= 0.1;
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        this.threatMap.globe.rotation.x += 0.1;
                        break;
                    case 'ArrowLeft':
                        e.preventDefault();
                        this.threatMap.globe.rotation.y -= 0.1;
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        this.threatMap.globe.rotation.y += 0.1;
                        break;
                    case '+':
                    case '=':
                        e.preventDefault();
                        this.threatMap.camera.position.z = Math.max(
                            this.threatMap.config.minZoom,
                            this.threatMap.camera.position.z - 10
                        );
                        break;
                    case '-':
                    case '_':
                        e.preventDefault();
                        this.threatMap.camera.position.z = Math.min(
                            this.threatMap.config.maxZoom,
                            this.threatMap.camera.position.z + 10
                        );
                        break;
                    case 'r':
                    case 'R':
                        e.preventDefault();
                        this.threatMap.resetView();
                        break;
                    case ' ':
                        e.preventDefault();
                        this.threatMap.isRotating = !this.threatMap.isRotating;
                        break;
                    case 'Escape':
                        this.threatMap.hideThreatDetails();
                        break;
                }
            });
        }

        enable() {
            this.enabled = true;
        }

        disable() {
            this.enabled = false;
        }
    }

    /**
     * Search Functionality
     */
    class ThreatSearch {
        constructor(threatMap) {
            this.threatMap = threatMap;
            this.createSearchUI();
        }

        createSearchUI() {
            const searchHTML = `
                <div class="threat-search-panel">
                    <div class="search-header">
                        <i class="bi bi-search"></i>
                        <input type="text" id="threat-search-input" placeholder="Search location or threat ID...">
                        <button id="search-clear-btn" class="btn-search-clear">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                    <div id="search-results" class="search-results"></div>
                </div>
            `;

            const container = this.threatMap.container;
            const searchDiv = document.createElement('div');
            searchDiv.innerHTML = searchHTML;
            container.appendChild(searchDiv.firstElementChild);

            this.setupSearchListeners();
        }

        setupSearchListeners() {
            const input = document.getElementById('threat-search-input');
            const clearBtn = document.getElementById('search-clear-btn');
            const resultsDiv = document.getElementById('search-results');

            input.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                if (query.length < 2) {
                    resultsDiv.innerHTML = '';
                    return;
                }

                const results = this.search(query);
                this.displayResults(results);
            });

            clearBtn.addEventListener('click', () => {
                input.value = '';
                resultsDiv.innerHTML = '';
            });
        }

        search(query) {
            return this.threatMap.threats.filter(threat => {
                const data = threat.data;
                return (
                    data.location.toLowerCase().includes(query) ||
                    data.name.toLowerCase().includes(query) ||
                    data.type.toLowerCase().includes(query) ||
                    `thr-${String(data.id).padStart(6, '0')}`.toLowerCase().includes(query)
                );
            });
        }

        displayResults(results) {
            const resultsDiv = document.getElementById('search-results');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<div class="search-no-results">No threats found</div>';
                return;
            }

            const html = results.slice(0, 5).map(threat => `
                <div class="search-result-item" data-threat-id="${threat.data.id}">
                    <div class="result-header">
                        <span class="severity-badge severity-${threat.data.type}">${threat.data.type}</span>
                        <span class="result-id">THR-${String(threat.data.id).padStart(6, '0')}</span>
                    </div>
                    <div class="result-name">${threat.data.name}</div>
                    <div class="result-location">
                        <i class="bi bi-geo-alt"></i> ${threat.data.location}
                    </div>
                </div>
            `).join('');

            resultsDiv.innerHTML = html;

            // Add click handlers
            resultsDiv.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    const threatId = parseInt(item.dataset.threatId);
                    const threat = results.find(t => t.data.id === threatId);
                    if (threat) {
                        this.focusOnThreat(threat);
                    }
                });
            });
        }

        focusOnThreat(threat) {
            // Show threat details
            this.threatMap.showThreatDetails(threat.data);
            this.threatMap.selectedThreat = threat.marker;

            // Animate camera to threat
            const targetPosition = threat.marker.position.clone().multiplyScalar(2);
            this.animateCamera(targetPosition);
        }

        animateCamera(targetPosition) {
            const startPosition = this.threatMap.camera.position.clone();
            const duration = 1000;
            const startTime = Date.now();

            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = this.easeInOutCubic(progress);

                this.threatMap.camera.position.lerpVectors(startPosition, targetPosition, eased);
                this.threatMap.camera.lookAt(0, 0, 0);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };

            animate();
        }

        easeInOutCubic(t) {
            return t < 0.5
                ? 4 * t * t * t
                : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }
    }

    /**
     * Attack Vector Visualizer
     */
    class AttackVectorVisualizer {
        constructor(scene, globeRadius) {
            this.scene = scene;
            this.globeRadius = globeRadius;
            this.attackPaths = [];
        }

        /**
         * Create animated attack vector between two points
         */
        createAttackVector(source, target, type = 'critical') {
            const curve = new THREE.CubicBezierCurve3(
                source,
                new THREE.Vector3(
                    (source.x + target.x) / 2,
                    (source.y + target.y) / 2 + this.globeRadius * 0.5,
                    (source.z + target.z) / 2
                ),
                new THREE.Vector3(
                    (source.x + target.x) / 2,
                    (source.y + target.y) / 2 + this.globeRadius * 0.3,
                    (source.z + target.z) / 2
                ),
                target
            );

            const points = curve.getPoints(100);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);

            const colorMap = {
                critical: 0xef4444,
                high: 0xf59e0b,
                medium: 0xfbbf24,
                low: 0x10b981
            };

            const material = new THREE.LineBasicMaterial({
                color: colorMap[type] || 0xef4444,
                transparent: true,
                opacity: 0,
                linewidth: 2
            });

            const line = new THREE.Line(geometry, material);
            this.scene.add(line);

            // Animated particles along path
            const particles = [];
            for (let i = 0; i < 5; i++) {
                const particleGeometry = new THREE.SphereGeometry(0.8, 8, 8);
                const particleMaterial = new THREE.MeshBasicMaterial({
                    color: colorMap[type],
                    transparent: true,
                    opacity: 0
                });
                const particle = new THREE.Mesh(particleGeometry, particleMaterial);
                this.scene.add(particle);
                particles.push({
                    mesh: particle,
                    progress: i / 5
                });
            }

            this.attackPaths.push({
                curve,
                line,
                particles,
                material,
                type,
                opacity: 0,
                active: true
            });

            this.animateAttackPath(this.attackPaths.length - 1);
        }

        /**
         * Animate attack path appearance and particles
         */
        animateAttackPath(index) {
            const path = this.attackPaths[index];
            const fadeInDuration = 1000;
            const startTime = Date.now();

            const animate = () => {
                if (!path.active) return;

                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / fadeInDuration, 1);

                // Fade in line
                path.opacity = progress * 0.6;
                path.material.opacity = path.opacity;

                // Animate particles
                path.particles.forEach(particle => {
                    particle.progress += 0.01;
                    if (particle.progress > 1) particle.progress = 0;

                    const point = path.curve.getPoint(particle.progress);
                    particle.mesh.position.copy(point);
                    particle.mesh.material.opacity = Math.sin(particle.progress * Math.PI) * 0.8;
                });

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    // Continue animating particles
                    this.animateParticles(index);
                }
            };

            animate();
        }

        animateParticles(index) {
            const path = this.attackPaths[index];

            const animate = () => {
                if (!path.active) return;

                path.particles.forEach(particle => {
                    particle.progress += 0.008;
                    if (particle.progress > 1) particle.progress = 0;

                    const point = path.curve.getPoint(particle.progress);
                    particle.mesh.position.copy(point);
                    particle.mesh.material.opacity = Math.sin(particle.progress * Math.PI) * 0.8;
                });

                requestAnimationFrame(animate);
            };

            animate();
        }

        /**
         * Clear all attack vectors
         */
        clearAll() {
            this.attackPaths.forEach(path => {
                path.active = false;
                this.scene.remove(path.line);
                path.particles.forEach(p => this.scene.remove(p.mesh));
            });
            this.attackPaths = [];
        }
    }

    /**
     * Time Filter System
     */
    class TimeFilter {
        constructor(threatMap) {
            this.threatMap = threatMap;
            this.currentFilter = 'all';
            this.createUI();
        }

        createUI() {
            const filterHTML = `
                <div class="time-filter-panel">
                    <h4>Time Range</h4>
                    <div class="time-filter-buttons">
                        <button class="btn-time-filter active" data-filter="all">All Time</button>
                        <button class="btn-time-filter" data-filter="week">Last Week</button>
                        <button class="btn-time-filter" data-filter="day">Last 24h</button>
                        <button class="btn-time-filter" data-filter="hour">Last Hour</button>
                    </div>
                </div>
            `;

            const controls = this.threatMap.container.querySelector('.threat-map-controls');
            if (controls) {
                const div = document.createElement('div');
                div.innerHTML = filterHTML;
                controls.appendChild(div.firstElementChild);

                this.setupListeners();
            }
        }

        setupListeners() {
            const buttons = document.querySelectorAll('.btn-time-filter');
            buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.applyFilter(btn.dataset.filter);
                });
            });
        }

        applyFilter(filter) {
            this.currentFilter = filter;
            const now = Date.now();
            const timeRanges = {
                hour: 3600000,
                day: 86400000,
                week: 604800000,
                all: Infinity
            };

            const cutoff = now - timeRanges[filter];

            this.threatMap.threats.forEach(threat => {
                const threatTime = new Date(threat.data.timestamp).getTime();
                const shouldShow = threatTime >= cutoff;
                threat.marker.visible = shouldShow && this.threatMap.filters[threat.data.type];
                threat.glow.visible = shouldShow && this.threatMap.filters[threat.data.type];
            });
        }
    }

    /**
     * Screenshot & Export Functionality
     */
    class ExportManager {
        constructor(threatMap) {
            this.threatMap = threatMap;
            this.createUI();
        }

        createUI() {
            const exportHTML = `
                <div class="export-panel">
                    <h4>Export</h4>
                    <button id="export-screenshot" class="btn-control">
                        <i class="bi bi-camera"></i> Screenshot
                    </button>
                    <button id="export-data" class="btn-control">
                        <i class="bi bi-download"></i> Export Data
                    </button>
                </div>
            `;

            const controls = this.threatMap.container.querySelector('.threat-map-controls');
            if (controls) {
                const div = document.createElement('div');
                div.innerHTML = exportHTML;
                controls.appendChild(div.firstElementChild);

                this.setupListeners();
            }
        }

        setupListeners() {
            document.getElementById('export-screenshot')?.addEventListener('click', () => {
                this.captureScreenshot();
            });

            document.getElementById('export-data')?.addEventListener('click', () => {
                this.exportData();
            });
        }

        captureScreenshot() {
            this.threatMap.renderer.render(this.threatMap.scene, this.threatMap.camera);
            const dataURL = this.threatMap.renderer.domElement.toDataURL('image/png');
            
            const link = document.createElement('a');
            link.download = `threat-map-${Date.now()}.png`;
            link.href = dataURL;
            link.click();

            if (typeof showToast !== 'undefined') {
                showToast.success('Screenshot saved!', 'Image downloaded to your device');
            }
        }

        exportData() {
            const data = this.threatMap.threats.map(t => t.data);
            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.download = `threat-data-${Date.now()}.json`;
            link.href = url;
            link.click();

            if (typeof showToast !== 'undefined') {
                showToast.success('Data exported!', `${data.length} threats exported`);
            }
        }
    }

    /**
     * Enhanced ThreatMap3D Initialization
     */
    window.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('threat-map-3d');
        if (!container || !window.threatMap3D) return;

        // Wait for base threat map to initialize
        setTimeout(() => {
            const map = window.threatMap3D;

            // Add clustering
            const clustering = new ThreatCluster(map.threats, 20);
            const clusters = clustering.generateClusters();
            console.log('Threat Clusters:', clustering.getStats());

            // Add heat map
            const heatMap = new HeatMapGenerator(map.scene, map.config.globeRadius);
            heatMap.generate(clusters);

            // Add keyboard navigation
            const keyboard = new KeyboardController(map);

            // Add search functionality
            const search = new ThreatSearch(map);

            // Add attack vectors (sample)
            const attackVectors = new AttackVectorVisualizer(map.scene, map.config.globeRadius);
            if (map.threats.length >= 2) {
                attackVectors.createAttackVector(
                    map.threats[0].marker.position,
                    map.threats[1].marker.position,
                    'critical'
                );
            }

            // Add time filter
            const timeFilter = new TimeFilter(map);

            // Add export functionality
            const exportManager = new ExportManager(map);

            // Store enhancements on map object
            map.enhancements = {
                clustering,
                heatMap,
                keyboard,
                search,
                attackVectors,
                timeFilter,
                exportManager
            };

            console.log('3D Threat Map Enhancements loaded successfully!');
        }, 1000);
    });

})();
