# Mac Mini Setup Guide

**Type:** Guide
**Audience:** AI Agents, Developers
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-26
**Last Updated:** 2026-03-26

Complete instructions to clone and run the full stack on a fresh Mac Mini (Apple Silicon).
This guide is designed so an AI agent or developer can follow it end-to-end without ambiguity.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| macOS | Sonoma 14+ or Sequoia 15+ | Pre-installed |
| Homebrew | Latest | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Git | 2.39+ | `brew install git` (or use Xcode CLT) |
| Python | 3.11.x | `brew install python@3.11` |
| Node.js | 18+ (v20 LTS or newer) | `brew install node@20` or use `nvm` |
| Docker + Colima | Latest | `brew install docker docker-compose colima` |
| VS Code | Latest | `brew install --cask visual-studio-code` |

> **Note:** Node v20+ and v25+ both work. The codebase requires Node 18 minimum.
>
> **Why Colima over Docker Desktop?** Colima is lightweight, CLI-based, uses less RAM, and is faster for dev machines. Docker Desktop works too but runs a heavier background VM.

### System libraries (needed for PDF reports via WeasyPrint)

```bash
brew install cairo pango libffi
```

---

## Step 1: Clone the Repository

```bash
cd ~/Project_VS_code   # or your preferred workspace
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib
```

### Verify the clone

```bash
ls Python/ react_app/ fastapi_app/ scripts/ docs/
# Should list all five directories
```

---

## Step 2: Python Environment

### Create virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Install all dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` installs **all** runtime dependencies (FastAPI, pandas, numpy, scipy, etc.).

### Install the library in editable mode (for development)

```bash
cd Python
pip install -e ".[dev,dxf,render,report,pdf,validation,cad]"
cd ..
```

> **Why both?** `requirements.txt` covers full-stack deps (FastAPI, testing tools, etc.). The editable install (`pip install -e`) registers `structural_lib` as an importable package and adds optional extras (DXF, PDF, CAD). Both are needed.

### Install pre-commit hooks

```bash
pre-commit install
```

### Verify Python setup

```bash
.venv/bin/python -c "import structural_lib; print(structural_lib.__version__)"
# Should print: 0.19.1 (or current version)
```

---

## Step 3: Run Python Tests

```bash
cd Python
../.venv/bin/pytest tests/ -q --tb=short --ignore=tests/performance
cd ..
```

**Expected:** 3,100+ tests pass, 0 failures.

---

## Step 4: React Frontend

### Install Node dependencies

```bash
cd react_app
npm install
```

### Set up environment

```bash
cp .env.example .env.local
```

Contents of `.env.local` (defaults are fine for local dev):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Build check

```bash
npm run build
```

**Expected:** Build succeeds with no errors.

### Start dev server

```bash
npm run dev
```

**URL:** http://localhost:5173

```bash
cd ..
```

---

## Step 5: FastAPI Backend

### Option A: Run directly (recommended for development)

```bash
cp .env.example .env   # .env.example exists in repo root
source .venv/bin/activate
uvicorn fastapi_app.main:app --host "::" --port 8000 --reload
```

### Option B: Run via Docker (Colima)

Start Colima first (if not already running):

```bash
colima start --cpu 4 --memory 4
```

Then run the containers:

```bash
cp .env.example .env
docker compose up --build
```

For dev with hot-reload:

```bash
docker compose -f docker-compose.dev.yml up --build
```

To stop Colima when done:

```bash
colima stop
```

**API docs:** http://localhost:8000/docs
**Health check:** http://localhost:8000/health

---

## Step 6: Environment File Reference

### Root `.env` (copy from `.env.example`)

```env
JWT_SECRET_KEY=change-me-in-production
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### `react_app/.env.local` (copy from `.env.example`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Step 7: Verify Full Stack

Run these commands to confirm everything works:

```bash
# 1. Environment check
./run.sh session start

# 2. Quick validation (8 checks, <30 seconds)
./run.sh check --quick

# 3. Full test suite
./run.sh test

# 4. React build
cd react_app && npm run build && cd ..

# 5. FastAPI starts (Ctrl+C after confirming)
uvicorn fastapi_app.main:app --port 8000 &
curl -s http://localhost:8000/health | head -1
kill %1
```

---

## Daily Workflow Commands

```bash
./run.sh session start              # Begin work session
./run.sh commit "type: message"     # Safe commit + push (ALWAYS use this)
./run.sh check --quick              # Fast validation
./run.sh test                       # Run pytest suite
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get exact API parameter names
./run.sh pr create TASK-XXX "desc"  # Start a PR branch
./run.sh pr finish                  # Ship the PR
./run.sh session end                # End-of-session logging
```

**Git rule:** NEVER use manual `git add/commit/push`. Always use `./scripts/ai_commit.sh` or `./run.sh commit`.

---

## Architecture Overview

```
structural_engineering_lib/
├── Python/structural_lib/      # Core library (IS 456 beam design)
│   ├── core/                   #   Base types, constants
│   ├── codes/is456/            #   Pure math (flexure, shear, torsion)
│   ├── services/               #   Orchestration (api.py, adapters.py)
│   ├── insights/               #   Design insights & analysis
│   ├── visualization/          #   3D geometry generation
│   └── reports/                #   Report templates
├── fastapi_app/                # REST + WebSocket backend (38 endpoints)
│   └── routers/                #   12 routers (design, geometry, import, export...)
├── react_app/src/              # React 19 + TypeScript + R3F + Tailwind
│   ├── components/             #   UI components by feature
│   ├── hooks/                  #   Custom hooks (CSV, geometry, design, export)
│   ├── store/                  #   Zustand state stores
│   └── types/                  #   TypeScript definitions
├── scripts/                    # 80+ automation scripts
├── docs/                       # Documentation (250+ files)
│   ├── TASKS.md                #   Current task board
│   ├── planning/               #   next-session-brief.md (agent handoff)
│   └── getting-started/        #   This file
└── run.sh                      # Unified CLI entry point
```

**Import rule:** Core cannot import from Services. Services cannot import from UI.
**Units:** Always explicit at API boundaries — mm, kN, kNm, N/mm².

---

## Ports Summary

| Service | Port | URL |
|---------|------|-----|
| React dev server | 5173 | http://localhost:5173 |
| FastAPI backend | 8000 | http://localhost:8000 |
| FastAPI API docs | 8000 | http://localhost:8000/docs |

---

## Troubleshooting

### `pip install weasyprint` fails

Install system dependencies first:

```bash
brew install cairo pango libffi
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"
pip install weasyprint
```

### `npm run build` fails with memory error

Increase Node memory:

```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Python import errors after clone

Make sure the library is installed in editable mode:

```bash
cd Python && pip install -e ".[dev]" && cd ..
```

### pre-commit hooks fail on first run

```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

### Docker build fails (WeasyPrint/Cairo)

The Dockerfile handles system deps automatically. If issues persist:

```bash
docker compose build --no-cache
```

### Colima won't start

```bash
colima delete    # Remove existing VM
colima start     # Fresh start
docker info      # Verify Docker is connected
```

---

## VBA/Excel Files (Local Only)

VBA and Excel files are **gitignored** but may exist locally at `VBA/` and `Excel/`.
These are not needed for the Python/React/FastAPI stack.
A separate VBA-specific repository is planned for the future.

---

## Reproducible Environment Setup

To replicate your full dev environment on a new machine, export these from your current machine:

```bash
# On old machine — run once to capture state
brew bundle dump --file=~/Brewfile          # All Homebrew packages
code --list-extensions > ~/extensions.txt   # VS Code extensions
npm list -g --depth=0 > ~/global-npm.txt    # Global npm packages (if any)
```

Then on the new machine:

```bash
# Replay
brew bundle --file=~/Brewfile
cat ~/extensions.txt | xargs -L 1 code --install-extension
```

---

## What to Read Next

- [agent-bootstrap.md](agent-bootstrap.md) — AI agent onboarding (60-second version)
- [python-quickstart.md](python-quickstart.md) — Python library usage examples
- [../TASKS.md](../TASKS.md) — Current task board and priorities
- [../planning/next-session-brief.md](../planning/next-session-brief.md) — Latest handoff notes
