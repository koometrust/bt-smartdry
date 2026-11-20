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

- **In:** working prototype, synthetic data only, 3 hubs, 3 crops, 2 roles, bilingual templates, SMS alerts with multi-tier dispatch and dashboard audit view, avoided-loss estimator, on-demand simulator control, Render + Supabase cloud deployment, comprehension evaluation protocol.
- **Out:** real sensor integration (simulated only), LLM, WhatsApp, edge inference, production security audit, formal third-party carbon-credit registration, real personal data.

## Milestone 4 Decisions

### Avoided-Post-Harvest-Loss Estimator (Objective 6)
- **Formulation:**
  $$\text{kg\_saved} = \text{initial\_weight\_kg} \times (\text{baseline\_loss\_rate} - \text{smartdry\_loss\_rate})$$
  $$\text{kes\_saved} = \text{kg\_saved} \times \text{market\_price\_per\_kg} \times \text{grade\_multiplier}$$
- **Baseline parameters:**
  - Moringa: Open-sun 35% vs SmartDry 5%, KES 300/kg
  - Prunus: Open-sun 30% vs SmartDry 4%, KES 450/kg
  - Hibiscus: Open-sun 40% vs SmartDry 6%, KES 250/kg
- **Quality grade multipliers:** Export = 1.0 (100%), Standard = 0.9 (90%), Downgraded = 0.5 (50%).
- **Persistence:** Persisted on `batches` table (`avoided_loss_kg`, `avoided_loss_kes`) when an operator confirms completion.
- **Presentation:** Rendered on Batch Detail and Batch History with explicit disclaimer: *"Indicative post-harvest metric; non-certified carbon or agronomic claim"*. Aggregated across crops and hubs on the Administrator Analytics page.

### Alerts & Africa's Talking Integration
- **Dispatch modes (`SMS_PROVIDER_MODE`):**
  - `mock`: Logs SMS to DB and backend console without network calls (default for local dev and CI/CD).
  - `sandbox`: Dispatches via Africa's Talking Sandbox API.
  - `live`: Dispatches real SMS to configured phone numbers via Africa's Talking live API with KES 500 airtime budget.
- **Dashboard Alert UI:**
  - Dedicated `/alerts` audit page with filterable table (Hub, Alert Type, Date range).
  - Header notification bell icon with real-time unread badge opening an Alert slide-out drawer.
  - Built using shadcn UI components (Sheet, Table, Badge, Button).
  - Polled every 30 seconds via React Query.

### Cloud Deployment & On-Demand Telemetry (Objective 5)
- **Target:** Render free tier (FastAPI Web Service + React Static Site) + Supabase (PostgreSQL).
- **Alembic migrations:** Run automatically as a pre-deploy release command.
- **On-demand simulator:** Controlled via authenticated endpoints `POST /api/v1/simulator/start` and `POST /api/v1/simulator/stop` (plus CLI runner) to prevent burning free-tier compute hours.

### Comprehension Evaluation Protocol (Objective 4)
- **Protocol:** `docs/evaluations/comprehension_test.md`.
- **Battery:** 5 canonical batch scenarios (Normal Drying, Near-Completion, Completion, Overheating Anomaly, High Humidity Anomaly) across English and Kiswahili.
- **Participants:** 5 testers (including native Kiswahili speakers and hub workers).
- **Scoring:** 3-point rubric (Correct 1.0, Partially Correct 0.5, Incorrect 0.0) targeting $\ge 80\%$ mean accuracy.

## Kiswahili

- Author (you) writes bilingual template examples.
- At least one native Kiswahili speaker among the 3–5 comprehension testers validates output quality.

