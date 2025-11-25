// Modern Enterprise Dashboard JavaScript

class SentinelDashboard {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.darkMode = localStorage.getItem('darkMode') === 'true';
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupCharts();
        this.setupEventListeners();
        this.loadInitialData();
        this.applyDarkMode();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/stream`);
        
        this.ws.onopen = () => {
            console.log('✓ WebSocket connected');
            this.showNotification('Connected to Sentinel', 'success');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateStats(data);
            this.updateCharts(data);
        };
        
        this.ws.onerror = () => {
            console.error('✗ WebSocket error');
            this.showNotification('Connection error', 'error');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket closed, reconnecting...');
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }

    setupCharts() {
        // Severity Distribution Chart
        const severityCtx = document.getElementById('severityChart');
        if (severityCtx) {
            this.charts.severity = new Chart(severityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: [
                            '#e74c3c',
                            '#f39c12',
                            '#3498db'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: { size: 12 }
                            }
                        }
                    }
                }
            });
        }

        // Timeline Chart
        const timelineCtx = document.getElementById('timelineChart');
        if (timelineCtx) {
            this.charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Alerts',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }

        // Actions Chart
        const actionsCtx = document.getElementById('actionsChart');
        if (actionsCtx) {
            this.charts.actions = new Chart(actionsCtx, {
                type: 'bar',
                data: {
                    labels: ['Isolate', 'Block', 'Redirect', 'Rate Limit', 'Log'],
                    datasets: [{
                        label: 'Actions',
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#e74c3c',
                            '#e67e22',
                            '#f39c12',
                            '#3498db',
                            '#95a5a6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }
    }

    async loadInitialData() {
        try {
            const [stats, alerts] = await Promise.all([
                fetch('/stats').then(r => r.json()),
                fetch('/alerts?limit=10').then(r => r.json())
            ]);
            
            this.updateStats(stats);
            this.updateSeverityChart(stats);
            this.updateActionsChart(stats);
            this.updateAlertsTable(alerts.items);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    updateStats(data) {
        this.updateElement('alertsCount', data.alerts || 0);
        this.updateElement('investigationsCount', data.investigations || 0);
        this.updateElement('actionsCount', data.actions || 0);
        
        // Calculate and update trends
        this.updateTrend('alertsTrend', data.alerts);
        this.updateTrend('investigationsTrend', data.investigations);
        this.updateTrend('actionsTrend', data.actions);
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            // Animate number change
            const current = parseInt(element.textContent) || 0;
            if (current !== value) {
                this.animateValue(element, current, value, 500);
            }
        }
    }

    animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.round(current);
        }, 16);
    }

    updateTrend(id, value) {
        const element = document.getElementById(id);
        if (element && this.lastValues) {
            const lastValue = this.lastValues[id] || 0;
            const diff = value - lastValue;
            
            if (diff > 0) {
                element.innerHTML = `<span class="trend-up">↑ ${diff}</span>`;
            } else if (diff < 0) {
                element.innerHTML = `<span class="trend-down">↓ ${Math.abs(diff)}</span>`;
            }
        }
        
        if (!this.lastValues) this.lastValues = {};
        this.lastValues[id] = value;
    }

    updateSeverityChart(stats) {
        if (this.charts.severity && stats.alert_severities) {
            const data = [
                stats.alert_severities.high || 0,
                stats.alert_severities.medium || 0,
                stats.alert_severities.low || 0
            ];
            this.charts.severity.data.datasets[0].data = data;
            this.charts.severity.update();
        }
    }

    updateActionsChart(stats) {
        if (this.charts.actions && stats.action_types) {
            const data = [
                stats.action_types.isolate_container || 0,
                stats.action_types.block_ip || 0,
                stats.action_types.redirect_to_honeypot || 0,
                stats.action_types.rate_limit || 0,
                stats.action_types.log_only || 0
            ];
            this.charts.actions.data.datasets[0].data = data;
            this.charts.actions.update();
        }
    }

    updateCharts(data) {
        // Update timeline chart
        if (this.charts.timeline) {
            const now = new Date().toLocaleTimeString();
            const labels = this.charts.timeline.data.labels;
            const values = this.charts.timeline.data.datasets[0].data;
            
            labels.push(now);
            values.push(data.alerts || 0);
            
            // Keep only last 20 data points
            if (labels.length > 20) {
                labels.shift();
                values.shift();
            }
            
            this.charts.timeline.update();
        }
    }

    async updateAlertsTable(alerts) {
        const tbody = document.getElementById('alertsTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = alerts.map(alert => `
            <tr class="fade-in">
                <td>${new Date(alert.ts * 1000).toLocaleString()}</td>
                <td><code>${alert.src_ip}</code></td>
                <td><code>${alert.dst_ip}</code></td>
                <td><span class="severity-badge severity-${alert.severity}">${alert.severity}</span></td>
                <td>${(alert.model_score * 100).toFixed(1)}%</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="dashboard.viewDetails('${alert.id}')">
                        Details
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async generateReport() {
        const button = document.getElementById('generateReportBtn');
        const status = document.getElementById('reportStatus');
        
        button.disabled = true;
        button.innerHTML = '<span class="spinner-small"></span> Generating...';
        
        try {
            const response = await fetch('/report/generate');
            const data = await response.json();
            
            if (data.status === 'success') {
                const filename = data.report_path.split(/[\\/]/).pop();
                status.innerHTML = `
                    <div class="status-message status-success show">
                        ✓ Report generated successfully! 
                        <a href="/report/download/${filename}" class="btn btn-sm btn-success">
                            Download PDF
                        </a>
                    </div>
                `;
                this.showNotification('Report generated successfully!', 'success');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            status.innerHTML = `
                <div class="status-message status-error show">
                    ✗ Error: ${error.message}
                </div>
            `;
            this.showNotification('Error generating report', 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = '📊 Generate Report';
        }
    }

    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
        this.applyDarkMode();
    }

    applyDarkMode() {
        if (this.darkMode) {
            document.body.classList.add('dark-mode');
            document.getElementById('darkModeToggle')?.classList.add('active');
        } else {
            document.body.classList.remove('dark-mode');
            document.getElementById('darkModeToggle')?.classList.remove('active');
        }
        
        // Update chart colors for dark mode
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.update();
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} slide-up`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    async viewDetails(alertId) {
        // Fetch and display alert details
        try {
            const response = await fetch(`/alerts`);
            const data = await response.json();
            const alert = data.items.find(a => a.id === alertId);
            
            if (alert) {
                alert('Alert Details:\n' + JSON.stringify(alert, null, 2));
            }
        } catch (error) {
            this.showNotification('Error loading details', 'error');
        }
    }

    setupEventListeners() {
        // Report generation
        const reportBtn = document.getElementById('generateReportBtn');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => this.generateReport());
        }
        
        // Dark mode toggle
        const darkModeBtn = document.getElementById('darkModeToggle');
        if (darkModeBtn) {
            darkModeBtn.addEventListener('click', () => this.toggleDarkMode());
        }
        
        // Refresh data
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadInitialData());
        }
    }
}

// Initialize dashboard when DOM is ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SentinelDashboard();
});
