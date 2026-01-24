---
Type: Guide
Audience: Developers
Status: Draft
Importance: High
Created: 2026-01-24
Last Updated: 2026-01-24
Related Tasks: TASK-CI-V3
---

# FastAPI Deployment Guide

This guide covers deploying the structural_engineering_lib FastAPI application to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Configuration](#production-configuration)
5. [Environment Variables](#environment-variables)
6. [Health Monitoring](#health-monitoring)
7. [Security Hardening](#security-hardening)
8. [Scaling Considerations](#scaling-considerations)

## Prerequisites

- Python 3.11 or 3.12
- Docker (for containerized deployment)
- Access to the structural_lib Python package

## Local Development

### Quick Start

```bash
# Install dependencies
cd /path/to/structural_engineering_lib
pip install -e "Python/[dev]"
pip install -r requirements.txt

# Run development server
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Development with Hot Reload

```bash
# With debug logging
LOG_LEVEL=debug uvicorn fastapi_app.main:app --reload --log-level debug

# With specific host/port
uvicorn fastapi_app.main:app --reload --host 127.0.0.1 --port 8080
```

### Running Tests

```bash
# All FastAPI tests
pytest fastapi_app/tests/ -v

# Security tests only
pytest fastapi_app/tests/test_security.py -v

# With coverage
pytest fastapi_app/tests/ --cov=fastapi_app --cov-report=html
```

## Docker Deployment

### Dockerfile

Create `Dockerfile.fastapi` in project root:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install structural_lib package (located under Python/)
COPY Python/pyproject.toml Python/setup.cfg Python/README.md ./Python/
COPY Python/structural_lib ./Python/structural_lib
RUN pip install --no-cache-dir ./Python

# Copy FastAPI app
COPY fastapi_app ./fastapi_app

EXPOSE 8000
CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-change-me-in-production}
      - RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
      - RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-60}
```

### Building and Running

```bash
# Build image
docker build -f Dockerfile.fastapi -t structeng-api:latest .

# Run container
docker run -d -p 8000:8000 \
  -e JWT_SECRET_KEY="$(openssl rand -hex 32)" \
  --name structeng-api \
  structeng-api:latest

# Using docker compose
docker compose up -d

# View logs
docker compose logs -f fastapi
```

## Production Configuration

### Production Notes

- For higher throughput, consider a Gunicorn + Uvicorn worker setup, but add `gunicorn` to `requirements.txt` first.
- CORS origins are currently set in `fastapi_app/main.py`; update that list or wire in env-based settings if needed.
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "structeng-api"

# Preload app for memory efficiency
preload_app = True

def on_starting(server):
    """Called before master process starts."""
    pass

def on_exit(server):
    """Called before master process exits."""
    pass
```

### Nginx Reverse Proxy

Example nginx configuration:

```nginx
upstream fastapi {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.yoursite.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yoursite.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 8k;
    }

    # WebSocket endpoints
    location /ws/ {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Health check endpoint (no rate limit)
    location /health {
        proxy_pass http://fastapi;
        limit_req off;
    }
}
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT signing key (32+ chars) | `dev-secret-key-change-in-prod` | **Yes (prod)** |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` | **Yes (prod)** |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` | No |
| `RATE_LIMIT_REQUESTS` | Requests per window | `100` | No |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60` | No |
| `JWT_EXPIRY_HOURS` | JWT token expiry | `24` | No |
| `REDIS_URL` | Redis URL for rate limiting | None (in-memory) | No |

### Example .env file

```bash
# .env (DO NOT COMMIT TO GIT)
SECRET_KEY=your-256-bit-secret-key-here-minimum-32-characters
ALLOWED_ORIGINS=https://yoursite.com,https://app.yoursite.com
LOG_LEVEL=info
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Health Monitoring

### Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Basic health check | `{"status": "healthy"}` |
| `GET /health/ready` | Readiness probe | `{"ready": true}` |
| `GET /health/info` | App info (version, uptime) | `{"version": "1.0.0", ...}` |

### Kubernetes Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: structeng-api
spec:
  template:
    spec:
      containers:
        - name: api
          image: structeng-api:latest
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
```

### Monitoring Metrics

For production monitoring, integrate with:

- **Prometheus**: Add `/metrics` endpoint with `prometheus-fastapi-instrumentator`
- **Sentry**: Error tracking with `sentry-sdk[fastapi]`
- **APM**: Use Datadog, New Relic, or similar

```python
# Example: Add Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Security Hardening

### Production Checklist

- [ ] Use strong, unique `SECRET_KEY` (32+ random characters)
- [ ] Set specific `ALLOWED_ORIGINS` (no wildcards)
- [ ] Enable HTTPS (TLS 1.2+)
- [ ] Set security headers via reverse proxy
- [ ] Configure rate limiting
- [ ] Enable request logging
- [ ] Disable debug mode
- [ ] Use non-root container user
- [ ] Scan dependencies for vulnerabilities
- [ ] Set up log aggregation

### Security Scanning

```bash
# Scan dependencies
pip-audit

# Scan code
bandit -r fastapi_app/ -ll

# Check API for issues
python scripts/check_fastapi_issues.py
```

## Scaling Considerations

### Horizontal Scaling

- Use stateless architecture (no server-side sessions)
- Share rate limit state via Redis
- Use load balancer (nginx, HAProxy, cloud LB)

### Vertical Scaling

- Increase Gunicorn workers: `workers = CPU * 2 + 1`
- Optimize database queries (if added)
- Use async endpoints where possible

### Performance Optimization

```bash
# Benchmark endpoints
python scripts/benchmark_api.py --threshold 50

# Quick performance test
python scripts/benchmark_api.py --quick
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CORS errors | Check `ALLOWED_ORIGINS` matches frontend URL exactly |
| 401 on all requests | Verify `SECRET_KEY` matches between instances |
| Rate limit too aggressive | Increase `RATE_LIMIT_REQUESTS` or `RATE_LIMIT_WINDOW` |
| WebSocket disconnects | Check proxy timeout settings (increase to 86400) |
| Slow responses | Check worker count, enable caching |

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=debug uvicorn fastapi_app.main:app --reload

# Check application state
curl http://localhost:8000/health/info | jq
```

## Related Documents

- [Live 3D Visualization Architecture](../research/live-3d-visualization-architecture.md)
- [API Reference](../reference/api.md)
- [V3 Architecture Overview](../architecture/v3-architecture.md)
