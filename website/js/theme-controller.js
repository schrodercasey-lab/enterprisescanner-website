/**
 * Dark AI Theme & AR Mode Controller
 * Manages theme switching and AR mode activation
 */

class ThemeController {
    constructor() {
        this.isDarkMode = true; // Default to dark mode for AI aesthetic
        this.init();
    }
    
    init() {
        // Apply dark theme by default
        this.applyTheme();
        
        // Create theme toggle button
        this.createThemeToggle();
        
        // Create AR activation button
        this.createARButton();
        
        // Create WiFi Eyes activation button
        this.createWiFiEyesButton();
        
        // Load saved preference
        this.loadThemePreference();
        
        console.log('🎨 Theme Controller initialized');
    }
    
    createThemeToggle() {
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'theme-toggle';
        toggleBtn.className = 'theme-toggle';
        toggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        toggleBtn.title = 'Toggle Dark/Light Mode';
        
        toggleBtn.addEventListener('click', () => this.toggleTheme());
        
        document.body.appendChild(toggleBtn);
    }
    
    createARButton() {
        const arBtn = document.createElement('button');
        arBtn.id = 'ar-mode-toggle';
        arBtn.className = 'ar-mode-toggle';
        arBtn.innerHTML = '<i class="bi bi-badge-ar"></i>';
        arBtn.title = 'Activate AR Mode';
        
        arBtn.addEventListener('click', () => this.activateAR());
        
        document.body.appendChild(arBtn);
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .ar-mode-toggle {
                position: fixed;
                bottom: 170px;
                right: 30px;
                width: 56px;
                height: 56px;
                background: linear-gradient(135deg, #06b6d4, #00ffff);
                border: none;
                border-radius: 50%;
                color: white;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 8px 24px rgba(6, 182, 212, 0.4);
                transition: all 0.3s ease;
                z-index: 9997;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .ar-mode-toggle:hover {
                transform: translateY(-4px) scale(1.1);
                box-shadow: 0 12px 32px rgba(6, 182, 212, 0.6);
            }
            
            .ar-mode-toggle i {
                transition: transform 0.3s ease;
            }
            
            .ar-mode-toggle:hover i {
                transform: scale(1.2);
            }
            
            @media (max-width: 768px) {
                .theme-toggle,
                .ar-mode-toggle {
                    width: 48px;
                    height: 48px;
                    font-size: 20px;
                    right: 20px;
                }
                
                .theme-toggle {
                    bottom: 90px;
                }
                
                .ar-mode-toggle {
                    bottom: 150px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    createWiFiEyesButton() {
        const wifiBtn = document.createElement('button');
        wifiBtn.id = 'wifi-eyes-toggle';
        wifiBtn.className = 'wifi-eyes-fab';
        wifiBtn.innerHTML = '<i class="bi bi-camera-video"></i>';
        wifiBtn.title = 'Activate WiFi Eyes (Camera Vision)';
        
        wifiBtn.addEventListener('click', () => this.activateWiFiEyes());
        
        document.body.appendChild(wifiBtn);
    }
    
    activateWiFiEyes() {
        if (window.jupiterWiFiEyes) {
            window.jupiterWiFiEyes.toggle();
            this.showNotification('WiFi Eyes Toggled', 'bi-camera-video');
        } else {
            console.log('⚠️ WiFi Eyes not loaded yet');
            this.showNotification('WiFi Eyes Loading...', 'bi-exclamation-triangle');
            
            // Try again in 1 second
            setTimeout(() => {
                if (window.jupiterWiFiEyes) {
                    window.jupiterWiFiEyes.toggle();
                } else {
                    this.showNotification('WiFi Eyes Not Available', 'bi-x-circle');
                }
            }, 1000);
        }
    }
    
    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme();
        this.saveThemePreference();
        
        // Update button icon
        const toggleBtn = document.getElementById('theme-toggle');
        if (this.isDarkMode) {
            toggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        } else {
            toggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
        
        // Show notification
        this.showNotification(
            this.isDarkMode ? 'Dark AI Mode Activated' : 'Light Mode Activated',
            this.isDarkMode ? 'bi-moon-stars' : 'bi-sun'
        );
    }
    
    applyTheme() {
        if (this.isDarkMode) {
            document.body.classList.add('dark-ai-theme');
        } else {
            document.body.classList.remove('dark-ai-theme');
        }
    }
    
    saveThemePreference() {
        localStorage.setItem('enterpriseScanner_theme', this.isDarkMode ? 'dark' : 'light');
    }
    
    loadThemePreference() {
        const saved = localStorage.getItem('enterpriseScanner_theme');
        if (saved) {
            this.isDarkMode = saved === 'dark';
            this.applyTheme();
            
            // Update button
            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn) {
                toggleBtn.innerHTML = this.isDarkMode 
                    ? '<i class="bi bi-moon-stars-fill"></i>' 
                    : '<i class="bi bi-sun-fill"></i>';
            }
        }
    }
    
    activateAR() {
        if (window.jupiterAREnhancements) {
            window.jupiterAREnhancements.activateAR();
            this.showNotification('AR Mode Activating...', 'bi-badge-ar');
        } else {
            console.log('⚠️ AR Enhancements not loaded yet');
            this.showNotification('AR System Loading...', 'bi-exclamation-triangle');
            
            // Try again in 1 second
            setTimeout(() => {
                if (window.jupiterAREnhancements) {
                    window.jupiterAREnhancements.activateAR();
                } else {
                    this.showNotification('AR Not Available', 'bi-x-circle');
                }
            }, 1000);
        }
    }
    
    showNotification(message, icon = 'bi-check-circle') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <i class="bi ${icon}"></i>
            <span>${message}</span>
        `;
        
        // Add styles if not exists
        if (!document.getElementById('theme-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'theme-notification-styles';
            style.textContent = `
                .theme-notification {
                    position: fixed;
                    top: 100px !important;
                    right: 30px;
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.95), rgba(118, 75, 162, 0.95));
                    color: white;
                    padding: 16px 24px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
                    backdrop-filter: blur(10px);
                    z-index: 100000 !important;
                    animation: notificationSlideIn 0.3s ease-out;
                }
                
                .theme-notification i {
                    font-size: 20px;
                }
                
                @keyframes notificationSlideIn {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes notificationSlideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }
                
                @media (max-width: 768px) {
                    .theme-notification {
                        top: 20px;
                        right: 20px;
                        left: 20px;
                        max-width: calc(100% - 40px);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'notificationSlideOut 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize theme controller when page loads
let themeController;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        themeController = new ThemeController();
        window.themeController = themeController;
    });
} else {
    themeController = new ThemeController();
    window.themeController = themeController;
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + D = Toggle Dark Mode
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (window.themeController) {
            window.themeController.toggleTheme();
        }
    }
    
    // Ctrl/Cmd + Shift + A = Activate AR
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        if (window.themeController) {
            window.themeController.activateAR();
        }
    }
    
    // Ctrl/Cmd + Shift + W = Activate WiFi Eyes
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'W') {
        e.preventDefault();
        if (window.themeController) {
            window.themeController.activateWiFiEyes();
        }
    }
});
