# Deployment Script for Autonomous Cyber Sentinel
# Supports: Local, Docker, Production

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('local', 'docker', 'production', 'help')]
    [string]$Mode = 'local'
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host ""
    Write-Host "🚀 Autonomous Cyber Sentinel - Deployment Script" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 -Mode <mode>" -ForegroundColor White
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Yellow
    Write-Host "  local       - Start local development server" -ForegroundColor White
    Write-Host "  docker      - Deploy using Docker Compose" -ForegroundColor White
    Write-Host "  production  - Production deployment checklist" -ForegroundColor White
    Write-Host "  help        - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 -Mode local" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Mode docker" -ForegroundColor White
    Write-Host ""
    exit 0
}

function Deploy-Local {
    Write-Host ""
    Write-Host "🏠 Starting Local Development Server" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    
    # Check Python
    Write-Host "Checking Python..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Python not found!" -ForegroundColor Red
        exit 1
    }
    
    # Check virtual environment
    Write-Host "Checking virtual environment..." -ForegroundColor Yellow
    if (Test-Path ".venv") {
        Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Virtual environment not found!" -ForegroundColor Red
        Write-Host "  Run: .\scripts\setup.ps1" -ForegroundColor Yellow
        exit 1
    }
    
    # Check .env
    Write-Host "Checking configuration..." -ForegroundColor Yellow
    if (Test-Path ".env") {
        Write-Host "  ✓ .env file exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Creating .env from example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "  ✓ .env created" -ForegroundColor Green
    }
    
    # Create directories
    Write-Host "Creating directories..." -ForegroundColor Yellow
    @("reports", "reports\charts", "data") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ | Out-Null
        }
    }
    Write-Host "  ✓ Directories ready" -ForegroundColor Green
    
    # Start server
    Write-Host ""
    Write-Host "🚀 Starting server..." -ForegroundColor Green
    Write-Host ""
    Write-Host "Dashboard will be available at:" -ForegroundColor Cyan
    Write-Host "  http://localhost:8001" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    & .\.venv\Scripts\python.exe -m uvicorn sentinel.dashboard.app:app --host 0.0.0.0 --port 8001 --reload
}

function Deploy-Docker {
    Write-Host ""
    Write-Host "🐳 Docker Deployment" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    
    # Check Docker
    Write-Host "Checking Docker..." -ForegroundColor Yellow
    try {
        $dockerVersion = docker --version 2>&1
        Write-Host "  ✓ $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker not found!" -ForegroundColor Red
        Write-Host "  Install from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
        exit 1
    }
    
    # Check docker-compose
    Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
    try {
        $composeVersion = docker-compose --version 2>&1
        Write-Host "  ✓ $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker Compose not found!" -ForegroundColor Red
        exit 1
    }
    
    # Create .env if needed
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "  ✓ .env created" -ForegroundColor Green
    }
    
    # Build and start
    Write-Host ""
    Write-Host "Building and starting containers..." -ForegroundColor Yellow
    docker-compose up --build -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Services:" -ForegroundColor Cyan
        Write-Host "  Dashboard: http://localhost:8000" -ForegroundColor White
        Write-Host "  Redis: localhost:6379" -ForegroundColor White
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  View logs:  docker-compose logs -f sentinel" -ForegroundColor White
        Write-Host "  Stop:       docker-compose down" -ForegroundColor White
        Write-Host "  Restart:    docker-compose restart" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "✗ Deployment failed!" -ForegroundColor Red
        Write-Host "Check logs: docker-compose logs" -ForegroundColor Yellow
        exit 1
    }
}

function Deploy-Production {
    Write-Host ""
    Write-Host "🏭 Production Deployment Checklist" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    
    Write-Host "Pre-Deployment Checklist:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [ ] Server provisioned (2+ CPU, 4GB+ RAM)" -ForegroundColor White
    Write-Host "  [ ] Domain name configured" -ForegroundColor White
    Write-Host "  [ ] SSL certificate obtained" -ForegroundColor White
    Write-Host "  [ ] Firewall configured (ports 80, 443)" -ForegroundColor White
    Write-Host "  [ ] Database setup (PostgreSQL recommended)" -ForegroundColor White
    Write-Host "  [ ] Redis installed and running" -ForegroundColor White
    Write-Host "  [ ] Nginx installed and configured" -ForegroundColor White
    Write-Host "  [ ] Environment variables configured" -ForegroundColor White
    Write-Host "  [ ] API keys added (optional)" -ForegroundColor White
    Write-Host "  [ ] Backup strategy in place" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Deployment Steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Upload project to server" -ForegroundColor White
    Write-Host "  2. Install dependencies" -ForegroundColor White
    Write-Host "  3. Configure environment" -ForegroundColor White
    Write-Host "  4. Setup systemd service" -ForegroundColor White
    Write-Host "  5. Configure Nginx reverse proxy" -ForegroundColor White
    Write-Host "  6. Setup SSL with Let's Encrypt" -ForegroundColor White
    Write-Host "  7. Start services" -ForegroundColor White
    Write-Host "  8. Verify deployment" -ForegroundColor White
    Write-Host "  9. Setup monitoring" -ForegroundColor White
    Write-Host "  10. Configure backups" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Documentation:" -ForegroundColor Yellow
    Write-Host "  See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Quick Commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  # On server (Linux):" -ForegroundColor Cyan
    Write-Host "  git clone <repo-url>" -ForegroundColor White
    Write-Host "  cd sentinel" -ForegroundColor White
    Write-Host "  python3 -m venv .venv" -ForegroundColor White
    Write-Host "  source .venv/bin/activate" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  cp .env.example .env" -ForegroundColor White
    Write-Host "  # Edit .env with production settings" -ForegroundColor White
    Write-Host "  sudo systemctl start sentinel" -ForegroundColor White
    Write-Host ""
}

# Main execution
switch ($Mode) {
    'help' { Show-Help }
    'local' { Deploy-Local }
    'docker' { Deploy-Docker }
    'production' { Deploy-Production }
    default { Show-Help }
}
