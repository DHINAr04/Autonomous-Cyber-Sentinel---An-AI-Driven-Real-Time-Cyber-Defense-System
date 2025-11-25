# 🔧 Troubleshooting Guide

Common issues and solutions for the Autonomous Cyber Sentinel.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Docker Issues](#docker-issues)
- [API Issues](#api-issues)
- [Performance Issues](#performance-issues)
- [Testing Issues](#testing-issues)

---

## Installation Issues

### Python Not Found

**Symptom**: `python: command not found` or `py: command not found`

**Solutions**:
1. Install Python 3.10+ from https://www.python.org
2. During installation, check "Add Python to PATH"
3. Restart PowerShell after installation
4. Try alternative commands:
   ```powershell
   python --version
   python3 --version
   py --version
   ```

### pip Install Fails

**Symptom**: `ERROR: Could not install packages`

**Solutions**:
1. Upgrade pip:
   ```powershell
   python -m pip install --upgrade pip
   ```

2. Install with verbose output:
   ```powershell
   pip install -r requirements.txt -v
   ```

3. Install system dependencies (for Scapy):
   - Windows: Install Npcap from https://npcap.com/
   - Ensure "WinPcap API-compatible Mode" is checked

### Virtual Environment Issues

**Symptom**: Cannot activate virtual environment

**Solutions**:
1. Enable script execution:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. Recreate virtual environment:
   ```powershell
   Remove-Item -Recurse -Force .venv
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

---

## Runtime Errors

### Module Not Found

**Symptom**: `ModuleNotFoundError: No module named 'sentinel'`

**Solutions**:
1. Ensure virtual environment is activated:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run from project root directory

### Redis Connection Error

**Symptom**: `redis.exceptions.ConnectionError`

**Solutions**:
1. Check if Redis is running:
   ```powershell
   docker ps | findstr redis
   ```

2. Start Redis:
   ```powershell
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. Or use in-memory mode:
   ```powershell
   # In .env file
   BUS=memory
   ```

### Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solutions**:
1. Stop all running instances
2. Delete database file:
   ```powershell
   Remove-Item sentinel.db
   Remove-Item data\*.db
   ```
3. Restart the system

### Import Errors

**Symptom**: `ImportError: cannot import name 'X'`

**Solutions**:
1. Check Python version (must be 3.10+):
   ```powershell
   python --version
   ```

2. Clear Python cache:
   ```powershell
   .\scripts\dev.ps1 clean
   ```

3. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

---

## Docker Issues

### Docker Not Running

**Symptom**: `error during connect: This error may indicate that the docker daemon is not running`

**Solutions**:
1. Start Docker Desktop
2. Wait for it to fully initialize (check system tray)
3. Verify:
   ```powershell
   docker ps
   ```

### Port Already in Use

**Symptom**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solutions**:
1. Find process using port:
   ```powershell
   netstat -ano | findstr :8000
   ```

2. Kill the process:
   ```powershell
   taskkill /PID <PID> /F
   ```

3. Or change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Use 8001 instead
   ```

### Container Build Fails

**Symptom**: `ERROR [internal] load metadata for docker.io/library/python`

**Solutions**:
1. Check internet connection
2. Clear Docker cache:
   ```powershell
   docker system prune -a
   ```

3. Rebuild without cache:
   ```powershell
   docker-compose build --no-cache
   ```

### Container Exits Immediately

**Symptom**: Container starts then stops

**Solutions**:
1. Check logs:
   ```powershell
   docker-compose logs sentinel
   ```

2. Run interactively:
   ```powershell
   docker-compose run sentinel /bin/sh
   ```

3. Check for missing files or configuration errors

---

## API Issues

### Cannot Connect to API

**Symptom**: `Connection refused` or `Failed to connect`

**Solutions**:
1. Verify server is running:
   ```powershell
   curl http://localhost:8000/health
   ```

2. Check if port is correct (default: 8000)

3. Check firewall settings

4. Try localhost alternatives:
   - http://localhost:8000
   - http://127.0.0.1:8000
   - http://0.0.0.0:8000

### 500 Internal Server Error

**Symptom**: API returns 500 error

**Solutions**:
1. Check server logs:
   ```powershell
   # Local mode
   # Logs appear in console
   
   # Docker mode
   docker-compose logs sentinel
   ```

2. Check database permissions

3. Verify configuration in `.env` and `settings.yml`

### WebSocket Connection Fails

**Symptom**: WebSocket connection error in browser

**Solutions**:
1. Check if server supports WebSockets
2. Verify URL format: `ws://localhost:8000/stream`
3. Check browser console for errors
4. Try different browser

### No Data Returned

**Symptom**: API returns empty arrays

**Solutions**:
1. Wait a few seconds for data generation
2. Check if detection engine is running:
   ```powershell
   curl http://localhost:8000/health
   ```

3. Verify system is generating synthetic data:
   ```powershell
   curl http://localhost:8000/stats
   ```

---

## Performance Issues

### High CPU Usage

**Symptom**: System using excessive CPU

**Solutions**:
1. Reduce packet capture rate (if using live capture)
2. Increase micro-batch size in `batcher.py`
3. Disable live capture:
   ```env
   LIVE_CAPTURE=0
   ```

### High Memory Usage

**Symptom**: System using excessive memory

**Solutions**:
1. Limit alert history:
   ```python
   # In state.py, add max size
   if len(self.alerts) > 1000:
       self.alerts = self.alerts[-1000:]
   ```

2. Enable Redis for caching (offload memory)

3. Restart periodically

### Slow Response Times

**Symptom**: API responses are slow

**Solutions**:
1. Enable Redis caching:
   ```env
   BUS=redis
   ```

2. Use pagination:
   ```
   /alerts?limit=10
   ```

3. Check database size:
   ```powershell
   Get-Item sentinel.db
   ```

4. Optimize queries or reset database

### Database Growing Too Large

**Symptom**: Database file is very large

**Solutions**:
1. Archive old data:
   ```powershell
   # Backup
   Copy-Item sentinel.db sentinel.db.backup
   
   # Delete
   Remove-Item sentinel.db
   ```

2. Implement data retention policy

3. Use external database (PostgreSQL)

---

## Testing Issues

### Tests Failing

**Symptom**: `pytest` shows failures

**Solutions**:
1. Run with verbose output:
   ```powershell
   pytest tests/ -v
   ```

2. Run specific test:
   ```powershell
   pytest tests/test_config.py -v
   ```

3. Check for missing dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Import Errors in Tests

**Symptom**: `ModuleNotFoundError` during tests

**Solutions**:
1. Ensure running from project root
2. Install package in development mode:
   ```powershell
   pip install -e .
   ```

3. Add project to PYTHONPATH:
   ```powershell
   $env:PYTHONPATH = "."
   pytest tests/
   ```

### Async Test Failures

**Symptom**: `RuntimeError: Event loop is closed`

**Solutions**:
1. Install pytest-asyncio:
   ```powershell
   pip install pytest-asyncio
   ```

2. Mark async tests:
   ```python
   @pytest.mark.asyncio
   async def test_something():
       pass
   ```

---

## Common Error Messages

### "Address already in use"

**Cause**: Port 8000 is occupied

**Fix**: Kill process or change port

### "Permission denied"

**Cause**: Insufficient permissions

**Fix**: Run as administrator or check file permissions

### "No such file or directory"

**Cause**: Missing file or wrong directory

**Fix**: Ensure running from project root

### "Connection refused"

**Cause**: Service not running

**Fix**: Start the service

### "Timeout"

**Cause**: Service taking too long to respond

**Fix**: Check service health, increase timeout

---

## Diagnostic Commands

### Check System Status

```powershell
# Check Python
python --version

# Check Docker
docker --version
docker ps

# Check Redis
docker exec -it sentinel-redis redis-cli ping

# Check API
curl http://localhost:8000/health

# Check logs
.\scripts\dev.ps1 logs
```

### Collect Debug Information

```powershell
# System info
python --version
docker --version

# Service status
docker-compose ps

# Logs
docker-compose logs > debug-logs.txt

# Configuration
Get-Content .env
Get-Content settings.yml

# Database
Get-Item sentinel.db
```

---

## Getting Help

If you're still experiencing issues:

1. **Check logs** for error messages
2. **Search** existing issues on GitHub
3. **Create** a new issue with:
   - Error message
   - Steps to reproduce
   - System information
   - Logs

### Useful Log Locations

- **Local mode**: Console output
- **Docker mode**: `docker-compose logs sentinel`
- **Test logs**: `pytest tests/ -v`

---

## Reset Everything

If all else fails, complete reset:

```powershell
# Stop all services
.\scripts\dev.ps1 down

# Clean everything
.\scripts\dev.ps1 clean

# Remove virtual environment
Remove-Item -Recurse -Force .venv

# Remove Docker volumes
docker-compose down -v

# Start fresh
.\scripts\setup.ps1
.\quickstart.ps1
```

---

## Prevention Tips

1. **Always activate virtual environment** before running commands
2. **Keep dependencies updated**: `pip install -r requirements.txt --upgrade`
3. **Regular cleanup**: `.\scripts\dev.ps1 clean`
4. **Monitor logs** for warnings
5. **Use version control** to track changes

---

For more help, see:
- [Getting Started Guide](GETTING_STARTED.md)
- [README](README.md)
- [API Documentation](API.md)
