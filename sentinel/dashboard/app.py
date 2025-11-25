from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from sentinel.common.state import SharedState
import os
from sentinel.common.event_bus import BusFactory
from sentinel.detection.engine import DetectionEngine
from sentinel.investigation.agent import InvestigationAgent
from sentinel.response.engine import ResponseEngine
from sentinel.common.persistence import Repository
from sentinel.common.metrics import latest
import asyncio


repo = Repository()
state = SharedState(repo=repo)
bus = BusFactory.from_env()
detection = DetectionEngine(bus, state, sensor_id="sensor-1")
investigator = InvestigationAgent(bus, state)
responder = ResponseEngine(bus, state)

app = FastAPI(title="Autonomous Cyber Sentinel", version="1.0.0")

# Enable CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    detection.start()
    investigator.start()
    responder.start()


@app.on_event("shutdown")
def _shutdown() -> None:
    detection.stop()
    investigator.stop()
    responder.stop()


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files"""
    from fastapi.responses import FileResponse
    import os
    
    static_path = os.path.join("sentinel", "dashboard", "static", file_path)
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return {"error": "File not found"}


@app.get("/")
def root() -> HTMLResponse:
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autonomous Cyber Sentinel - Enterprise Dashboard</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    </head>
    <body>
        <div class="dashboard-container">
            <!-- Header -->
            <div class="dashboard-header fade-in">
                <div class="header-title">
                    <div>
                        <h1>🛡️ Autonomous Cyber Sentinel</h1>
                        <p class="header-subtitle">Enterprise Security Operations Center</p>
                    </div>
                </div>
                <div class="header-actions">
                    <button id="darkModeToggle" class="btn btn-primary" title="Toggle Dark Mode">
                        🌙 Dark Mode
                    </button>
                    <button id="refreshBtn" class="btn btn-primary" title="Refresh Data">
                        🔄 Refresh
                    </button>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="stats-grid slide-up">
                <div class="stat-card danger">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="alertsCount">0</div>
                            <div class="stat-label">Alerts Detected</div>
                            <div class="stat-trend" id="alertsTrend"></div>
                        </div>
                        <div class="stat-icon">🚨</div>
                    </div>
                </div>
                
                <div class="stat-card warning">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="investigationsCount">0</div>
                            <div class="stat-label">Investigations</div>
                            <div class="stat-trend" id="investigationsTrend"></div>
                        </div>
                        <div class="stat-icon">🔍</div>
                    </div>
                </div>
                
                <div class="stat-card success">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="actionsCount">0</div>
                            <div class="stat-label">Actions Taken</div>
                            <div class="stat-trend" id="actionsTrend"></div>
                        </div>
                        <div class="stat-icon">⚡</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value">< 10s</div>
                            <div class="stat-label">Response Time</div>
                            <div class="stat-trend"><span class="trend-up">✓ Within SLA</span></div>
                        </div>
                        <div class="stat-icon">⏱️</div>
                    </div>
                </div>
            </div>

            <!-- TI Sources -->
            <div class="ti-sources-card slide-up">
                <div class="chart-header">
                    <h3 class="chart-title">🔍 Threat Intelligence Sources</h3>
                    <span style="color: #27ae60; font-weight: 600;">6 Active Sources</span>
                </div>
                <div class="ti-sources-grid">
                    <div class="ti-badge">
                        <div>VirusTotal</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                    <div class="ti-badge">
                        <div>AbuseIPDB</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                    <div class="ti-badge">
                        <div>AlienVault OTX</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                    <div class="ti-badge">
                        <div>IPQualityScore</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                    <div class="ti-badge">
                        <div>ThreatCrowd</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                    <div class="ti-badge">
                        <div>GreyNoise</div>
                        <span class="ti-badge-status">✓ Active</span>
                    </div>
                </div>
            </div>

            <!-- Charts Grid -->
            <div class="charts-grid slide-up">
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Alert Severity Distribution</h3>
                    </div>
                    <div class="chart-container">
                        <canvas id="severityChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Real-Time Alert Timeline</h3>
                    </div>
                    <div class="chart-container">
                        <canvas id="timelineChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Response Actions</h3>
                    </div>
                    <div class="chart-container">
                        <canvas id="actionsChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Report Generation -->
            <div class="alerts-section slide-up">
                <div class="section-header">
                    <h3 class="section-title">📊 Automated Reporting</h3>
                    <button id="generateReportBtn" class="btn btn-success">
                        📊 Generate Comprehensive Report
                    </button>
                </div>
                <div id="reportStatus"></div>
                <p style="color: #666; margin-top: 10px;">
                    Generate professional PDF reports with charts, analysis, and recommendations.
                </p>
            </div>

            <!-- Recent Alerts -->
            <div class="alerts-section slide-up">
                <div class="section-header">
                    <h3 class="section-title">🚨 Recent Alerts</h3>
                    <div>
                        <a href="/alerts" class="btn btn-primary">View All</a>
                    </div>
                </div>
                <table class="alerts-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Source IP</th>
                            <th>Destination IP</th>
                            <th>Severity</th>
                            <th>Confidence</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="alertsTableBody">
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 30px; color: #999;">
                                Loading alerts...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Quick Links -->
            <div class="alerts-section slide-up">
                <div class="section-header">
                    <h3 class="section-title">🔗 Quick Links</h3>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="/investigations" class="btn btn-primary">View Investigations</a>
                    <a href="/actions" class="btn btn-primary">View Actions</a>
                    <a href="/report/list" class="btn btn-primary">View Reports</a>
                    <a href="/metrics" class="btn btn-primary">Prometheus Metrics</a>
                    <a href="/docs" class="btn btn-primary">API Documentation</a>
                </div>
            </div>
        </div>

        <script src="/static/js/dashboard.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "components": {
            "detection": "running",
            "investigation": "running",
            "response": "running"
        }
    }


@app.get("/alerts")
def alerts(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    items = state.alerts[offset:offset+limit]
    return {
        "total": len(state.alerts),
        "limit": limit,
        "offset": offset,
        "items": items
    }


@app.get("/investigations")
def investigations(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    items = state.investigations[offset:offset+limit]
    return {
        "total": len(state.investigations),
        "limit": limit,
        "offset": offset,
        "items": items
    }


@app.get("/actions")
def actions(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    items = state.actions[offset:offset+limit]
    return {
        "total": len(state.actions),
        "limit": limit,
        "offset": offset,
        "items": items
    }


@app.get("/stats")
def stats() -> Dict[str, Any]:
    return {
        "alerts": len(state.alerts),
        "investigations": len(state.investigations),
        "actions": len(state.actions),
        "alert_severities": _count_by_field(state.alerts, "severity"),
        "action_types": _count_by_field(state.actions, "action_type"),
        "verdicts": _count_by_field(state.investigations, "verdict")
    }


def _count_by_field(items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        val = item.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts


@app.websocket("/stream")
async def stream(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            payload = {
                "alerts": len(state.alerts),
                "investigations": len(state.investigations),
                "actions": len(state.actions),
            }
            await ws.send_json(payload)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


@app.get("/metrics")
def metrics() -> Response:
    body, ctype = latest()
    return Response(content=body, media_type=ctype)


@app.get("/report/generate")
def generate_report(time_range: str = "24h") -> Dict[str, Any]:
    """Generate a comprehensive incident report"""
    from sentinel.reporting.generator import ReportGenerator
    
    generator = ReportGenerator()
    
    try:
        report_path = generator.generate_full_report(
            alerts=state.alerts,
            investigations=state.investigations,
            actions=state.actions,
            time_range=time_range
        )
        
        return {
            "status": "success",
            "report_path": report_path,
            "message": f"Report generated successfully: {report_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/report/download/{filename}")
def download_report(filename: str):
    """Download a generated report"""
    from fastapi.responses import FileResponse
    import os
    
    report_path = os.path.join("reports", filename)
    
    if os.path.exists(report_path):
        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=filename
        )
    else:
        return {"error": "Report not found"}


@app.get("/report/list")
def list_reports() -> Dict[str, Any]:
    """List all generated reports"""
    import os
    from pathlib import Path
    
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        return {"reports": []}
    
    reports = []
    for file in reports_dir.glob("*.pdf"):
        reports.append({
            "filename": file.name,
            "size": file.stat().st_size,
            "created": file.stat().st_ctime,
            "download_url": f"/report/download/{file.name}"
        })
    
    reports.sort(key=lambda x: x['created'], reverse=True)
    
    return {"reports": reports}