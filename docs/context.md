# BT-SmartDry: Design Decisions

Canonical record of all decisions made during the grilling session. Overrides `docs/agents/proposal.md` where they conflict. Hard-to-reverse decisions with genuine trade-offs are also recorded as ADRs in `docs/adr/`.

## Architecture

- **Cloud-only prototype.** No edge inference. Everything runs on Render/Supabase. The report notes edge deployment as future work.
- **Monorepo** with top-level directories: `frontend/`, `backend/`, `ml/`, `simulator/`, `docs/`, `.github/workflows/`.
- **ML inference is embedded in the backend** (a Python module loaded at startup), not a separate microservice.
- **No LLM.** Advisories are bilingual template strings with variable slots. See [ADR-0001](adr/0001-templated-advisories-over-llm.md).

## Data model

- **One dryer per hub, but multiple concurrent batches per dryer**, bounded by a 200 kg capacity. See [ADR-0002](adr/0002-multi-batch-per-dryer.md).
- **Batch states:** `active` (drying) and `completed` (operator confirmed removal). Transition is an explicit operator action.
- **3 quality grades:** Export, Standard, Downgraded. Over-drying degrades quality (both under-drying and over-drying penalised).
- **3 crop types:** Moringa, Prunus, Hibiscus.
- **Batch creation fields:** crop type (dropdown), weight in kg (number), target moisture % (optional, default per crop).
- **5 database tables:** `users`, `hubs`, `batches`, `readings`, `alerts`.
- **Readings are per-batch.** Ambient fields (temperature, humidity, VPD) are duplicated across batches sharing a dryer at the same timestamp. Moisture content is per-batch.

## ML

- **Single latest-snapshot model**, not time-series. First prediction after the first reading.
- **10 features:** temperature, humidity, VPD, current moisture, batch weight (kg), crop type, hub location, elapsed hours, ambient temperature, ambient humidity.
- **Two models:** XGBoost regressor for remaining hours; gradient-boosted classifier (or Random Forest — whichever wins on validation) for quality grade.
- **Training:** 80/20 split, 5-fold cross-validation. Check class balance; use resampling or class weights if needed.
- **Targets:** R² ≥ 0.85 (time), ≥ 80% accuracy (grade).
- **Fairness check:** compare predictions across crop type and hub; flag subgroups with systematically worse accuracy.
- **Model artifacts:** committed to `backend/models/` (< 5 MB each). Loaded at backend startup.

## Synthetic data

- **~2,000 batch records**, each with ~50–150 readings at 5-minute intervals.
- **Exponential-decay drying curves** with crop/hub/weight-dependent parameters.
- **Grade determined by rules:** final moisture in optimal range + drying time within bounds → Export; borderline → Standard; outside (too wet or too dry) → Downgraded.

## Simulator

- **Simulated device script** (Python process POSTing synthetic readings to the API).
- **Default interval:** 5 minutes. Configurable down to 1 second for demos.
- **Supports multiple concurrent batches** across hubs (e.g., moringa + hibiscus in Meru, prunus in Eldoret).
- **Optional future enhancement:** Wokwi virtual devices for demo visualisation.

## Advisory and alerts

- **Advisories are bilingual templates** (English + Kiswahili) stored as JSON i18n files (`locales/en.json`, `locales/sw.json`). No LLM.
- **Operator's language preference** is a field on their user profile; backend and frontend respect it.
- **Frontend i18n:** `react-i18next`.
- **SMS alerts via Africa's Talking** (sandbox during development, live with KES 500 credit for defense demo).
- **3 alert trigger types**, max 1 per type per batch:
  1. Near-completion (predicted remaining time < 30 min)
  2. Completion (target moisture reached)
  3. Anomaly (temperature or humidity outside safe range)
- **WhatsApp** is out of scope for the prototype.

## Dashboard

- **6 pages:**
  1. Active Batches (operator: hub-scoped; admin: all hubs)
  2. Batch Detail (sensor chart, current advisory, predicted grade)
  3. Batch History (completed batches with final grades)
  4. Hub Overview (admin only: summary cards per hub)
  5. Analytics (admin only: historical trends, crop stats, hub comparison)
  6. Login
- **Polling every 30 seconds** via React Query (`refetchInterval: 30000`). No WebSockets.
- **Responsive, mobile-first** for low-cost Android screens. Sufficient colour contrast; text labels not colour alone.

## Auth

- **JWT** with username/password login. `python-jose` + bcrypt.
- **2 roles:** Operator (hub-scoped) and Administrator (cross-hub).
- **Pre-seeded test accounts** (one operator per hub, one admin). No registration flow.

## Stack and tooling

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Data fetching | React Query (TanStack Query) |
| Backend | FastAPI (Python) |
| ORM | SQLAlchemy (async + asyncpg) |
| Migrations | Alembic |
| Database | Supabase (PostgreSQL, free tier) |
| SMS | Africa's Talking |
| ML training | XGBoost, scikit-learn |
| Package mgmt (Python) | `requirements.txt` + `venv` |
| Package mgmt (JS) | npm |
| Local dev | Docker Compose |
| Hosting | Render free tier (static site for frontend, web service for backend) |
| CI/CD | GitHub Actions |
| Version control | Git (this repo) |

## Scope

- **In:** working prototype, synthetic data only, 3 hubs, 3 crops, 2 roles, bilingual templates, SMS alerts, Render deployment.
- **Out:** real sensor integration (simulated only), LLM, WhatsApp, edge inference, production security audit, carbon-credit registration, real personal data.
- **Objective 6 (avoided-loss estimator):** not planned architecturally. If time permits at week 18, it's a simple dashboard card addition.

## Kiswahili

- Author (you) writes bilingual template examples.
- At least one native Kiswahili speaker among the 3–5 comprehension testers validates output quality.

