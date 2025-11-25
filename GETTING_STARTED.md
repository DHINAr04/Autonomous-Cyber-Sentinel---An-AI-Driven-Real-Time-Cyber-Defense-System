# 🚀 Getting Started with Autonomous Cyber Sentinel

This guide will help you set up and run the Autonomous Cyber Sentinel system on your Windows machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Requires Windows 10/11 Pro, Enterprise, or Education
   - Enable WSL 2 backend during installation
   - Verify: `docker --version`

3. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/downloads
   - Verify: `git --version`

### Optional (for full functionality)

- **API Keys** (free tier available):
  - VirusTotal: https://www.virustotal.com/gui/join-us
  - AbuseIPDB: https://www.abuseipdb.com/register
  - AlienVault OTX: https://otx.alienvault.com/

## 🛠️ Installation

### Step 1: Get the Code

**Option A: Clone with Git**
```powershell
git clone https://github.com/yourusername/sentinel.git
cd sentinel
```

**Option B: Download ZIP**
1. Download the repository as ZIP
2. Extract to a folder
3. Open PowerShell in that folder

### Step 2: Run Setup

```powershell
.\scripts\setup.ps1
```

This script will:
- ✅ Check Python and Docker installations
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Set up data directories

### Step 3: Configure (Optional)

Edit the `.env` file to add your API keys:

```powershell
notepad .env
```

Add your keys:
```env
VT_API_KEY=your_virustotal_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_key_here
OTX_API_KEY=your_otx_key_here
```

**Note**: The system works without API keys using mocked data for testing.

## 🎮 Running the System

### Option 1: Development Mode (Recommended for Testing)

Run the system locally without Docker:

```powershell
.\scripts\dev.ps1 run
```

This starts the system on **http://localhost:8000**

Open your browser and visit:
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

Press `Ctrl+C` to stop.

### Option 2: Full Docker Stack (Production-like)

Run the complete system with all services:

```powershell
.\scripts\dev.ps1 up
```

This starts:
- 🛡️ Sentinel Dashboard
- 📦 Redis (event bus)
- 🌐 Simulated network services
- 🍯 Honeypot
- 🚦 Traffic generator

Access the dashboard at **http://localhost:8000**

To stop:
```powershell
.\scripts\dev.ps1 down
```

## 📊 Verifying the System

### 1. Check System Health

```powershell
curl http://localhost:8000/health
```

Expected response:
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

### 2. Monitor Live Activity

Open the dashboard at http://localhost:8000 and watch:
- Alerts being detected
- Investigations being performed
- Actions being taken

The numbers should increase every few seconds.

### 3. Generate Test Traffic

In a new PowerShell window:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run traffic generator
python scripts/generate_traffic.py --mode monitor --duration 30
```

## 🧪 Running Tests

### Quick Tests
```powershell
.\scripts\dev.ps1 test-quick
```

### Full Test Suite
```powershell
.\scripts\dev.ps1 test
```

### Code Quality
```powershell
# Linting
.\scripts\dev.ps1 lint

# Security scan
.\scripts\dev.ps1 security
```

## 🎓 Training a Custom Model

To train your own threat detection model:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Train model
python scripts/train_model.py
```

This creates `models/threat_detector.joblib`. To use it:

1. Edit `.env`:
   ```env
   MODEL_PATH=models/threat_detector.joblib
   ```

2. Restart the system

## 📖 Understanding the Dashboard

### Home Page
- **Alerts Detected**: Total threats identified
- **Investigations**: Threat intelligence lookups performed
- **Actions Taken**: Autonomous responses executed

### Alerts Page
View all detected threats with:
- Severity (low/medium/high)
- Source/destination IPs
- Model confidence scores
- Timestamps

### Investigations Page
See threat intelligence findings:
- VirusTotal reputation scores
- AbuseIPDB abuse confidence
- AlienVault OTX pulse counts
- Risk scores and verdicts

### Actions Page
Monitor autonomous responses:
- Action types (isolate, block, redirect, etc.)
- Targets (containers, IPs)
- Results and safety gates
- Reversibility status

## 🔧 Troubleshooting

### "Python not found"
- Ensure Python is installed and in PATH
- Restart PowerShell after installation
- Try: `python3 --version` or `py --version`

### "Docker not running"
- Start Docker Desktop
- Wait for it to fully initialize
- Check system tray icon

### "Port 8000 already in use"
- Stop other services using port 8000
- Or change port in `docker-compose.yml`

### "Module not found" errors
- Ensure virtual environment is activated
- Run: `.\scripts\dev.ps1 install`

### No alerts appearing
- System generates synthetic alerts automatically
- Wait 5-10 seconds after startup
- Check logs: `.\scripts\dev.ps1 logs`

## 🎯 Next Steps

### For Development
1. Read the [Architecture Documentation](README.md#-architecture)
2. Explore the [API Documentation](http://localhost:8000/docs)
3. Review the [Project Blueprint](project_blueprint.md)

### For Testing
1. Run the traffic generator with different scenarios
2. Modify `settings.yml` to adjust thresholds
3. Create custom decision matrices

### For Production
1. Add real API keys to `.env`
2. Configure network capture: `LIVE_CAPTURE=1`
3. Set up Prometheus monitoring
4. Review security settings

## 📚 Additional Resources

- **README.md**: Full project documentation
- **project_blueprint.md**: Comprehensive technical details
- **API Docs**: http://localhost:8000/docs (when running)
- **Tests**: See `tests/` directory for examples

## 🆘 Getting Help

If you encounter issues:

1. Check the logs:
   ```powershell
   .\scripts\dev.ps1 logs
   ```

2. Clean and restart:
   ```powershell
   .\scripts\dev.ps1 clean
   .\scripts\dev.ps1 run
   ```

3. Review test output:
   ```powershell
   .\scripts\dev.ps1 test -v
   ```

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Docker Desktop running
- [ ] Setup script completed successfully
- [ ] System starts without errors
- [ ] Dashboard accessible at http://localhost:8000
- [ ] Alerts appearing on dashboard
- [ ] Tests passing
- [ ] Traffic generator working

Congratulations! You're now running the Autonomous Cyber Sentinel! 🎉

---

**Need more help?** Check the [README](README.md) or review the [Project Blueprint](project_blueprint.md).
