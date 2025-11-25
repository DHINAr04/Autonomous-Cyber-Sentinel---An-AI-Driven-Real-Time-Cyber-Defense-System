# Verification script to check if the project is properly set up

Write-Host ""
Write-Host "🛡️  Autonomous Cyber Sentinel - System Verification" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

$allGood = $true

# Check Python
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "3\.1[0-9]" -or $pythonVersion -match "3\.[2-9][0-9]") {
        Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Python: $pythonVersion (3.10+ recommended)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    $allGood = $false
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Docker not found (optional for local dev)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📁 Checking Project Structure..." -ForegroundColor Yellow
Write-Host ""

# Check directories
$requiredDirs = @(
    "sentinel",
    "sentinel/common",
    "sentinel/detection",
    "sentinel/investigation",
    "sentinel/response",
    "sentinel/dashboard",
    "tests",
    "scripts",
    "data",
    "models"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir/" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir/ missing" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "📄 Checking Core Files..." -ForegroundColor Yellow
Write-Host ""

# Check core files
$requiredFiles = @(
    "sentinel/common/config.py",
    "sentinel/common/event_bus.py",
    "sentinel/common/persistence.py",
    "sentinel/detection/engine.py",
    "sentinel/investigation/agent.py",
    "sentinel/response/engine.py",
    "sentinel/dashboard/app.py",
    "requirements.txt",
    "docker-compose.yml",
    "Dockerfile",
    ".env.example",
    "settings.yml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "📚 Checking Documentation..." -ForegroundColor Yellow
Write-Host ""

$docFiles = @(
    "README.md",
    "GETTING_STARTED.md",
    "API.md",
    "PROJECT_STATUS.md",
    "TROUBLESHOOTING.md",
    "BUILD_COMPLETE.md",
    "LICENSE"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file missing" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🧪 Checking Test Files..." -ForegroundColor Yellow
Write-Host ""

$testFiles = @(
    "tests/test_config.py",
    "tests/test_features.py",
    "tests/test_model.py",
    "tests/test_integration.py",
    "tests/test_end_to_end.py"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file missing" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🔧 Checking Configuration..." -ForegroundColor Yellow
Write-Host ""

# Check .env
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ .env file not found (will be created on first run)" -ForegroundColor Yellow
}

# Check virtual environment
if (Test-Path ".venv") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
    
    # Check if dependencies are installed
    if (Test-Path ".venv/Lib/site-packages/fastapi") {
        Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Dependencies not installed" -ForegroundColor Yellow
        Write-Host "    Run: .\scripts\dev.ps1 install" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠ Virtual environment not found" -ForegroundColor Yellow
    Write-Host "    Run: .\scripts\setup.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚀 Checking Scripts..." -ForegroundColor Yellow
Write-Host ""

$scriptFiles = @(
    "scripts/setup.ps1",
    "scripts/dev.ps1",
    "scripts/train_model.py",
    "scripts/generate_traffic.py",
    "quickstart.ps1"
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "=" * 60
Write-Host ""

if ($allGood) {
    Write-Host "✅ All critical components verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Your system is ready to run!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run setup (if not done): .\scripts\setup.ps1"
    Write-Host "  2. Start the system: .\quickstart.ps1"
    Write-Host "  3. Open browser: http://localhost:8000"
    Write-Host ""
} else {
    Write-Host "⚠️  Some components are missing" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please ensure all files are present." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📖 For help, see:" -ForegroundColor Cyan
Write-Host "  - GETTING_STARTED.md"
Write-Host "  - TROUBLESHOOTING.md"
Write-Host "  - BUILD_COMPLETE.md"
Write-Host ""
