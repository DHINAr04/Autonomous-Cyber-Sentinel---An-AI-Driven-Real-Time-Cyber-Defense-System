FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for Scapy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY sentinel /app/sentinel
COPY settings.yml /app/settings.yml

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

CMD ["python", "-m", "uvicorn", "sentinel.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]