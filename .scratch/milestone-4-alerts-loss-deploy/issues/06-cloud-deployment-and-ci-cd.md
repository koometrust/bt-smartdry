# 06: Free-Tier Cloud Deployment Configuration & CI/CD Pipeline

**What to build:** Complete, production-ready cloud deployment blueprints for Render (FastAPI Web Service + React Static Site) and Supabase (PostgreSQL), with automated Alembic migrations on release and end-to-end GitHub Actions continuous integration verification.

**Blocked by:** 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup, 02: Multi-Tier Alert Service Hardening & Scoped Alerts API, 03: On-Demand Cloud Telemetry Controller API & CLI Runner

**Status:** ready-for-agent

- [ ] Render configuration (`render.yaml` Blueprint or deployment manifest) defining:
  - Backend Web Service (Python 3.11, environment variables, pre-deploy `alembic upgrade head`, start command).
  - Frontend Static Site (Build command, publish directory, SPA rewrite rules).
- [ ] Production environment variable template (`.env.production.example`) with documentation for Supabase DB connection string and Africa's Talking API keys.
- [ ] Healthcheck endpoint (`GET /health`) verifying database connectivity, ML model loading, and alert subsystem status.
- [ ] `.github/workflows/ci.yml` expanded to run backend, ML, simulator, and frontend test suites and verify static site compilation.
- [ ] End-to-end containerized verification via Docker Compose confirms clean cold-start execution.

