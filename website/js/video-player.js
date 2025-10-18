/**
 * Video Player Component - Phase 2
 * Enterprise Scanner Website
 * Features: Custom controls, autoplay on scroll, playlist, fullscreen, analytics
 */

class VideoPlayer {
    constructor(options = {}) {
        this.options = {
            containerId: options.containerId || 'video-player',
            videoUrl: options.videoUrl || '',
            posterUrl: options.posterUrl || '',
            autoplay: options.autoplay || false,
            autoplayOnScroll: options.autoplayOnScroll !== false,
            scrollThreshold: options.scrollThreshold || 0.5,
            muted: options.muted !== false,
            loop: options.loop || false,
            controls: options.controls !== false,
            playlist: options.playlist || [],
            currentIndex: 0,
            analytics: options.analytics !== false,
            ...options
        };

        this.video = null;
        this.container = null;
        this.isPlaying = false;
        this.isPaused = true;
        this.isMuted = this.options.muted;
        this.isFullscreen = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 0.8;
        this.playbackRate = 1;
        this.hasStartedPlaying = false;
        this.watchTime = 0;
        this.lastUpdateTime = 0;

        this.init();
    }

    init() {
        this.injectStyles();
        this.container = document.getElementById(this.options.containerId);
        
        if (this.container) {
            this.render();
            this.setupEventListeners();
            this.setupScrollAutoplay();
        }
    }

    injectStyles() {
        if (document.getElementById('video-player-styles')) return;

        const style = document.createElement('style');
        style.id = 'video-player-styles';
        style.textContent = `
            .video-player-wrapper {
                position: relative;
                width: 100%;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            }

            .video-player-container {
                position: relative;
                width: 100%;
                padding-bottom: 56.25%; /* 16:9 aspect ratio */
                background: #000000;
            }

            .video-player-element {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .video-player-poster {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                cursor: pointer;
                transition: opacity 0.3s ease;
            }

            .video-player-poster.hidden {
                opacity: 0;
                pointer-events: none;
            }

            .video-player-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    to bottom,
                    rgba(0, 0, 0, 0.3) 0%,
                    transparent 30%,
                    transparent 70%,
                    rgba(0, 0, 0, 0.6) 100%
                );
                pointer-events: none;
                z-index: 1;
            }

            .video-player-play-button {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border: 4px solid rgba(255, 255, 255, 0.9);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 2;
                box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
            }

            .video-player-play-button:hover {
                transform: translate(-50%, -50%) scale(1.1);
                box-shadow: 0 15px 40px rgba(59, 130, 246, 0.6);
            }

            .video-player-play-button.playing {
                opacity: 0;
                pointer-events: none;
            }

            .video-player-play-button i {
                font-size: 2rem;
                color: #ffffff;
                margin-left: 4px;
            }

            .video-player-controls {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(
                    to top,
                    rgba(0, 0, 0, 0.9) 0%,
                    rgba(0, 0, 0, 0.7) 50%,
                    transparent 100%
                );
                padding: 20px 16px 12px;
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
                z-index: 3;
            }

            .video-player-wrapper:hover .video-player-controls,
            .video-player-controls.visible {
                opacity: 1;
                transform: translateY(0);
            }

            .video-player-progress-container {
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                cursor: pointer;
                margin-bottom: 12px;
                position: relative;
            }

            .video-player-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                border-radius: 3px;
                width: 0%;
                transition: width 0.1s linear;
                position: relative;
            }

            .video-player-progress-handle {
                position: absolute;
                right: -8px;
                top: 50%;
                transform: translateY(-50%);
                width: 16px;
                height: 16px;
                background: #ffffff;
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .video-player-progress-container:hover .video-player-progress-handle {
                opacity: 1;
            }

            .video-player-buffered {
                position: absolute;
                height: 100%;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                width: 0%;
                top: 0;
                left: 0;
            }

            .video-player-buttons {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .video-player-button {
                background: transparent;
                border: none;
                color: #ffffff;
                cursor: pointer;
                padding: 8px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                font-size: 1.1rem;
            }

            .video-player-button:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            .video-player-time {
                color: #ffffff;
                font-size: 0.85rem;
                margin-left: 4px;
                font-variant-numeric: tabular-nums;
            }

            .video-player-spacer {
                flex: 1;
            }

            .video-player-volume-container {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .video-player-volume-slider {
                width: 0;
                height: 4px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
                cursor: pointer;
                position: relative;
                overflow: hidden;
                transition: width 0.3s ease;
            }

            .video-player-volume-container:hover .video-player-volume-slider {
                width: 80px;
            }

            .video-player-volume-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                border-radius: 2px;
                width: 80%;
            }

            .video-player-speed-menu {
                position: relative;
            }

            .video-player-speed-options {
                position: absolute;
                bottom: 100%;
                right: 0;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                margin-bottom: 8px;
                display: none;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }

            .video-player-speed-options.active {
                display: block;
            }

            .video-player-speed-option {
                padding: 8px 16px;
                color: #ffffff;
                cursor: pointer;
                border-radius: 4px;
                white-space: nowrap;
                font-size: 0.9rem;
                transition: background 0.2s ease;
            }

            .video-player-speed-option:hover,
            .video-player-speed-option.active {
                background: rgba(59, 130, 246, 0.3);
            }

            .video-player-loading {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 4;
                display: none;
            }

            .video-player-loading.active {
                display: block;
            }

            .video-player-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255, 255, 255, 0.2);
                border-top-color: #3b82f6;
                border-radius: 50%;
                animation: spin-video 1s linear infinite;
            }

            @keyframes spin-video {
                to { transform: rotate(360deg); }
            }

            .video-player-playlist {
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding: 16px;
            }

            .video-player-playlist-title {
                color: #ffffff;
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 12px;
            }

            .video-player-playlist-items {
                display: grid;
                gap: 12px;
            }

            .video-player-playlist-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .video-player-playlist-item:hover {
                background: rgba(59, 130, 246, 0.2);
                border-color: rgba(59, 130, 246, 0.4);
            }

            .video-player-playlist-item.active {
                background: rgba(59, 130, 246, 0.3);
                border-color: rgba(59, 130, 246, 0.5);
            }

            .video-player-playlist-thumbnail {
                width: 80px;
                height: 45px;
                border-radius: 4px;
                object-fit: cover;
                background: rgba(0, 0, 0, 0.3);
            }

            .video-player-playlist-info {
                flex: 1;
            }

            .video-player-playlist-item-title {
                color: #ffffff;
                font-size: 0.9rem;
                font-weight: 500;
                margin-bottom: 4px;
            }

            .video-player-playlist-item-duration {
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.8rem;
            }

            .video-player-playlist-item-playing {
                color: #3b82f6;
                font-size: 1.2rem;
            }

            /* Fullscreen mode */
            .video-player-wrapper.fullscreen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 9999;
                border-radius: 0;
            }

            .video-player-wrapper.fullscreen .video-player-container {
                padding-bottom: 0;
                height: 100vh;
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .video-player-play-button {
                    width: 60px;
                    height: 60px;
                }

                .video-player-play-button i {
                    font-size: 1.5rem;
                }

                .video-player-volume-container:hover .video-player-volume-slider {
                    width: 60px;
                }

                .video-player-button {
                    font-size: 1rem;
                    padding: 6px;
                }

                .video-player-time {
                    font-size: 0.75rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    render() {
        const currentVideo = this.getCurrentVideo();
        
        const html = `
            <div class="video-player-wrapper">
                <div class="video-player-container">
                    <video 
                        class="video-player-element" 
                        ${this.options.muted ? 'muted' : ''}
                        ${this.options.loop ? 'loop' : ''}
                        playsinline
                        preload="metadata">
                        ${currentVideo.url ? `<source src="${currentVideo.url}" type="video/mp4">` : ''}
                    </video>
                    
                    ${currentVideo.poster ? `
                        <img class="video-player-poster" src="${currentVideo.poster}" alt="Video thumbnail">
                    ` : ''}
                    
                    <div class="video-player-overlay"></div>
                    
                    <div class="video-player-play-button">
                        <i class="bi bi-play-fill"></i>
                    </div>
                    
                    <div class="video-player-loading">
                        <div class="video-player-spinner"></div>
                    </div>
                    
                    ${this.renderControls()}
                </div>
                
                ${this.options.playlist.length > 0 ? this.renderPlaylist() : ''}
            </div>
        `;
        
        this.container.innerHTML = html;
        this.video = this.container.querySelector('.video-player-element');
        this.cacheElements();
    }

    renderControls() {
        return `
            <div class="video-player-controls">
                <div class="video-player-progress-container">
                    <div class="video-player-buffered"></div>
                    <div class="video-player-progress-bar">
                        <div class="video-player-progress-handle"></div>
                    </div>
                </div>
                <div class="video-player-buttons">
                    <button class="video-player-button play-pause" title="Play/Pause">
                        <i class="bi bi-play-fill"></i>
                    </button>
                    <button class="video-player-button skip-back" title="Rewind 10s">
                        <i class="bi bi-skip-backward-fill"></i>
                    </button>
                    <button class="video-player-button skip-forward" title="Forward 10s">
                        <i class="bi bi-skip-forward-fill"></i>
                    </button>
                    <span class="video-player-time">
                        <span class="current-time">0:00</span> / <span class="total-time">0:00</span>
                    </span>
                    <div class="video-player-spacer"></div>
                    <div class="video-player-volume-container">
                        <button class="video-player-button volume-button" title="Mute/Unmute">
                            <i class="bi ${this.isMuted ? 'bi-volume-mute-fill' : 'bi-volume-up-fill'}"></i>
                        </button>
                        <div class="video-player-volume-slider">
                            <div class="video-player-volume-bar"></div>
                        </div>
                    </div>
                    <div class="video-player-speed-menu">
                        <button class="video-player-button speed-button" title="Playback Speed">
                            <i class="bi bi-speedometer2"></i>
                        </button>
                        <div class="video-player-speed-options">
                            <div class="video-player-speed-option" data-speed="0.5">0.5x</div>
                            <div class="video-player-speed-option" data-speed="0.75">0.75x</div>
                            <div class="video-player-speed-option active" data-speed="1">1x</div>
                            <div class="video-player-speed-option" data-speed="1.25">1.25x</div>
                            <div class="video-player-speed-option" data-speed="1.5">1.5x</div>
                            <div class="video-player-speed-option" data-speed="2">2x</div>
                        </div>
                    </div>
                    <button class="video-player-button fullscreen-button" title="Fullscreen">
                        <i class="bi bi-arrows-fullscreen"></i>
                    </button>
                </div>
            </div>
        `;
    }

    renderPlaylist() {
        const items = this.options.playlist.map((video, index) => `
            <div class="video-player-playlist-item ${index === this.options.currentIndex ? 'active' : ''}" data-index="${index}">
                ${video.thumbnail ? `<img class="video-player-playlist-thumbnail" src="${video.thumbnail}" alt="${video.title}">` : ''}
                <div class="video-player-playlist-info">
                    <div class="video-player-playlist-item-title">${video.title}</div>
                    <div class="video-player-playlist-item-duration">${video.duration || ''}</div>
                </div>
                ${index === this.options.currentIndex ? '<i class="video-player-playlist-item-playing bi bi-play-circle-fill"></i>' : ''}
            </div>
        `).join('');

        return `
            <div class="video-player-playlist">
                <div class="video-player-playlist-title">
                    <i class="bi bi-collection-play me-2"></i>Product Demos
                </div>
                <div class="video-player-playlist-items">
                    ${items}
                </div>
            </div>
        `;
    }

    cacheElements() {
        this.elements = {
            poster: this.container.querySelector('.video-player-poster'),
            playButton: this.container.querySelector('.video-player-play-button'),
            controls: this.container.querySelector('.video-player-controls'),
            playPauseBtn: this.container.querySelector('.play-pause'),
            skipBackBtn: this.container.querySelector('.skip-back'),
            skipForwardBtn: this.container.querySelector('.skip-forward'),
            volumeBtn: this.container.querySelector('.volume-button'),
            volumeSlider: this.container.querySelector('.video-player-volume-slider'),
            volumeBar: this.container.querySelector('.video-player-volume-bar'),
            speedBtn: this.container.querySelector('.speed-button'),
            speedOptions: this.container.querySelector('.video-player-speed-options'),
            fullscreenBtn: this.container.querySelector('.fullscreen-button'),
            progressContainer: this.container.querySelector('.video-player-progress-container'),
            progressBar: this.container.querySelector('.video-player-progress-bar'),
            bufferedBar: this.container.querySelector('.video-player-buffered'),
            currentTimeEl: this.container.querySelector('.current-time'),
            totalTimeEl: this.container.querySelector('.total-time'),
            loading: this.container.querySelector('.video-player-loading')
        };
    }

    getCurrentVideo() {
        if (this.options.playlist.length > 0) {
            return this.options.playlist[this.options.currentIndex];
        }
        return {
            url: this.options.videoUrl,
            poster: this.options.posterUrl
        };
    }

    setupEventListeners() {
        if (!this.video) return;

        // Video events
        this.video.addEventListener('loadedmetadata', () => this.handleLoadedMetadata());
        this.video.addEventListener('timeupdate', () => this.handleTimeUpdate());
        this.video.addEventListener('progress', () => this.handleProgress());
        this.video.addEventListener('play', () => this.handlePlay());
        this.video.addEventListener('pause', () => this.handlePause());
        this.video.addEventListener('ended', () => this.handleEnded());
        this.video.addEventListener('waiting', () => this.showLoading());
        this.video.addEventListener('canplay', () => this.hideLoading());

        // Play button
        if (this.elements.playButton) {
            this.elements.playButton.addEventListener('click', () => this.togglePlay());
        }

        if (this.elements.poster) {
            this.elements.poster.addEventListener('click', () => this.togglePlay());
        }

        // Control buttons
        if (this.elements.playPauseBtn) {
            this.elements.playPauseBtn.addEventListener('click', () => this.togglePlay());
        }

        if (this.elements.skipBackBtn) {
            this.elements.skipBackBtn.addEventListener('click', () => this.skip(-10));
        }

        if (this.elements.skipForwardBtn) {
            this.elements.skipForwardBtn.addEventListener('click', () => this.skip(10));
        }

        if (this.elements.volumeBtn) {
            this.elements.volumeBtn.addEventListener('click', () => this.toggleMute());
        }

        if (this.elements.volumeSlider) {
            this.elements.volumeSlider.addEventListener('click', (e) => this.handleVolumeChange(e));
        }

        if (this.elements.speedBtn) {
            this.elements.speedBtn.addEventListener('click', () => this.toggleSpeedMenu());
        }

        // Speed options
        this.container.querySelectorAll('.video-player-speed-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const speed = parseFloat(e.target.dataset.speed);
                this.setPlaybackRate(speed);
            });
        });

        if (this.elements.fullscreenBtn) {
            this.elements.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        // Progress bar
        if (this.elements.progressContainer) {
            this.elements.progressContainer.addEventListener('click', (e) => this.handleProgressClick(e));
        }

        // Playlist items
        this.container.querySelectorAll('.video-player-playlist-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                this.playVideo(index);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    setupScrollAutoplay() {
        if (!this.options.autoplayOnScroll) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio >= this.options.scrollThreshold) {
                    if (!this.hasStartedPlaying && this.options.autoplay) {
                        this.play();
                    }
                }
            });
        }, {
            threshold: [0, 0.25, 0.5, 0.75, 1]
        });

        observer.observe(this.container);
    }

    togglePlay() {
        if (this.isPaused) {
            this.play();
        } else {
            this.pause();
        }
    }

    play() {
        if (!this.video) return;

        this.video.play().then(() => {
            this.isPlaying = true;
            this.isPaused = false;
            this.hasStartedPlaying = true;
            
            if (this.elements.poster) {
                this.elements.poster.classList.add('hidden');
            }

            this.trackAnalytics('play');
        }).catch(error => {
            console.error('Error playing video:', error);
        });
    }

    pause() {
        if (!this.video) return;

        this.video.pause();
        this.isPlaying = false;
        this.isPaused = true;

        this.trackAnalytics('pause');
    }

    skip(seconds) {
        if (!this.video) return;
        this.video.currentTime = Math.max(0, Math.min(this.duration, this.video.currentTime + seconds));
    }

    toggleMute() {
        if (!this.video) return;

        this.isMuted = !this.isMuted;
        this.video.muted = this.isMuted;

        if (this.elements.volumeBtn) {
            const icon = this.elements.volumeBtn.querySelector('i');
            icon.className = this.isMuted ? 'bi bi-volume-mute-fill' : 'bi bi-volume-up-fill';
        }
    }

    handleVolumeChange(e) {
        if (!this.video) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const width = rect.width;
        const volume = Math.max(0, Math.min(1, x / width));

        this.video.volume = volume;
        this.volume = volume;
        
        if (this.elements.volumeBar) {
            this.elements.volumeBar.style.width = `${volume * 100}%`;
        }

        if (volume > 0 && this.isMuted) {
            this.toggleMute();
        }
    }

    toggleSpeedMenu() {
        if (this.elements.speedOptions) {
            this.elements.speedOptions.classList.toggle('active');
        }
    }

    setPlaybackRate(rate) {
        if (!this.video) return;

        this.video.playbackRate = rate;
        this.playbackRate = rate;

        // Update active state
        this.container.querySelectorAll('.video-player-speed-option').forEach(option => {
            option.classList.remove('active');
            if (parseFloat(option.dataset.speed) === rate) {
                option.classList.add('active');
            }
        });

        this.toggleSpeedMenu();
    }

    toggleFullscreen() {
        const wrapper = this.container.querySelector('.video-player-wrapper');
        
        if (!this.isFullscreen) {
            if (wrapper.requestFullscreen) {
                wrapper.requestFullscreen();
            } else if (wrapper.webkitRequestFullscreen) {
                wrapper.webkitRequestFullscreen();
            } else if (wrapper.msRequestFullscreen) {
                wrapper.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }

        this.isFullscreen = !this.isFullscreen;
    }

    handleProgressClick(e) {
        if (!this.video) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const width = rect.width;
        const percentage = x / width;
        const time = percentage * this.duration;

        this.video.currentTime = time;
    }

    handleLoadedMetadata() {
        this.duration = this.video.duration;
        if (this.elements.totalTimeEl) {
            this.elements.totalTimeEl.textContent = this.formatTime(this.duration);
        }
    }

    handleTimeUpdate() {
        this.currentTime = this.video.currentTime;

        // Update progress bar
        const percentage = (this.currentTime / this.duration) * 100;
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = `${percentage}%`;
        }

        // Update time display
        if (this.elements.currentTimeEl) {
            this.elements.currentTimeEl.textContent = this.formatTime(this.currentTime);
        }

        // Track watch time
        this.watchTime += this.currentTime - this.lastUpdateTime;
        this.lastUpdateTime = this.currentTime;
    }

    handleProgress() {
        if (!this.video || !this.video.buffered.length) return;

        const bufferedEnd = this.video.buffered.end(this.video.buffered.length - 1);
        const percentage = (bufferedEnd / this.duration) * 100;

        if (this.elements.bufferedBar) {
            this.elements.bufferedBar.style.width = `${percentage}%`;
        }
    }

    handlePlay() {
        if (this.elements.playPauseBtn) {
            const icon = this.elements.playPauseBtn.querySelector('i');
            icon.className = 'bi bi-pause-fill';
        }

        if (this.elements.playButton) {
            this.elements.playButton.classList.add('playing');
        }
    }

    handlePause() {
        if (this.elements.playPauseBtn) {
            const icon = this.elements.playPauseBtn.querySelector('i');
            icon.className = 'bi bi-play-fill';
        }

        if (this.elements.playButton) {
            this.elements.playButton.classList.remove('playing');
        }
    }

    handleEnded() {
        this.trackAnalytics('ended');

        // Auto-play next video in playlist
        if (this.options.playlist.length > 0 && this.options.currentIndex < this.options.playlist.length - 1) {
            this.playVideo(this.options.currentIndex + 1);
        }
    }

    playVideo(index) {
        if (index < 0 || index >= this.options.playlist.length) return;

        this.options.currentIndex = index;
        this.render();
        this.setupEventListeners();
        
        // Auto-play new video
        setTimeout(() => {
            this.play();
        }, 100);
    }

    showLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.add('active');
        }
    }

    hideLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.remove('active');
        }
    }

    handleKeyboard(e) {
        // Only if video container is in focus
        if (!this.container.contains(document.activeElement) && document.activeElement !== document.body) return;

        switch(e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.skip(-5);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.skip(5);
                break;
            case 'm':
                e.preventDefault();
                this.toggleMute();
                break;
            case 'f':
                e.preventDefault();
                this.toggleFullscreen();
                break;
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    trackAnalytics(event) {
        if (!this.options.analytics) return;

        const data = {
            event,
            currentTime: this.currentTime,
            duration: this.duration,
            watchTime: this.watchTime,
            playbackRate: this.playbackRate,
            videoIndex: this.options.currentIndex
        };

        // Send to analytics service (Google Analytics, Mixpanel, etc.)
        console.log('Video Analytics:', data);

        // Example: Google Analytics
        if (window.gtag) {
            window.gtag('event', event, {
                event_category: 'Video',
                event_label: this.getCurrentVideo().title || 'Video',
                value: Math.floor(this.currentTime)
            });
        }
    }

    destroy() {
        if (this.video) {
            this.video.pause();
        }
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('video-player');
    if (container) {
        // Initialize with sample playlist
        window.videoPlayer = new VideoPlayer({
            autoplay: false,
            autoplayOnScroll: true,
            muted: true,
            playlist: [
                {
                    title: 'Enterprise Scanner Overview',
                    url: 'assets/videos/overview.mp4',
                    poster: 'assets/videos/overview-poster.jpg',
                    thumbnail: 'assets/videos/overview-thumb.jpg',
                    duration: '2:30'
                },
                {
                    title: 'Dashboard Features Demo',
                    url: 'assets/videos/dashboard.mp4',
                    poster: 'assets/videos/dashboard-poster.jpg',
                    thumbnail: 'assets/videos/dashboard-thumb.jpg',
                    duration: '3:15'
                },
                {
                    title: 'Security Scanning in Action',
                    url: 'assets/videos/scanning.mp4',
                    poster: 'assets/videos/scanning-poster.jpg',
                    thumbnail: 'assets/videos/scanning-thumb.jpg',
                    duration: '2:45'
                }
            ]
        });
    }
});
