/**
 * Status Dashboard Widget
 * ========================
 * 
 * Real-time system health and feature status monitoring
 * Features: Circuit breaker status, error rates, latency, feature health
 * 
 * Usage:
 *   const dashboard = new StatusDashboard('#status-container');
 *   dashboard.updateStatus(statusData);
 */

class StatusDashboard {
    constructor(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.statusData = null;
        this.updateInterval = null;
        
        if (this.container) {
            this.init();
        }
    }

    init() {
        this.render();
        this.startAutoRefresh(30000); // Refresh every 30 seconds
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="status-dashboard bg-slate-800/90 rounded-lg shadow-lg p-4 border border-slate-700">
                <!-- Header -->
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-slate-200 flex items-center">
                        <i class="fas fa-heartbeat text-green-500 mr-2"></i>
                        System Health
                    </h3>
                    <button onclick="statusDashboard.refresh()" class="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>

                <!-- Overall Status -->
                <div class="overall-status mb-4 p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-slate-300">Overall Status</span>
                        <div class="flex items-center space-x-2">
                            <span class="status-badge px-3 py-1 rounded-full text-xs font-semibold">
                                <i class="fas fa-circle mr-1"></i>Loading...
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Metrics Grid -->
                <div class="metrics-grid grid grid-cols-2 gap-3 mb-4">
                    <!-- Error Rate -->
                    <div class="metric-item p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-xs text-slate-400">Error Rate</span>
                            <i class="fas fa-exclamation-triangle text-yellow-500 text-sm"></i>
                        </div>
                        <div class="error-rate-value text-xl font-bold text-slate-200">0%</div>
                        <div class="text-xs text-slate-500 mt-1">Last hour</div>
                    </div>

                    <!-- Latency -->
                    <div class="metric-item p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-xs text-slate-400">Latency</span>
                            <i class="fas fa-tachometer-alt text-blue-500 text-sm"></i>
                        </div>
                        <div class="latency-value text-xl font-bold text-slate-200">--ms</div>
                        <div class="text-xs text-slate-500 mt-1">Average</div>
                    </div>

                    <!-- Total Errors -->
                    <div class="metric-item p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-xs text-slate-400">Total Errors</span>
                            <i class="fas fa-bug text-red-500 text-sm"></i>
                        </div>
                        <div class="total-errors-value text-xl font-bold text-slate-200">0</div>
                        <div class="text-xs text-slate-500 mt-1">Last hour</div>
                    </div>

                    <!-- Uptime -->
                    <div class="metric-item p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-xs text-slate-400">Uptime</span>
                            <i class="fas fa-clock text-green-500 text-sm"></i>
                        </div>
                        <div class="uptime-value text-xl font-bold text-slate-200">99.9%</div>
                        <div class="text-xs text-slate-500 mt-1">Last 24h</div>
                    </div>
                </div>

                <!-- Feature Status -->
                <div class="feature-status">
                    <h4 class="text-sm font-semibold text-slate-300 mb-2 flex items-center">
                        <i class="fas fa-cog mr-2"></i>
                        Feature Status
                    </h4>
                    <div class="feature-list space-y-2">
                        <div class="text-center text-slate-500 text-sm py-2">
                            Loading features...
                        </div>
                    </div>
                </div>

                <!-- Error Types (Expandable) -->
                <div class="error-types mt-4">
                    <button class="error-types-toggle w-full text-left text-sm font-semibold text-slate-300 flex items-center justify-between p-2 hover:bg-slate-900/30 rounded transition-colors">
                        <span>
                            <i class="fas fa-list mr-2"></i>
                            Error Breakdown
                        </span>
                        <i class="fas fa-chevron-down text-xs transition-transform"></i>
                    </button>
                    <div class="error-types-content hidden mt-2 space-y-1">
                        <div class="text-center text-slate-500 text-xs py-2">
                            No error data available
                        </div>
                    </div>
                </div>

                <!-- Last Updated -->
                <div class="last-updated text-xs text-slate-500 text-center mt-4">
                    Last updated: Never
                </div>
            </div>
        `;

        // Attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        const toggle = this.container.querySelector('.error-types-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                const content = this.container.querySelector('.error-types-content');
                const icon = toggle.querySelector('.fa-chevron-down');
                
                if (content.classList.contains('hidden')) {
                    content.classList.remove('hidden');
                    icon.classList.add('rotate-180');
                } else {
                    content.classList.add('hidden');
                    icon.classList.remove('rotate-180');
                }
            });
        }
    }

    async updateStatus(data) {
        this.statusData = data;
        
        if (!data) {
            // Fetch from API
            try {
                const response = await fetch('/api/feature-status');
                data = await response.json();
                this.statusData = data;
            } catch (error) {
                console.error('Failed to fetch status:', error);
                return;
            }
        }

        this.renderOverallStatus(data);
        this.renderMetrics(data);
        this.renderFeatureStatus(data);
        this.renderErrorTypes(data);
        this.updateTimestamp();
    }

    renderOverallStatus(data) {
        const badge = this.container.querySelector('.status-badge');
        if (!badge) return;

        let status = 'operational';
        let statusClass = 'bg-green-900/30 text-green-400 border border-green-900/50';
        let icon = 'fa-check-circle';

        if (data.circuit_breakers) {
            const breakers = Object.values(data.circuit_breakers);
            const openBreakers = breakers.filter(b => b.state === 'OPEN').length;
            const halfOpenBreakers = breakers.filter(b => b.state === 'HALF_OPEN').length;

            if (openBreakers > 0) {
                status = 'degraded';
                statusClass = 'bg-yellow-900/30 text-yellow-400 border border-yellow-900/50';
                icon = 'fa-exclamation-triangle';
            } else if (halfOpenBreakers > 0) {
                status = 'recovering';
                statusClass = 'bg-blue-900/30 text-blue-400 border border-blue-900/50';
                icon = 'fa-sync-alt fa-spin';
            }
        }

        badge.className = `status-badge px-3 py-1 rounded-full text-xs font-semibold ${statusClass}`;
        badge.innerHTML = `<i class="fas ${icon} mr-1"></i>${status.charAt(0).toUpperCase() + status.slice(1)}`;
    }

    renderMetrics(data) {
        // Error Rate
        if (data.error_stats) {
            const errorRate = data.error_stats.error_rate || 0;
            const errorRateEl = this.container.querySelector('.error-rate-value');
            if (errorRateEl) {
                errorRateEl.textContent = `${errorRate.toFixed(2)}%`;
                errorRateEl.className = `error-rate-value text-xl font-bold ${
                    errorRate > 5 ? 'text-red-400' : errorRate > 2 ? 'text-yellow-400' : 'text-green-400'
                }`;
            }

            // Total Errors
            const totalErrors = data.error_stats.total_errors || 0;
            const totalErrorsEl = this.container.querySelector('.total-errors-value');
            if (totalErrorsEl) {
                totalErrorsEl.textContent = totalErrors;
            }
        }

        // Latency (from connection monitor if available)
        if (window.connectionMonitor) {
            const status = connectionMonitor.getStatus();
            if (status.latency !== null) {
                const latencyEl = this.container.querySelector('.latency-value');
                if (latencyEl) {
                    latencyEl.textContent = `${status.latency}ms`;
                    latencyEl.className = `latency-value text-xl font-bold ${
                        status.latency > 1000 ? 'text-red-400' : status.latency > 500 ? 'text-yellow-400' : 'text-green-400'
                    }`;
                }
            }
        }
    }

    renderFeatureStatus(data) {
        const featureList = this.container.querySelector('.feature-list');
        if (!featureList) return;

        if (!data.circuit_breakers && !data.features) {
            featureList.innerHTML = '<div class="text-center text-slate-500 text-sm py-2">No feature data available</div>';
            return;
        }

        let html = '';

        // Circuit breakers
        if (data.circuit_breakers) {
            Object.entries(data.circuit_breakers).forEach(([name, breaker]) => {
                const statusColor = {
                    'CLOSED': 'green',
                    'OPEN': 'red',
                    'HALF_OPEN': 'yellow'
                }[breaker.state] || 'gray';

                html += `
                    <div class="feature-item flex items-center justify-between p-2 rounded bg-slate-900/30 border border-slate-700">
                        <div class="flex items-center space-x-2">
                            <i class="fas fa-plug text-${statusColor}-500"></i>
                            <span class="text-sm text-slate-300">${this.formatFeatureName(name)}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="text-xs px-2 py-0.5 rounded-full bg-${statusColor}-900/30 text-${statusColor}-400 border border-${statusColor}-900/50">
                                ${breaker.state}
                            </span>
                            ${breaker.state === 'OPEN' ? `
                                <button onclick="statusDashboard.resetCircuitBreaker('${name}')" 
                                        class="text-xs px-2 py-0.5 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                                        title="Reset circuit breaker">
                                    <i class="fas fa-redo"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
        }

        // Features
        if (data.features) {
            Object.entries(data.features).forEach(([name, feature]) => {
                const enabled = feature.enabled;
                const statusColor = enabled ? 'green' : 'red';

                html += `
                    <div class="feature-item flex items-center justify-between p-2 rounded bg-slate-900/30 border border-slate-700">
                        <div class="flex items-center space-x-2">
                            <i class="fas fa-cube text-${statusColor}-500"></i>
                            <span class="text-sm text-slate-300">${this.formatFeatureName(name)}</span>
                        </div>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-${statusColor}-900/30 text-${statusColor}-400 border border-${statusColor}-900/50">
                            ${enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                `;
            });
        }

        featureList.innerHTML = html;
    }

    renderErrorTypes(data) {
        const errorTypesContent = this.container.querySelector('.error-types-content');
        if (!errorTypesContent) return;

        if (!data.error_stats || !data.error_stats.by_type || Object.keys(data.error_stats.by_type).length === 0) {
            errorTypesContent.innerHTML = '<div class="text-center text-slate-500 text-xs py-2">No errors recorded</div>';
            return;
        }

        let html = '';
        const sortedErrors = Object.entries(data.error_stats.by_type)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5); // Top 5 error types

        sortedErrors.forEach(([type, count]) => {
            const percentage = ((count / data.error_stats.total_errors) * 100).toFixed(1);
            html += `
                <div class="error-type-item flex items-center justify-between p-2 rounded bg-slate-900/30 text-xs">
                    <span class="text-slate-400">${type}</span>
                    <div class="flex items-center space-x-2">
                        <span class="text-slate-300 font-semibold">${count}</span>
                        <span class="text-slate-500">(${percentage}%)</span>
                    </div>
                </div>
            `;
        });

        errorTypesContent.innerHTML = html;
    }

    updateTimestamp() {
        const timestampEl = this.container.querySelector('.last-updated');
        if (timestampEl) {
            const now = new Date();
            timestampEl.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        }
    }

    formatFeatureName(name) {
        return name
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    async resetCircuitBreaker(featureName) {
        try {
            const response = await fetch(`/api/reset-circuit-breaker/${featureName}`);
            const result = await response.json();
            
            if (result.success) {
                showSuccess(`${this.formatFeatureName(featureName)} circuit breaker reset`, 3000);
                this.refresh();
            } else {
                showError(`Failed to reset circuit breaker: ${result.message}`, 5000);
            }
        } catch (error) {
            console.error('Failed to reset circuit breaker:', error);
            showError('Failed to reset circuit breaker', 5000);
        }
    }

    async refresh() {
        await this.updateStatus(null);
    }

    startAutoRefresh(interval = 30000) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.refresh();
        }, interval);
    }

    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Global instance (will be initialized when container is available)
let statusDashboard = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('status-dashboard');
    if (container) {
        statusDashboard = new StatusDashboard(container);
    }
});
