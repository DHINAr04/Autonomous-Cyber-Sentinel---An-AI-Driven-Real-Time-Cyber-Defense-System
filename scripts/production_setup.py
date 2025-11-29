"""Automated production setup script."""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header."""
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  {text}")
    logger.info("=" * 70)
    logger.info("")


def check_python_version():
    """Check Python version."""
    logger.info("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        logger.info(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"  ✗ Python 3.10+ required, found {version.major}.{version.minor}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    logger.info("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        logger.info("  ✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  ✗ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    logger.info("Creating directories...")
    directories = ['models', 'logs', 'data', 'reports', 'reports/charts']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"  ✓ {directory}/")
    
    return True


def train_models():
    """Train all ML models."""
    logger.info("Training ML models (this may take a few minutes)...")
    try:
        subprocess.run([sys.executable, 'scripts/train_models.py'], check=True)
        logger.info("  ✓ Models trained successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  ✗ Model training failed: {e}")
        return False


def setup_configuration():
    """Set up configuration files."""
    logger.info("Setting up configuration...")
    
    # Check if .env exists
    if os.path.exists('.env'):
        logger.info("  ✓ .env already exists")
    elif os.path.exists('.env.production'):
        logger.info("  Copying .env.production to .env...")
        with open('.env.production', 'r') as src:
            with open('.env', 'w') as dst:
                dst.write(src.read())
        logger.info("  ✓ .env created from .env.production")
    elif os.path.exists('.env.example'):
        logger.info("  Copying .env.example to .env...")
        with open('.env.example', 'r') as src:
            with open('.env', 'w') as dst:
                dst.write(src.read())
        logger.info("  ✓ .env created from .env.example")
    else:
        logger.warning("  ⚠ No .env file found, creating minimal config...")
        with open('.env', 'w') as f:
            f.write("ENABLE_PRODUCTION_ACTIONS=false\n")
            f.write("LIVE_CAPTURE=false\n")
            f.write("IP_WHITELIST=127.0.0.1,localhost\n")
        logger.info("  ✓ Minimal .env created")
    
    return True


def verify_installation():
    """Verify installation."""
    logger.info("Verifying installation...")
    
    checks = {
        'Models directory': os.path.exists('models'),
        'Random Forest model': os.path.exists('models/random_forest.joblib'),
        'SVM model': os.path.exists('models/svm.joblib'),
        'Scaler': os.path.exists('models/scaler.joblib'),
        'RL Q-table': os.path.exists('models/rl_q_table.json'),
        '.env file': os.path.exists('.env'),
        'Logs directory': os.path.exists('logs'),
    }
    
    all_passed = True
    for check, passed in checks.items():
        if passed:
            logger.info(f"  ✓ {check}")
        else:
            logger.warning(f"  ⚠ {check} (optional)")
            if check in ['Random Forest model', 'SVM model', 'Scaler']:
                all_passed = False
    
    return all_passed


def print_next_steps():
    """Print next steps."""
    print_header("SETUP COMPLETE!")
    
    logger.info("Your Autonomous Cyber Sentinel is now 100% production-ready!")
    logger.info("")
    logger.info("📋 NEXT STEPS:")
    logger.info("")
    logger.info("1. Configure your environment:")
    logger.info("   Edit .env file:")
    logger.info("     - Set CAPTURE_INTERFACE to your network interface")
    logger.info("     - Update IP_WHITELIST with your management IPs")
    logger.info("     - Add API keys for threat intelligence (optional)")
    logger.info("")
    logger.info("2. Test in simulation mode:")
    logger.info("   python sentinel/run.py")
    logger.info("")
    logger.info("3. Enable production mode (when ready):")
    logger.info("   Edit .env: ENABLE_PRODUCTION_ACTIONS=true")
    logger.info("   Run with sudo: sudo -E python sentinel/run.py")
    logger.info("")
    logger.info("4. Access dashboard:")
    logger.info("   http://localhost:8000")
    logger.info("")
    logger.info("📚 DOCUMENTATION:")
    logger.info("   - PRODUCTION_DEPLOYMENT.md - Full deployment guide")
    logger.info("   - GETTING_STARTED.md - Quick start guide")
    logger.info("   - TROUBLESHOOTING.md - Common issues")
    logger.info("")
    logger.info("⚠️  IMPORTANT SAFETY NOTES:")
    logger.info("   - Always test in simulation mode first")
    logger.info("   - Configure IP whitelist before enabling production mode")
    logger.info("   - Run with sudo for packet capture")
    logger.info("   - Monitor logs during initial deployment")
    logger.info("")
    logger.info("✅ System Status: PRODUCTION READY")
    logger.info("")


def main():
    """Main setup function."""
    print_header("AUTONOMOUS CYBER SENTINEL - PRODUCTION SETUP")
    
    logger.info("This script will:")
    logger.info("  1. Check Python version")
    logger.info("  2. Install dependencies")
    logger.info("  3. Create directories")
    logger.info("  4. Train ML models")
    logger.info("  5. Set up configuration")
    logger.info("  6. Verify installation")
    logger.info("")
    
    input("Press Enter to continue...")
    
    # Run setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Training models", train_models),
        ("Setting up configuration", setup_configuration),
        ("Verifying installation", verify_installation),
    ]
    
    for step_name, step_func in steps:
        print_header(step_name)
        if not step_func():
            logger.error(f"Setup failed at: {step_name}")
            logger.error("Please fix the errors and run again.")
            sys.exit(1)
    
    # Print next steps
    print_next_steps()


if __name__ == '__main__':
    main()
