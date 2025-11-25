# Quick Start Script for Autonomous Cyber Sentinel
# This script sets up and runs the system in one command

param(
    [switch]$Docker,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host ""
    Write-Host "🛡️  Autonomous Cyber Sentinel - Quick Start" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\quickstart.ps1          # Run locally (development mode)"
    Write-Host "  .\quickstart.ps1 -Docker  # Run with Docker Compose"
    Write-Host "  .\quickstart.ps1 -Help    # Show this help"
    Write-Host ""
    exit 0
}

if ($Help) {
    Show-Help
}

Write-Host ""
Write-Host "🛡️  Autonomous Cyber Sentinel - Quick Start" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host "    Please install Python 3.10+ from https://www.python.org" -ForegroundColor Yellow
    exit 1
}

if ($Docker) {
    # Check Docker
    try {
        $dockerVersion = docker --version 2>&1
        Write-Host "  ✓ Docker: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Docker not found!" -ForegroundColor Red
        Write-Host "    Please install Docker Desktop from https://www.docker.com" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Run setup if needed
if (-not (Test-Path ".venv") -or -not (Test-Path ".env")) {
    Write-Host "🔧 Running initial setup..." -ForegroundColor Yellow
    & .\scripts\setup.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Setup failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Start the system
if ($Docker) {
    Write-Host "🐳 Starting Docker Compose stack..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Services starting:" -ForegroundColor Cyan
    Write-Host "  • Sentinel Dashboard (http://localhost:8000)"
    Write-Host "  • Redis (event bus)"
    Write-Host "  • Simulated network services"
    Write-Host "  • Traffic generator"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
    Write-Host ""
    
    docker-compose up --build
    
} else {
    Write-Host "🚀 Starting development server..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Dashboard: http://localhost:8000" -ForegroundColor Green
    Write-Host "API Docs:  http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "Metrics:   http://localhost:8000/metrics" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    # Activate venv and run
    & .\.venv\Scripts\Activate.ps1
    python -m uvicorn sentinel.dashboard.app:app --reload --host 0.0.0.0 --port 8000
}
