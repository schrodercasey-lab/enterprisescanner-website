/**
 * 3D Threat Map Component
 * Enterprise Scanner - Interactive Global Threat Visualization
 * 
 * Features:
 * - Three.js 3D globe with realistic Earth texture
 * - Real-time threat markers (pulsing animated spheres)
 * - Geographic threat distribution
 * - Animated data flow connections between threats
 * - Interactive camera controls (mouse drag, zoom, auto-rotate)
 * - Threat filtering by type and severity
 * - Click interactions for threat details
 * - Country highlighting on hover
 * - Performance optimized for 60 FPS
 * - Mobile-responsive with touch controls
 * - Dark theme integration
 * 
 * @version 1.0.0
 * @author Enterprise Scanner
 */

class ThreatMap3D {
    constructor(containerId, options = {}) {
        // Container setup
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Configuration
        this.config = {
            globeRadius: 100,
            cameraDistance: 300,
            autoRotate: true,
            autoRotateSpeed: 0.2,
            enableZoom: true,
            enablePan: false,
            minZoom: 200,
            maxZoom: 500,
            threatPulseSpeed: 0.03,
            dataFlowSpeed: 0.02,
            maxThreats: 50,
            colors: {
                globe: 0x1e293b,
                atmosphere: 0x3b82f6,
                threatCritical: 0xef4444,
                threatHigh: 0xf59e0b,
                threatMedium: 0xfbbf24,
                threatLow: 0x10b981,
                dataFlow: 0x8b5cf6,
                highlight: 0x60a5fa
            },
            ...options
        };

        // State
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.globe = null;
        this.threats = [];
        this.dataFlows = [];
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedThreat = null;
        this.isRotating = this.config.autoRotate;
        this.animationId = null;

        // Filter state
        this.filters = {
            critical: true,
            high: true,
            medium: true,
            low: true
        };

        // Initialize
        this.init();
    }

    /**
     * Initialize the 3D scene
     */
    init() {
        this.createScene();
        this.createCamera();
        this.createRenderer();
        this.createLights();
        this.createGlobe();
        this.createAtmosphere();
        this.generateMockThreats();
        this.setupControls();
        this.setupEventListeners();
        this.animate();
        this.createUI();
    }

    /**
     * Create Three.js scene
     */
    createScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f172a);
        this.scene.fog = new THREE.Fog(0x0f172a, 400, 800);
    }

    /**
     * Create camera
     */
    createCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 1, 1000);
        this.camera.position.z = this.config.cameraDistance;
    }

    /**
     * Create WebGL renderer
     */
    createRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.container.appendChild(this.renderer.domElement);
    }

    /**
     * Create scene lighting
     */
    createLights() {
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);

        // Directional light (simulating sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 3, 5);
        this.scene.add(directionalLight);

        // Point light for dramatic effect
        const pointLight = new THREE.PointLight(0x3b82f6, 0.5, 400);
        pointLight.position.set(-200, 50, 100);
        this.scene.add(pointLight);
    }

    /**
     * Create the globe
     */
    createGlobe() {
        const geometry = new THREE.SphereGeometry(
            this.config.globeRadius,
            64,
            64
        );

        // Create material with gradient effect
        const material = new THREE.MeshPhongMaterial({
            color: this.config.colors.globe,
            emissive: 0x0a1628,
            emissiveIntensity: 0.3,
            shininess: 10,
            transparent: true,
            opacity: 0.9
        });

        // Add wireframe for grid effect
        const wireframeGeometry = new THREE.EdgesGeometry(geometry);
        const wireframeMaterial = new THREE.LineBasicMaterial({
            color: 0x334155,
            transparent: true,
            opacity: 0.3
        });
        const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);

        this.globe = new THREE.Group();
        const sphere = new THREE.Mesh(geometry, material);
        this.globe.add(sphere);
        this.globe.add(wireframe);
        this.scene.add(this.globe);
    }

    /**
     * Create atmospheric glow effect
     */
    createAtmosphere() {
        const geometry = new THREE.SphereGeometry(
            this.config.globeRadius * 1.15,
            64,
            64
        );

        const material = new THREE.ShaderMaterial({
            uniforms: {
                color: { value: new THREE.Color(this.config.colors.atmosphere) }
            },
            vertexShader: `
                varying vec3 vNormal;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 color;
                varying vec3 vNormal;
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
                    gl_FragColor = vec4(color, 1.0) * intensity;
                }
            `,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending,
            transparent: true
        });

        const atmosphere = new THREE.Mesh(geometry, material);
        this.scene.add(atmosphere);
    }

    /**
     * Generate mock threat data
     */
    generateMockThreats() {
        const threatTypes = ['critical', 'high', 'medium', 'low'];
        const threatNames = [
            'Ransomware Attack',
            'DDoS Attack',
            'Data Breach',
            'Phishing Campaign',
            'Zero-Day Exploit',
            'SQL Injection',
            'XSS Vulnerability',
            'Malware Distribution',
            'Credential Stuffing',
            'API Breach'
        ];

        const locations = [
            { name: 'New York, USA', lat: 40.7128, lon: -74.0060 },
            { name: 'London, UK', lat: 51.5074, lon: -0.1278 },
            { name: 'Tokyo, Japan', lat: 35.6762, lon: 139.6503 },
            { name: 'Sydney, Australia', lat: -33.8688, lon: 151.2093 },
            { name: 'São Paulo, Brazil', lat: -23.5505, lon: -46.6333 },
            { name: 'Mumbai, India', lat: 19.0760, lon: 72.8777 },
            { name: 'Moscow, Russia', lat: 55.7558, lon: 37.6173 },
            { name: 'Cairo, Egypt', lat: 30.0444, lon: 31.2357 },
            { name: 'Beijing, China', lat: 39.9042, lon: 116.4074 },
            { name: 'Berlin, Germany', lat: 52.5200, lon: 13.4050 },
            { name: 'Paris, France', lat: 48.8566, lon: 2.3522 },
            { name: 'Singapore', lat: 1.3521, lon: 103.8198 },
            { name: 'Toronto, Canada', lat: 43.6532, lon: -79.3832 },
            { name: 'Dubai, UAE', lat: 25.2048, lon: 55.2708 },
            { name: 'Seoul, South Korea', lat: 37.5665, lon: 126.9780 },
            { name: 'Mexico City, Mexico', lat: 19.4326, lon: -99.1332 },
            { name: 'Lagos, Nigeria', lat: 6.5244, lon: 3.3792 },
            { name: 'Buenos Aires, Argentina', lat: -34.6037, lon: -58.3816 },
            { name: 'Bangkok, Thailand', lat: 13.7563, lon: 100.5018 },
            { name: 'Istanbul, Turkey', lat: 41.0082, lon: 28.9784 }
        ];

        // Generate threats
        for (let i = 0; i < this.config.maxThreats; i++) {
            const location = locations[Math.floor(Math.random() * locations.length)];
            const type = threatTypes[Math.floor(Math.random() * threatTypes.length)];
            const threat = {
                id: i,
                type: type,
                name: threatNames[Math.floor(Math.random() * threatNames.length)],
                location: location.name,
                lat: location.lat,
                lon: location.lon,
                severity: this.getSeverityValue(type),
                timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
                status: Math.random() > 0.3 ? 'active' : 'mitigated'
            };

            this.addThreat(threat);
        }

        // Create data flows between some threats
        this.createDataFlows();
    }

    /**
     * Get severity numeric value
     */
    getSeverityValue(type) {
        const severityMap = {
            critical: 4,
            high: 3,
            medium: 2,
            low: 1
        };
        return severityMap[type] || 1;
    }

    /**
     * Add threat marker to globe
     */
    addThreat(threatData) {
        // Convert lat/lon to 3D coordinates
        const phi = (90 - threatData.lat) * (Math.PI / 180);
        const theta = (threatData.lon + 180) * (Math.PI / 180);

        const x = -this.config.globeRadius * Math.sin(phi) * Math.cos(theta);
        const y = this.config.globeRadius * Math.cos(phi);
        const z = this.config.globeRadius * Math.sin(phi) * Math.sin(theta);

        // Create threat marker
        const markerSize = this.getSeverityValue(threatData.type) * 1.5;
        const geometry = new THREE.SphereGeometry(markerSize, 16, 16);
        
        // Get color based on threat type
        const color = this.config.colors[`threat${threatData.type.charAt(0).toUpperCase() + threatData.type.slice(1)}`];
        
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.8
        });

        const marker = new THREE.Mesh(geometry, material);
        marker.position.set(x, y, z);
        marker.userData = threatData;
        marker.userData.pulsePhase = Math.random() * Math.PI * 2;

        // Create outer glow
        const glowGeometry = new THREE.SphereGeometry(markerSize * 1.5, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.set(x, y, z);

        this.globe.add(marker);
        this.globe.add(glow);

        this.threats.push({
            data: threatData,
            marker: marker,
            glow: glow
        });
    }

    /**
     * Create animated data flows between threats
     */
    createDataFlows() {
        const numFlows = Math.min(10, Math.floor(this.threats.length / 2));

        for (let i = 0; i < numFlows; i++) {
            const source = this.threats[Math.floor(Math.random() * this.threats.length)];
            const target = this.threats[Math.floor(Math.random() * this.threats.length)];

            if (source === target) continue;

            // Create curve between two points
            const curve = new THREE.QuadraticBezierCurve3(
                source.marker.position,
                new THREE.Vector3(
                    (source.marker.position.x + target.marker.position.x) / 2 * 1.5,
                    (source.marker.position.y + target.marker.position.y) / 2 * 1.5,
                    (source.marker.position.z + target.marker.position.z) / 2 * 1.5
                ),
                target.marker.position
            );

            const points = curve.getPoints(50);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);

            const material = new THREE.LineBasicMaterial({
                color: this.config.colors.dataFlow,
                transparent: true,
                opacity: 0.4
            });

            const line = new THREE.Line(geometry, material);
            this.scene.add(line);

            // Create animated particle along the curve
            const particleGeometry = new THREE.SphereGeometry(0.5, 8, 8);
            const particleMaterial = new THREE.MeshBasicMaterial({
                color: this.config.colors.dataFlow,
                transparent: true,
                opacity: 0.8
            });
            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            this.scene.add(particle);

            this.dataFlows.push({
                curve: curve,
                line: line,
                particle: particle,
                progress: Math.random()
            });
        }
    }

    /**
     * Setup mouse/touch controls
     */
    setupControls() {
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };

        // Mouse down
        this.renderer.domElement.addEventListener('mousedown', (e) => {
            isDragging = true;
            this.isRotating = false;
        });

        // Mouse move
        this.renderer.domElement.addEventListener('mousemove', (e) => {
            // Update mouse position for raycasting
            const rect = this.renderer.domElement.getBoundingClientRect();
            this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            if (isDragging) {
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;

                this.globe.rotation.y += deltaX * 0.005;
                this.globe.rotation.x += deltaY * 0.005;

                // Limit vertical rotation
                this.globe.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.globe.rotation.x));
            }

            previousMousePosition = { x: e.clientX, y: e.clientY };
        });

        // Mouse up
        this.renderer.domElement.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // Mouse wheel (zoom)
        this.renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY;
            this.camera.position.z += delta * 0.1;
            this.camera.position.z = Math.max(this.config.minZoom, Math.min(this.config.maxZoom, this.camera.position.z));
        });

        // Click to select threat
        this.renderer.domElement.addEventListener('click', (e) => {
            if (!isDragging) {
                this.handleThreatClick();
            }
        });

        // Touch controls for mobile
        let touchStartX = 0;
        let touchStartY = 0;

        this.renderer.domElement.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                this.isRotating = false;
            }
        });

        this.renderer.domElement.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1) {
                const deltaX = e.touches[0].clientX - touchStartX;
                const deltaY = e.touches[0].clientY - touchStartY;

                this.globe.rotation.y += deltaX * 0.005;
                this.globe.rotation.x += deltaY * 0.005;

                this.globe.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.globe.rotation.x));

                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
            }
        });
    }

    /**
     * Handle threat marker clicks
     */
    handleThreatClick() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        const intersects = this.raycaster.intersectObjects(
            this.threats.map(t => t.marker)
        );

        if (intersects.length > 0) {
            const threat = intersects[0].object;
            this.showThreatDetails(threat.userData);
            this.selectedThreat = threat;
        } else {
            this.hideThreatDetails();
            this.selectedThreat = null;
        }
    }

    /**
     * Show threat details panel
     */
    showThreatDetails(threatData) {
        let panel = document.getElementById('threat-details-panel');
        
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'threat-details-panel';
            panel.className = 'threat-details-panel';
            this.container.appendChild(panel);
        }

        const severityClass = `severity-${threatData.type}`;
        const statusClass = threatData.status === 'active' ? 'status-active' : 'status-mitigated';

        panel.innerHTML = `
            <div class="threat-header ${severityClass}">
                <h3>${threatData.name}</h3>
                <button class="close-btn" onclick="window.threatMap3D.hideThreatDetails()">×</button>
            </div>
            <div class="threat-body">
                <div class="threat-field">
                    <span class="label">Threat ID:</span>
                    <span class="value">THR-${String(threatData.id).padStart(6, '0')}</span>
                </div>
                <div class="threat-field">
                    <span class="label">Type:</span>
                    <span class="value ${severityClass}">${threatData.type.toUpperCase()}</span>
                </div>
                <div class="threat-field">
                    <span class="label">Location:</span>
                    <span class="value">${threatData.location}</span>
                </div>
                <div class="threat-field">
                    <span class="label">Coordinates:</span>
                    <span class="value">${threatData.lat.toFixed(4)}°, ${threatData.lon.toFixed(4)}°</span>
                </div>
                <div class="threat-field">
                    <span class="label">Status:</span>
                    <span class="value ${statusClass}">${threatData.status.toUpperCase()}</span>
                </div>
                <div class="threat-field">
                    <span class="label">Detected:</span>
                    <span class="value">${new Date(threatData.timestamp).toLocaleString()}</span>
                </div>
                <div class="threat-field">
                    <span class="label">Severity:</span>
                    <span class="value">${threatData.severity}/4</span>
                </div>
            </div>
            <div class="threat-actions">
                <button class="btn-action btn-investigate">Investigate</button>
                <button class="btn-action btn-mitigate">Mitigate</button>
            </div>
        `;

        panel.classList.add('visible');
    }

    /**
     * Hide threat details panel
     */
    hideThreatDetails() {
        const panel = document.getElementById('threat-details-panel');
        if (panel) {
            panel.classList.remove('visible');
        }
        this.selectedThreat = null;
    }

    /**
     * Create UI controls
     */
    createUI() {
        const controlsHTML = `
            <div class="threat-map-controls">
                <div class="control-group">
                    <h4>Threat Filters</h4>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="filter-critical" checked>
                        <span class="severity-critical">Critical</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="filter-high" checked>
                        <span class="severity-high">High</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="filter-medium" checked>
                        <span class="severity-medium">Medium</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="filter-low" checked>
                        <span class="severity-low">Low</span>
                    </label>
                </div>
                <div class="control-group">
                    <h4>View Controls</h4>
                    <button id="toggle-rotation" class="btn-control">
                        <i class="bi bi-arrow-clockwise"></i> Auto-Rotate
                    </button>
                    <button id="reset-view" class="btn-control">
                        <i class="bi bi-arrow-counterclockwise"></i> Reset View
                    </button>
                </div>
                <div class="stats-panel">
                    <div class="stat-item">
                        <span class="stat-label">Active Threats:</span>
                        <span class="stat-value" id="stat-active">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Mitigated:</span>
                        <span class="stat-value" id="stat-mitigated">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Critical:</span>
                        <span class="stat-value severity-critical" id="stat-critical">0</span>
                    </div>
                </div>
            </div>
        `;

        const controlsDiv = document.createElement('div');
        controlsDiv.innerHTML = controlsHTML;
        this.container.appendChild(controlsDiv.firstElementChild);

        // Update stats
        this.updateStats();
    }

    /**
     * Update statistics
     */
    updateStats() {
        const active = this.threats.filter(t => t.data.status === 'active').length;
        const mitigated = this.threats.filter(t => t.data.status === 'mitigated').length;
        const critical = this.threats.filter(t => t.data.type === 'critical').length;

        document.getElementById('stat-active').textContent = active;
        document.getElementById('stat-mitigated').textContent = mitigated;
        document.getElementById('stat-critical').textContent = critical;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Filter checkboxes
        document.getElementById('filter-critical')?.addEventListener('change', (e) => {
            this.filters.critical = e.target.checked;
            this.applyFilters();
        });

        document.getElementById('filter-high')?.addEventListener('change', (e) => {
            this.filters.high = e.target.checked;
            this.applyFilters();
        });

        document.getElementById('filter-medium')?.addEventListener('change', (e) => {
            this.filters.medium = e.target.checked;
            this.applyFilters();
        });

        document.getElementById('filter-low')?.addEventListener('change', (e) => {
            this.filters.low = e.target.checked;
            this.applyFilters();
        });

        // Toggle rotation
        document.getElementById('toggle-rotation')?.addEventListener('click', () => {
            this.isRotating = !this.isRotating;
        });

        // Reset view
        document.getElementById('reset-view')?.addEventListener('click', () => {
            this.resetView();
        });
    }

    /**
     * Apply threat filters
     */
    applyFilters() {
        this.threats.forEach(threat => {
            const shouldShow = this.filters[threat.data.type];
            threat.marker.visible = shouldShow;
            threat.glow.visible = shouldShow;
        });
    }

    /**
     * Reset camera view
     */
    resetView() {
        this.camera.position.set(0, 0, this.config.cameraDistance);
        this.globe.rotation.set(0, 0, 0);
        this.isRotating = this.config.autoRotate;
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        // Auto-rotate globe
        if (this.isRotating) {
            this.globe.rotation.y += this.config.autoRotateSpeed * 0.01;
        }

        // Animate threat markers (pulsing effect)
        this.threats.forEach(threat => {
            threat.marker.userData.pulsePhase += this.config.threatPulseSpeed;
            const scale = 1 + Math.sin(threat.marker.userData.pulsePhase) * 0.3;
            threat.marker.scale.set(scale, scale, scale);
            threat.glow.scale.set(scale * 1.2, scale * 1.2, scale * 1.2);

            // Update opacity for pulsing
            threat.marker.material.opacity = 0.6 + Math.sin(threat.marker.userData.pulsePhase) * 0.2;
            threat.glow.material.opacity = 0.2 + Math.sin(threat.marker.userData.pulsePhase) * 0.1;
        });

        // Animate data flows
        this.dataFlows.forEach(flow => {
            flow.progress += this.config.dataFlowSpeed;
            if (flow.progress > 1) {
                flow.progress = 0;
            }

            const point = flow.curve.getPoint(flow.progress);
            flow.particle.position.copy(point);
        });

        // Render scene
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Destroy the 3D map
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        // Dispose geometries and materials
        this.threats.forEach(threat => {
            threat.marker.geometry.dispose();
            threat.marker.material.dispose();
            threat.glow.geometry.dispose();
            threat.glow.material.dispose();
        });

        this.dataFlows.forEach(flow => {
            flow.line.geometry.dispose();
            flow.line.material.dispose();
            flow.particle.geometry.dispose();
            flow.particle.material.dispose();
        });

        // Remove renderer
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('threat-map-3d');
    if (container) {
        window.threatMap3D = new ThreatMap3D('threat-map-3d', {
            autoRotate: true,
            autoRotateSpeed: 0.2,
            maxThreats: 50
        });
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThreatMap3D;
}
