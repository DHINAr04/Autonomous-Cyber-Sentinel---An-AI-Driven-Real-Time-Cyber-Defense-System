# GitHub Push Script for Autonomous Cyber Sentinel
# This script will initialize git, add all files, and push to GitHub

param(
    [Parameter(Mandatory=$false)]
    [string]$RepoUrl = "",
    [Parameter(Mandatory=$false)]
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🚀 GitHub Push Script - Autonomous Cyber Sentinel" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Check if git is installed
Write-Host "Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "  ✓ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git not installed!" -ForegroundColor Red
    Write-Host "  Install from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Cyan

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host ""
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "  ✓ Git initialized" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Git repository already initialized" -ForegroundColor Green
}

# Configure git user if not set
Write-Host ""
Write-Host "Checking Git configuration..." -ForegroundColor Yellow
$userName = git config user.name 2>$null
$userEmail = git config user.email 2>$null

if (-not $userName) {
    Write-Host "  Git user.name not set" -ForegroundColor Yellow
    $name = Read-Host "  Enter your name"
    git config user.name "$name"
    Write-Host "  ✓ User name set" -ForegroundColor Green
}

if (-not $userEmail) {
    Write-Host "  Git user.email not set" -ForegroundColor Yellow
    $email = Read-Host "  Enter your email"
    git config user.email "$email"
    Write-Host "  ✓ User email set" -ForegroundColor Green
}

# Get repository URL if not provided
if (-not $RepoUrl) {
    Write-Host ""
    Write-Host "GitHub Repository Setup" -ForegroundColor Cyan
    Write-Host "Please create a repository on GitHub first:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://github.com/new" -ForegroundColor White
    Write-Host "  2. Create a new repository (e.g., 'autonomous-cyber-sentinel')" -ForegroundColor White
    Write-Host "  3. Copy the repository URL" -ForegroundColor White
    Write-Host ""
    $RepoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git)"
}

# Add all files
Write-Host ""
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "  ✓ Files added" -ForegroundColor Green

# Show status
Write-Host ""
Write-Host "Git Status:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Autonomous Cyber Sentinel - Enterprise Edition

Features:
- Real-time threat detection with ML
- 6 threat intelligence sources
- Autonomous response system
- Automated PDF report generation
- Modern enterprise UI with dark mode
- Interactive real-time charts
- Complete documentation
- Production-ready deployment"

git commit -m "$commitMessage"
Write-Host "  ✓ Commit created" -ForegroundColor Green

# Set branch name
Write-Host ""
Write-Host "Setting branch to '$Branch'..." -ForegroundColor Yellow
git branch -M $Branch
Write-Host "  ✓ Branch set" -ForegroundColor Green

# Add remote
Write-Host ""
Write-Host "Adding remote repository..." -ForegroundColor Yellow
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "  Remote 'origin' already exists, updating..." -ForegroundColor Yellow
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}
Write-Host "  ✓ Remote added: $RepoUrl" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin $Branch
    Write-Host ""
    Write-Host "=" * 60
    Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "=" * 60
    Write-Host ""
    Write-Host "Your repository is now available at:" -ForegroundColor Cyan
    $repoWebUrl = $RepoUrl -replace '\.git$', ''
    Write-Host "  $repoWebUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Visit your repository on GitHub" -ForegroundColor White
    Write-Host "  2. Add a description and topics" -ForegroundColor White
    Write-Host "  3. Enable GitHub Pages (optional)" -ForegroundColor White
    Write-Host "  4. Share with others!" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "✗ Push failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Repository doesn't exist - Create it on GitHub first" -ForegroundColor White
    Write-Host "  2. Authentication failed - Set up GitHub credentials" -ForegroundColor White
    Write-Host "  3. Permission denied - Check repository access" -ForegroundColor White
    Write-Host ""
    Write-Host "For authentication, you may need to:" -ForegroundColor Yellow
    Write-Host "  - Use a Personal Access Token instead of password" -ForegroundColor White
    Write-Host "  - Set up SSH keys" -ForegroundColor White
    Write-Host "  - Use GitHub CLI (gh auth login)" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Show final stats
Write-Host "Repository Statistics:" -ForegroundColor Cyan
$fileCount = (git ls-files | Measure-Object).Count
$commitCount = (git rev-list --count HEAD)
Write-Host "  Files: $fileCount" -ForegroundColor White
Write-Host "  Commits: $commitCount" -ForegroundColor White
Write-Host ""
