param([string]$cmd='help')

Write-Host "🛡️  Autonomous Cyber Sentinel - Dev Tools" -ForegroundColor Cyan
Write-Host ""

switch ($cmd) {
  'install' { 
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "✓ Installation complete" -ForegroundColor Green
  }
  'run' { 
    Write-Host "Starting development server on http://localhost:8000" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    python -m uvicorn sentinel.dashboard.app:app --reload --host 0.0.0.0 --port 8000
  }
  'test' { 
    Write-Host "Running tests..." -ForegroundColor Yellow
    python -m pytest tests/ -v
  }
  'test-quick' {
    Write-Host "Running quick tests..." -ForegroundColor Yellow
    python -m pytest tests/ -q --ignore=tests/test_end_to_end.py
  }
  'lint' {
    Write-Host "Running linters..." -ForegroundColor Yellow
    flake8 sentinel --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 sentinel --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
  }
  'security' {
    Write-Host "Running security scan..." -ForegroundColor Yellow
    bandit -r sentinel -ll
  }
  'up' { 
    Write-Host "Starting Docker Compose stack..." -ForegroundColor Yellow
    docker-compose up --build
  }
  'down' { 
    Write-Host "Stopping Docker Compose stack..." -ForegroundColor Yellow
    docker-compose down -v
  }
  'logs' {
    Write-Host "Showing Docker logs..." -ForegroundColor Yellow
    docker-compose logs -f sentinel
  }
  'clean' {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue sentinel.db
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue data/*.db
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue sentinel/**/__pycache__
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue tests/__pycache__
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache
    Write-Host "✓ Cleanup complete" -ForegroundColor Green
  }
  default { 
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  install      - Install Python dependencies"
    Write-Host "  run          - Start development server"
    Write-Host "  test         - Run all tests"
    Write-Host "  test-quick   - Run quick tests (skip E2E)"
    Write-Host "  lint         - Run code linters"
    Write-Host "  security     - Run security scan"
    Write-Host "  up           - Start Docker Compose"
    Write-Host "  down         - Stop Docker Compose"
    Write-Host "  logs         - Show Docker logs"
    Write-Host "  clean        - Clean up generated files"
    Write-Host ""
    Write-Host "Usage: .\scripts\dev.ps1 <command>" -ForegroundColor Yellow
  }
}