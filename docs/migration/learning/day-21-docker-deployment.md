# Day 21: Docker & Deployment — Containerizing Safety-Critical Calculations

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 20 (End-to-End Data Flow), basic terminal skills
**Library files:** `Dockerfile.fastapi`, `docker-compose.yml`, `docker-compose.dev.yml`, `scripts/launch_stack.sh`, `fastapi_app/main.py`, `fastapi_app/config.py`
**IS 456 Clauses:** None — this is infrastructure

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why Docker matters for structural engineering software (reproducibility is safety)
- How our Dockerfile builds the FastAPI + structural_lib image layer by layer
- What `docker-compose.yml` and `docker-compose.dev.yml` do differently
- How `./run.sh dev` launches the full stack locally
- Container security hardening for an engineering API
- The difference between "library user" (pip install) and "full-stack deployment" (Docker)

---

## Part 1: Why Docker for Structural Engineering?

Structural engineering calculations are **safety-critical**. When a function computes that a beam needs 1,200 mm² of steel, that number must be reproducible — same input, same output, every time, on every machine.

Without Docker:
```
Developer A (macOS, Python 3.11):  Ast = 1,206.5 mm²
Developer B (Ubuntu, Python 3.12): Ast = 1,206.5 mm²  ← same, good
Server (Alpine, Python 3.10):      ImportError: numpy  ← BROKEN
CI runner (Debian, Python 3.11):   Ast = 1,206.5 mm²  ← fixed after debugging
```

With Docker:
```
Everyone, everywhere:              Ast = 1,206.5 mm²  ← identical environment
```

**Three guarantees Docker gives us:**
1. **Reproducibility** — Same Python version, same deps, same OS, same results
2. **Isolation** — Container can't mess up your laptop's Python
3. **Portability** — Works on macOS, Linux, Windows, AWS, GCP, any cloud

---

## Part 2: Colima — Our Docker Runtime on macOS

Docker needs a Linux kernel to run containers. On macOS, something must provide that Linux environment.

| Runtime | Cost | Notes |
|---------|------|-------|
| Docker Desktop | Free for small teams, paid for enterprise | Heavy, auto-updates |
| **Colima** | **Free, open-source** | **Our choice — lightweight, CLI-only** |
| Podman | Free, open-source | Different API, less ecosystem support |

```bash
# Install once
brew install colima docker docker-compose

# Start the VM (allocate resources for structural calculations)
colima start --cpu 4 --memory 4

# Verify it works
docker ps    # Should show empty table, not "permission denied"
```

If `docker ps` gives "Cannot connect to the Docker daemon" — Colima isn't running.

---

## Part 3: Two Audiences, Two Deployment Models

```
┌────────────────────────────┐    ┌────────────────────────────────┐
│   LIBRARY USER             │    │   FULL-STACK DEPLOYER          │
│                            │    │                                │
│   pip install structural-  │    │   Docker image with:           │
│   lib-is456                │    │   - FastAPI backend (:8000)    │
│                            │    │   - React frontend (:5173)     │
│   Pure Python. No Docker.  │    │   - structural_lib inside      │
│   Import and call from     │    │   Web UI + REST API + 3D viz   │
│   your own code.           │    │                                │
│                            │    │   Needs Docker.                │
│   from structural_lib      │    │   docker compose up --build    │
│     import design_beam     │    │                                │
└────────────────────────────┘    └────────────────────────────────┘
```

Docker is for the **full-stack deployment**. Library users who just want `design_beam_is456()` in their Python code don't need Docker at all.

---

## Part 4: The Dockerfile — Layer by Layer

Our `Dockerfile.fastapi` builds the production image:

```dockerfile
FROM python:3.11-slim
# Base: Debian + Python 3.11, ~150MB
# "slim" excludes gcc, make, docs — smaller attack surface

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# No .pyc files (smaller image), unbuffered output (better logging)

WORKDIR /app

# ── Layer 1: System Dependencies (changes rarely → cached 99%) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    libffi-dev libcairo2 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 2: Python Dependencies (changes weekly → cached often) ──
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Layer 3: Install structural_lib (changes per release) ──
COPY Python/pyproject.toml Python/README.md ./Python/
COPY Python/structural_lib ./Python/structural_lib
RUN pip install --no-cache-dir ./Python

# ── Layer 4: Application Code (changes most frequently) ──
COPY fastapi_app ./fastapi_app
COPY Etabs_CSV ./Etabs_CSV

# ── Layer 5: Security Hardening ──
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser
# CRITICAL: Never run as root in production

# ── Layer 6: Runtime Configuration ──
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key insight:** Layer order matters for cache efficiency:
```
Layer 1: apt-get install         ← Changes rarely  (cached 99%)
Layer 2: pip install deps        ← Changes weekly  (cached when deps don't change)
Layer 3: install structural_lib  ← Changes often   (rebuilt when lib code changes)
Layer 4: copy fastapi_app        ← Changes most    (rebuilt on every API change)
```

If you copy code BEFORE installing deps, Docker can't cache the pip install — it rebuilds everything on every code change.

---

## Part 5: docker-compose.yml — Production

```yaml
services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY must be set}
      - RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
      - RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-60}
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**Security features:**

| Setting | What It Does |
|---------|-------------|
| `JWT_SECRET_KEY:?...` | Fails to start if secret not set — prevents insecure defaults |
| `no-new-privileges` | Process can't gain more permissions than it started with |
| `cap_drop: ALL` | Removes ALL Linux capabilities |
| `restart: unless-stopped` | Crashes auto-restart; manual stops stay stopped |
| Non-root user | Container runs as `appuser`, not root |

---

## Part 6: docker-compose.dev.yml — Development with Hot Reload

```yaml
services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    command: ["uvicorn", "fastapi_app.main:app",
              "--host", "0.0.0.0", "--port", "8000", "--reload"]
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret}
    volumes:
      - ./fastapi_app:/app/fastapi_app:ro
      - ./Python/structural_lib:/app/Python/structural_lib:ro
      - ./Etabs_CSV:/app/Etabs_CSV:ro
```

**Key differences from production:**

| Feature | Production | Development |
|---------|-----------|-------------|
| `--reload` flag | No | Yes (auto-restart on changes) |
| Volume mounts | No (code baked in) | Yes (`:ro` — read-only) |
| JWT secret | Must be set explicitly | Default `dev-secret` |
| Code changes | Rebuild image required | Instant (mounted from host) |

---

## Part 7: The Dev Stack Launcher — `./run.sh dev`

```bash
./run.sh dev                  # Local: FastAPI (:8000) + React (:5173)
./run.sh dev --docker         # Docker mode: uses docker-compose
./run.sh dev --docker-dev     # Docker dev: hot reload
./run.sh dev --kill-only      # Stop all dev services
./run.sh dev --no-react       # FastAPI only
./run.sh dev --no-fastapi     # React only
./run.sh dev --open           # Launch + open browser
```

In local mode, `launch_stack.sh` does:
```
1. Kill any existing processes on :8000 and :5173
2. Start FastAPI:  uvicorn fastapi_app.main:app --reload --port 8000
3. Start React:    cd react_app && npm run dev
4. Wait for health checks on both
5. Print status with URLs
```

```
┌──────────────────────────────────────────────────────┐
│                   Developer Machine                  │
│                                                      │
│  ┌──────────────┐        ┌──────────────────────┐    │
│  │ React Dev    │  HTTP  │ FastAPI Backend       │    │
│  │ Server       │───────→│                       │    │
│  │ :5173        │  API   │ :8000                 │    │
│  │              │  calls │ ┌──────────────────┐  │    │
│  │ Vite + HMR  │        │ │ structural_lib   │  │    │
│  │ TypeScript   │        │ │ (IS 456 math)    │  │    │
│  │ Tailwind     │        │ └──────────────────┘  │    │
│  └──────────────┘        └──────────────────────┘    │
│                                                      │
│  Browser: http://localhost:5173                       │
│  API docs: http://localhost:8000/docs                │
└──────────────────────────────────────────────────────┘
```

---

## Part 8: Exercises

### Exercise 1: Build and Explore
```bash
colima start --cpu 4 --memory 4
docker compose build
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" > .env
docker compose up -d
docker compose ps              # Should show: fastapi ... Up (healthy)
curl http://localhost:8000/health
docker compose down
```

### Exercise 2: Development Workflow
```bash
./run.sh dev
# Open http://localhost:5173
# Upload Etabs_CSV/beam_forces.csv → design a beam → export BBS
# Open http://localhost:8000/docs → try POST /api/v1/design/beam
```

### Exercise 3: Understand Layer Caching
```bash
time docker compose build          # ~2 min first time
# Edit fastapi_app/main.py (add a comment)
time docker compose build          # ~15 sec (cached deps)
# Edit requirements.txt (add blank line)
time docker compose build          # ~1 min (pip install rebuilds)
```

---

## Part 9: Self-Check Q&A

1. **Why `python:3.11-slim` not `alpine`?** Alpine uses musl libc — NumPy/SciPy C extensions often fail. Slim is Debian with all C extensions working.
2. **Why COPY requirements.txt before source code?** Docker caches layers. Deps-first means code changes don't rebuild pip install.
3. **What does `cap_drop: ALL` do?** Removes ALL Linux capabilities — the container can only do basic I/O and compute.
4. **What's the difference between `docker compose up` and `./run.sh dev`?** Docker runs in a container; run.sh dev starts processes locally without Docker.
5. **Why Colima instead of Docker Desktop?** Free, open-source, lightweight, no paid license needed.
6. **What happens if JWT_SECRET_KEY isn't set?** Production compose fails to start — the `:?` syntax enforces it.
7. **What's the `:ro` in volume mounts?** Read-only — the container can see but not modify host files.
8. **Why non-root user in Docker?** If an attacker exploits a vulnerability, they can't install packages or modify the system.
9. **How does the HEALTHCHECK work?** Docker pings `/health` every 30 seconds. 3 consecutive failures → container marked unhealthy → orchestrator restarts.
10. **Does a library user need Docker?** No — `pip install structural-lib-is456` works without Docker. Docker is only for the full-stack web deployment.

---

## Part 10: Things to Know — Deep Insights

### 10.1: The slim vs alpine choice is NOT about size
Alpine saves ~100MB but uses musl libc instead of glibc. NumPy, SciPy, and other C extensions compile against glibc. On Alpine, you either get cryptic segfaults or need to compile from source (adding gcc, which eliminates the size advantage). For a scientific Python stack, always use slim.

### 10.2: Docker layer caching is your most important build optimization
A typical pip install takes 90 seconds. If your Dockerfile puts `COPY . .` before `pip install`, every single code change triggers a 90-second rebuild. By putting requirements.txt first, code-only changes rebuild in under 10 seconds. Over a day of development (50+ builds), this saves hours.

### 10.3: Volume mounts with :ro prevent accidental corruption
Without `:ro`, a bug in the container could write to your source code on the host. The read-only flag means the container can read your files but can never modify them — even if a process runs amok.

### 10.4: `PYTHONUNBUFFERED=1` is critical for containerized apps
Without it, Python buffers stdout. If the container crashes, the last few log lines are in the buffer and never printed. In production, those lost lines are exactly the ones you need for debugging. Always set `PYTHONUNBUFFERED=1`.

### 10.5: The HEALTHCHECK is not just monitoring — it enables auto-recovery
Docker Swarm, Kubernetes, and even basic `docker compose` use the healthcheck. When a container is marked unhealthy, the orchestrator can automatically restart it. Without a healthcheck, a process that hangs (but doesn't crash) stays broken forever.

### 10.6: `--no-cache-dir` in pip install reduces image size by 30%
pip caches downloaded wheels in `~/.cache/pip/`. In a Docker image, this cache is useless (you'll never run pip install again). The `--no-cache-dir` flag skips writing the cache, saving 50-200MB depending on dependencies.

---

## Part 11: What Can Be Done Better

### 11.1: No multi-stage build
The current Dockerfile installs build tools (libffi-dev) that aren't needed at runtime. A multi-stage build would compile in a "builder" stage, then copy only the built artifacts to a clean "runtime" stage — reducing image size by ~200MB.

### 11.2: No .dockerignore file
Without `.dockerignore`, `docker build` sends the ENTIRE context (node_modules, .git, docs, logs) to the Docker daemon. A proper `.dockerignore` would skip these, reducing build context from ~500MB to ~50MB and speeding up builds.

### 11.3: No image scanning in CI
The built image should be scanned for known CVEs in system packages and Python dependencies. Tools like `trivy`, `grype`, or `docker scout` can flag vulnerabilities before deployment.

### 11.4: No container resource limits
The compose file doesn't set `mem_limit` or `cpus`. A single runaway calculation could consume all available memory and crash the host. Resource limits prevent this.

### 11.5: No log rotation or structured logging
Container logs grow unbounded. In production, they should use structured JSON logging and be forwarded to a log aggregator (ELK, Loki, CloudWatch) with rotation policies.

---

## Part 12: Innovation Directions

### 12.1: Multi-stage build with distroless base
Use `gcr.io/distroless/python3` as the final stage — no shell, no package manager, no attack surface. The image contains ONLY the Python runtime and your code. If an attacker gets in, there's no `bash`, `curl`, or `apt` to exploit.

### 12.2: Container-native health probes
Beyond simple HTTP checks, add readiness probes (is the model loaded?) and liveness probes (is the event loop responsive?). Kubernetes uses these to route traffic only to healthy pods.

### 12.3: BuildKit cache mounts
Docker BuildKit supports `--mount=type=cache,target=/root/.cache/pip` which caches pip downloads ACROSS builds without storing them in the image. Faster rebuilds AND smaller images.

### 12.4: Serverless deployment (AWS Lambda / Cloud Run)
Package the FastAPI app as a serverless function. Pay only per request. Zero servers to manage. Google Cloud Run supports any Docker container as a service.

### 12.5: Dev Containers for VS Code
A `.devcontainer/devcontainer.json` would let any developer open the repo in VS Code and instantly have the full environment — Python, Node, extensions, settings — running inside a container. Zero local setup.

---

## Part 13: Next Repo Must-Add

### Concrete items

1. **`.dockerignore` file** — Exclude `.git/`, `node_modules/`, `docs/`, `logs/`, `*.pyc`
2. **Multi-stage Dockerfile** — Builder stage for compilation, runtime stage for serving
3. **Image CVE scanning in CI** — `trivy image` in GitHub Actions pipeline
4. **Container resource limits** — `mem_limit: 2g` and `cpus: 2.0` in compose
5. **Structured JSON logging** — Replace print statements with structured loggers
6. **Dev Container config** — `.devcontainer/` for instant VS Code setup
7. **Docker Compose profiles** — Separate dev/staging/prod with `profiles:` instead of multiple files

### Day-1 checklist for containerizing a new service

```
□ 1. Write Dockerfile with deps-first layer ordering
□ 2. Use slim base image (not alpine for scientific Python)
□ 3. Create non-root user, switch to it before CMD
□ 4. Add HEALTHCHECK with reasonable intervals
□ 5. Set PYTHONDONTWRITEBYTECODE=1 and PYTHONUNBUFFERED=1
□ 6. Add .dockerignore (exclude .git, node_modules, docs, __pycache__)
□ 7. Use -no-cache-dir with pip install
□ 8. Set cap_drop: ALL and no-new-privileges in compose
□ 9. Use :ro on all volume mounts in dev compose
□ 10. Test: build, run, healthcheck, stop — all must work cleanly
```

---

## Summary

| Concept | Command / File | Purpose |
|---------|---------------|---------|
| Docker runtime (macOS) | `colima start --cpu 4 --memory 4` | Provides Linux kernel for containers |
| Build image | `docker compose build` | Creates production image from Dockerfile |
| Production deploy | `docker compose up` | Runs container with security hardening |
| Dev with hot reload | `docker compose -f docker-compose.dev.yml up` | Volume mounts + `--reload` |
| Easiest dev start | `./run.sh dev` | Local FastAPI + React, no Docker needed |
| Kill dev services | `./run.sh dev --kill-only` | Stops all running dev processes |
| Health check | `curl localhost:8000/health` | Verifies API is running |
| API docs | `localhost:8000/docs` | Swagger UI for all endpoints |
| Container security | `cap_drop: ALL`, non-root user | Minimal privileges |
| Layer caching | Deps before code in Dockerfile | Fast rebuilds on code changes |

---

## References

- `Dockerfile.fastapi` — Production image definition
- `docker-compose.yml` — Hardened deployment
- `docker-compose.dev.yml` — Hot reload with volume mounts
- `scripts/launch_stack.sh` — Full-stack startup script
- `fastapi_app/main.py` — Application setup, middleware, routers
- `fastapi_app/config.py` — Environment variable management
- **Previous:** Day 20 covers end-to-end data flow through all layers
- **Next:** Day 22 covers Git automation with ai_commit.sh

You've now completed the full journey from raw materials (Day 1) through IS 456 math, API design, frontend integration, data flow, and deployment. The next modules will cover advanced topics like **testing strategies**, **CI/CD pipelines**, and **contributing to the library**. But with Days 1-21 under your belt, you can already read, understand, and modify any layer of this codebase.
