# 06: Free-Tier Cloud Deployment Configuration & CI/CD Pipeline

**What to build:** Complete, production-ready cloud deployment blueprints for Render (FastAPI Web Service + React Static Site) and Supabase (PostgreSQL), with automated Alembic migrations on release and end-to-end GitHub Actions continuous integration verification.

**Blocked by:** 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup, 02: Multi-Tier Alert Service Hardening & Scoped Alerts API, 03: On-Demand Cloud Telemetry Controller API & CLI Runner

**Status:** resolved

- [x] Render configuration (`render.yaml` Blueprint or deployment manifest) defining:
  - Backend Web Service (Python 3.11, environment variables, pre-deploy `alembic upgrade head`, start command).
  - Frontend Static Site (Build command, publish directory, SPA rewrite rules).
- [x] Production environment variable template (`.env.production.example`) with documentation for Supabase DB connection string and Africa's Talking API keys.
- [x] Healthcheck endpoint (`GET /health`) verifying database connectivity, ML model loading, and alert subsystem status.
- [x] `.github/workflows/ci.yml` expanded to run backend, ML, simulator, and frontend test suites and verify static site compilation.
- [x] End-to-end containerized verification via Docker Compose confirms clean cold-start execution.

## Answer

Implemented in `render.yaml`, `.env.production.example`, `backend/app/main.py` (`/health` endpoint), `docker-compose.yml`, and `.github/workflows/ci.yml`.
- `render.yaml` defines the full Blueprint for free-tier Render deployment (FastAPI web service with auto Alembic migrations + Vite React static site with SPA rewrite rules).
- `.env.production.example` documents Supabase PostgreSQL pooler configuration and Africa's Talking SMS modes.
- `/health` endpoint checks database connectivity, ML model loading status, and alert dispatch mode.
- CI/CD in `.github/workflows/ci.yml` verifies the full Python test suite (49 tests) and Vite frontend compilation (18 tests).
