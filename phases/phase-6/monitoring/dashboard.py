"""Monitoring dashboard for the restaurant recommendation system."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from .metrics import metrics, health_checker
from .logging import logger


app = FastAPI(title="Monitoring Dashboard", version="1.0.0")

# Templates
templates = Jinja2Templates(directory="phases/phase-6/monitoring/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main monitoring dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/metrics")
async def get_metrics(time_window: int = 300):
    """Get current metrics."""
    return metrics.get_summary_metrics(time_window)


@app.get("/api/time-series")
async def get_time_series(metric: str, time_window: int = 3600, interval: int = 60):
    """Get time series data for metrics."""
    return metrics.get_time_series_data(metric, time_window, interval)


@app.get("/api/health")
async def get_system_health():
    """Get system health status."""
    return health_checker.run_all_checks()


@app.get("/api/logs")
async def get_recent_logs(limit: int = 100):
    """Get recent log entries."""
    # This would typically read from a log file or logging service
    # For now, return a placeholder
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "System operating normally",
                "request_id": "12345"
            }
        ]
    }


# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Recommendation System - Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .header .subtitle {
            opacity: 0.9;
            margin-top: 0.25rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-title {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .metric-change {
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .metric-change.positive {
            color: #10b981;
        }
        
        .metric-change.negative {
            color: #ef4444;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .chart-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .health-section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .health-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .health-checks {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .health-check {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .health-check.healthy {
            background: #d1fae5;
            color: #065f46;
        }
        
        .health-check.unhealthy {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .health-status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.75rem;
        }
        
        .health-status.healthy {
            background: #10b981;
        }
        
        .health-status.unhealthy {
            background: #ef4444;
        }
        
        .alerts-section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }
        
        .alert.warning {
            background: #fef3c7;
            border-color: #f59e0b;
            color: #92400e;
        }
        
        .alert.critical {
            background: #fee2e2;
            border-color: #ef4444;
            color: #991b1b;
        }
        
        .refresh-button {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #667eea;
            color: white;
            border: none;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: background 0.2s;
        }
        
        .refresh-button:hover {
            background: #5a67d8;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .charts-section {
                grid-template-columns: 1fr;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Restaurant Recommendation System</h1>
        <div class="subtitle">Real-time Monitoring Dashboard</div>
    </div>
    
    <div class="container">
        <!-- Metrics Cards -->
        <div class="metrics-grid" id="metrics-grid">
            <div class="loading">Loading metrics...</div>
        </div>
        
        <!-- Charts Section -->
        <div class="charts-section">
            <div class="chart-card">
                <h3 class="chart-title">Response Time Trend</h3>
                <canvas id="response-time-chart"></canvas>
            </div>
            <div class="chart-card">
                <h3 class="chart-title">Request Volume</h3>
                <canvas id="request-volume-chart"></canvas>
            </div>
        </div>
        
        <!-- Health Section -->
        <div class="health-section">
            <h3 class="health-title">System Health</h3>
            <div class="health-checks" id="health-checks">
                <div class="loading">Loading health checks...</div>
            </div>
        </div>
        
        <!-- Alerts Section -->
        <div class="alerts-section" id="alerts-section" style="display: none;">
            <h3 class="health-title">Active Alerts</h3>
            <div id="alerts-list"></div>
        </div>
    </div>
    
    <button class="refresh-button" onclick="refreshData()">Refresh Data</button>
    
    <script>
        let responseTimeChart = null;
        let requestVolumeChart = null;
        
        // Initialize charts
        function initCharts() {
            const ctx1 = document.getElementById('response-time-chart').getContext('2d');
            responseTimeChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Response Time (s)',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Response Time (s)'
                            }
                        }
                    }
                }
            });
            
            const ctx2 = document.getElementById('request-volume-chart').getContext('2d');
            requestVolumeChart = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Requests per Minute',
                        data: [],
                        backgroundColor: '#10b981'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Requests per Minute'
                            }
                        }
                    }
                }
            });
        }
        
        // Update metrics cards
        function updateMetrics(data) {
            const metricsGrid = document.getElementById('metrics-grid');
            
            const metricsHtml = `
                <div class="metric-card">
                    <div class="metric-title">Total Requests</div>
                    <div class="metric-value">${data.request_metrics.total_requests}</div>
                    <div class="metric-change positive">${data.request_metrics.requests_per_minute.toFixed(1)}/min</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Success Rate</div>
                    <div class="metric-value">${data.performance_metrics.error_rate > 0 ? (100 - data.performance_metrics.error_rate).toFixed(1) : 100}%</div>
                    <div class="metric-change ${data.performance_metrics.error_rate > 5 ? 'negative' : 'positive'}">
                        Error Rate: ${data.performance_metrics.error_rate.toFixed(1)}%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Avg Response Time</div>
                    <div class="metric-value">${data.performance_metrics.avg_response_time.toFixed(2)}s</div>
                    <div class="metric-change ${data.performance_metrics.avg_response_time > 2 ? 'negative' : 'positive'}">
                        P95: ${data.performance_metrics.p95_response_time.toFixed(2)}s
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Active Requests</div>
                    <div class="metric-value">${data.request_metrics.active_requests}</div>
                    <div class="metric-change">Catalog: ${data.system_metrics.catalog_size} items</div>
                </div>
            `;
            
            metricsGrid.innerHTML = metricsHtml;
        }
        
        // Update health checks
        function updateHealth(data) {
            const healthChecks = document.getElementById('health-checks');
            
            let checksHtml = '';
            for (const [name, check] of Object.entries(data.checks)) {
                const statusClass = check.status === 'healthy' ? 'healthy' : 'unhealthy';
                checksHtml += `
                    <div class="health-check ${statusClass}">
                        <div class="health-status ${statusClass}"></div>
                        <div>
                            <div style="font-weight: 600;">${name}</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">
                                ${check.status === 'healthy' ? 'Operational' : check.error || 'Unavailable'}
                            </div>
                        </div>
                    </div>
                `;
            }
            
            healthChecks.innerHTML = checksHtml;
        }
        
        // Update alerts
        function updateAlerts(alerts) {
            const alertsSection = document.getElementById('alerts-section');
            const alertsList = document.getElementById('alerts-list');
            
            if (alerts.length === 0) {
                alertsSection.style.display = 'none';
                return;
            }
            
            alertsSection.style.display = 'block';
            
            let alertsHtml = '';
            for (const alert of alerts) {
                const alertClass = alert.severity === 'critical' ? 'critical' : 'warning';
                alertsHtml += `
                    <div class="alert ${alertClass}">
                        <strong>${alert.severity.toUpperCase()}:</strong> ${alert.message}
                        <div style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">
                            ${new Date(alert.timestamp * 1000).toLocaleString()}
                        </div>
                    </div>
                `;
            }
            
            alertsList.innerHTML = alertsHtml;
        }
        
        // Update charts
        async function updateCharts() {
            try {
                const response = await fetch('/api/time-series?metric=response_time&time_window=3600&interval=300');
                const data = await response.json();
                
                if (responseTimeChart) {
                    responseTimeChart.data.labels = data.map(point => 
                        new Date(point.timestamp * 1000).toLocaleTimeString()
                    );
                    responseTimeChart.data.datasets[0].data = data.map(point => point.value);
                    responseTimeChart.update();
                }
                
                // Update request volume chart (using same data for demo)
                if (requestVolumeChart) {
                    requestVolumeChart.data.labels = data.map(point => 
                        new Date(point.timestamp * 1000).toLocaleTimeString()
                    );
                    requestVolumeChart.data.datasets[0].data = data.map(point => point.count);
                    requestVolumeChart.update();
                }
            } catch (error) {
                console.error('Error updating charts:', error);
            }
        }
        
        // Refresh all data
        async function refreshData() {
            try {
                // Get metrics
                const metricsResponse = await fetch('/api/metrics');
                const metricsData = await metricsResponse.json();
                updateMetrics(metricsData);
                updateAlerts(metricsData.alerts || []);
                
                // Get health
                const healthResponse = await fetch('/api/health');
                const healthData = await healthResponse.json();
                updateHealth(healthData);
                
                // Update charts
                updateCharts();
                
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
"""


@app.get("/dashboard", response_class=HTMLResponse)
async def standalone_dashboard():
    """Standalone dashboard endpoint."""
    return HTMLResponse(content=DASHBOARD_HTML)


def create_template_directory():
    """Create template directory and file."""
    import os
    
    template_dir = "phases/phase-6/monitoring/templates"
    os.makedirs(template_dir, exist_ok=True)
    
    with open(f"{template_dir}/dashboard.html", "w") as f:
        f.write(DASHBOARD_HTML)


def add_health_checks():
    """Add default health checks."""
    import httpx
    
    async def check_phase2_health():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://127.0.0.1:8200/health")
                return response.status_code == 200
        except:
            return False
    
    async def check_phase3_health():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://127.0.0.1:8300/health")
                return response.status_code == 200
        except:
            return False
    
    async def check_phase4_health():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://127.0.0.1:8401/health")
                return response.status_code == 200
        except:
            return False
    
    async def check_phase5_health():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://127.0.0.1:8500/health")
                return response.status_code == 200
        except:
            return False
    
    health_checker.add_check("Phase 2 Service", check_phase2_health)
    health_checker.add_check("Phase 3 Service", check_phase3_health)
    health_checker.add_check("Phase 4 Service", check_phase4_health)
    health_checker.add_check("Phase 5 Service", check_phase5_health)


if __name__ == "__main__":
    create_template_directory()
    add_health_checks()
    
    print("Starting Monitoring Dashboard...")
    print("Dashboard will be available at: http://127.0.0.1:8600")
    print("Standalone dashboard: http://127.0.0.1:8600/dashboard")
    
    uvicorn.run(app, host="127.0.0.1", port=8600, log_level="info")
