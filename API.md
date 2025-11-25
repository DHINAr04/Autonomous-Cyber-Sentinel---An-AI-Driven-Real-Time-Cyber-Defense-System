# 📡 Autonomous Cyber Sentinel API Documentation

Complete API reference for the Autonomous Cyber Sentinel system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, implement API key authentication or OAuth2.

## Endpoints

### System Health

#### GET /health

Check system health and component status.

**Response**
```json
{
  "status": "ok",
  "components": {
    "detection": "running",
    "investigation": "running",
    "response": "running"
  }
}
```

**Status Codes**
- `200 OK`: System is healthy
- `503 Service Unavailable`: System is unhealthy

---

### Statistics

#### GET /stats

Get current system statistics and metrics.

**Response**
```json
{
  "alerts": 42,
  "investigations": 42,
  "actions": 38,
  "alert_severities": {
    "low": 15,
    "medium": 18,
    "high": 9
  },
  "action_types": {
    "log_only": 20,
    "redirect_to_honeypot": 10,
    "isolate_container": 8
  },
  "verdicts": {
    "benign": 25,
    "suspicious": 12,
    "malicious": 5
  }
}
```

---

### Alerts

#### GET /alerts

Retrieve detected alerts with pagination.

**Query Parameters**
- `limit` (integer, optional): Number of items to return (default: 100)
- `offset` (integer, optional): Number of items to skip (default: 0)

**Example Request**
```bash
GET /alerts?limit=10&offset=0
```

**Response**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ts": 1701234567.89,
      "src_ip": "10.0.0.5",
      "dst_ip": "10.0.0.10",
      "proto": "tcp",
      "features": {
        "bytes": 15000,
        "pkts": 150,
        "iat_avg": 0.05
      },
      "model_score": 0.85,
      "confidence": 0.85,
      "severity": "high",
      "sensor_id": "sensor-1"
    }
  ]
}
```

**Alert Object Fields**
- `id`: Unique alert identifier
- `ts`: Unix timestamp
- `src_ip`: Source IP address
- `dst_ip`: Destination IP address
- `proto`: Protocol (tcp, udp, icmp, etc.)
- `features`: Network traffic features
- `model_score`: ML model threat score (0-1)
- `confidence`: Detection confidence (0-1)
- `severity`: Threat severity (low, medium, high)
- `sensor_id`: Sensor that detected the threat

---

### Investigations

#### GET /investigations

Retrieve threat intelligence investigation results.

**Query Parameters**
- `limit` (integer, optional): Number of items to return (default: 100)
- `offset` (integer, optional): Number of items to skip (default: 0)

**Example Request**
```bash
GET /investigations?limit=10&offset=0
```

**Response**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "alert_id": "550e8400-e29b-41d4-a716-446655440000",
      "ts": 1701234568.12,
      "ioc_findings": {
        "vt": {
          "source": "vt",
          "ip": "10.0.0.5",
          "reputation": 45,
          "mocked": true
        },
        "abuseipdb": {
          "source": "abuseipdb",
          "ip": "10.0.0.5",
          "abuse_score": 67,
          "mocked": true
        },
        "otx": {
          "source": "otx",
          "ip": "10.0.0.5",
          "pulses": 3,
          "mocked": true
        }
      },
      "sources": ["virustotal", "abuseipdb", "otx"],
      "risk_score": 0.78,
      "verdict": "malicious",
      "notes": "automatic investigation",
      "uncertainty": 0.2,
      "confidence": 0.8,
      "alert_severity": "high"
    }
  ]
}
```

**Investigation Object Fields**
- `alert_id`: Associated alert ID
- `ts`: Investigation timestamp
- `ioc_findings`: Threat intelligence findings from each source
- `sources`: List of TI sources queried
- `risk_score`: Calculated risk score (0-1)
- `verdict`: Investigation verdict (benign, suspicious, malicious)
- `notes`: Additional notes
- `uncertainty`: Uncertainty level (0-1)
- `confidence`: Investigation confidence (0-1)
- `alert_severity`: Original alert severity

---

### Actions

#### GET /actions

Retrieve autonomous response actions taken.

**Query Parameters**
- `limit` (integer, optional): Number of items to return (default: 100)
- `offset` (integer, optional): Number of items to skip (default: 0)

**Example Request**
```bash
GET /actions?limit=10&offset=0
```

**Response**
```json
{
  "total": 38,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "action_id": "550e8400-e29b-41d4-a716-446655440000",
      "alert_id": "550e8400-e29b-41d4-a716-446655440000",
      "ts": 1701234569.45,
      "action_type": "isolate_container",
      "target": "container://app1",
      "parameters": {
        "verdict": "malicious"
      },
      "result": "simulated_isolation",
      "safety_gate": "high",
      "reversible": "yes",
      "reverted": "no"
    }
  ]
}
```

**Action Object Fields**
- `action_id`: Unique action identifier
- `alert_id`: Associated alert ID
- `ts`: Action timestamp
- `action_type`: Type of action taken
  - `log_only`: Only log the event
  - `redirect_to_honeypot`: Redirect to honeypot
  - `isolate_container`: Isolate container from network
  - `block_ip`: Block IP address
  - `rate_limit`: Apply rate limiting
  - `quarantine_file`: Quarantine file
- `target`: Target of the action
- `parameters`: Action parameters
- `result`: Action result
- `safety_gate`: Safety level (low, medium, high)
- `reversible`: Whether action can be reversed (yes/no)
- `reverted`: Whether action has been reverted (yes/no)

---

### Metrics

#### GET /metrics

Get Prometheus-compatible metrics.

**Response Format**: Prometheus text format

**Example Response**
```
# HELP alerts_total Total alerts generated
# TYPE alerts_total counter
alerts_total 42.0
# HELP investigations_total Total investigations generated
# TYPE investigations_total counter
investigations_total 42.0
# HELP actions_total Total actions executed
# TYPE actions_total counter
actions_total 38.0
```

**Use with Prometheus**
```yaml
scrape_configs:
  - job_name: 'sentinel'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

### WebSocket Stream

#### WS /stream

Real-time event stream via WebSocket.

**Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Stats:', data);
};
```

**Message Format**
```json
{
  "alerts": 42,
  "investigations": 42,
  "actions": 38
}
```

**Update Frequency**: Every 1 second

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes**
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting to prevent abuse.

---

## Examples

### Python

```python
import requests

# Get system health
response = requests.get('http://localhost:8000/health')
print(response.json())

# Get recent alerts
response = requests.get('http://localhost:8000/alerts', params={'limit': 5})
alerts = response.json()
print(f"Total alerts: {alerts['total']}")

# Get statistics
response = requests.get('http://localhost:8000/stats')
stats = response.json()
print(f"High severity alerts: {stats['alert_severities']['high']}")
```

### PowerShell

```powershell
# Get system health
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
Write-Host "Status: $($health.status)"

# Get recent alerts
$alerts = Invoke-RestMethod -Uri "http://localhost:8000/alerts?limit=5"
Write-Host "Total alerts: $($alerts.total)"

# Get statistics
$stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
Write-Host "Alerts: $($stats.alerts)"
```

### cURL

```bash
# Get system health
curl http://localhost:8000/health

# Get recent alerts
curl "http://localhost:8000/alerts?limit=5"

# Get statistics
curl http://localhost:8000/stats

# Get metrics
curl http://localhost:8000/metrics
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test API calls directly from the browser
- Download OpenAPI specification

---

## WebSocket Example

### JavaScript

```javascript
const ws = new WebSocket('ws://localhost:8000/stream');

ws.onopen = () => {
  console.log('Connected to Sentinel stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  document.getElementById('alerts').textContent = data.alerts;
  document.getElementById('investigations').textContent = data.investigations;
  document.getElementById('actions').textContent = data.actions;
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from Sentinel stream');
};
```

### Python

```python
import asyncio
import websockets
import json

async def stream_stats():
    uri = "ws://localhost:8000/stream"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Alerts: {data['alerts']}, "
                  f"Investigations: {data['investigations']}, "
                  f"Actions: {data['actions']}")

asyncio.run(stream_stats())
```

---

## Best Practices

1. **Pagination**: Always use pagination for large datasets
2. **Caching**: Cache responses when appropriate
3. **Error Handling**: Always handle potential errors
4. **WebSocket Reconnection**: Implement reconnection logic for WebSocket connections
5. **Monitoring**: Use the `/metrics` endpoint for monitoring

---

## Future Enhancements

Planned API improvements:

- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Filtering and search capabilities
- [ ] Bulk operations
- [ ] Webhook notifications
- [ ] GraphQL endpoint
- [ ] API versioning

---

For more information, see the [README](README.md) or visit the interactive documentation at http://localhost:8000/docs when the system is running.
