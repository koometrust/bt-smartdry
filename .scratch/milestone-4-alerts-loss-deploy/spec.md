Status: ready-for-agent

# Milestone 4 Spec: Alerts Hardening, Avoided-Loss Estimator, Cloud Deployment, and Comprehension Protocol

## Problem Statement

With the core telemetry simulator, machine learning pipeline, and operator/admin dashboard in place (Milestones 1–3), BT-SmartDry requires the final feature-complete capabilities and empirical verification defined in the project proposal before thesis defense:
1. Operators and Administrators need visibility into triggered SMS alerts directly within the dashboard (without relying solely on external mobile handsets) and need guaranteed zero-cost testability alongside reliable live cellular dispatch via Africa's Talking.
2. Smallholder drying hubs in Kenya experience 30%–40% post-harvest spoilage under open-air sun drying. Hub stakeholders and administrators lack a quantified, indicative metric demonstrating the physical kilograms and economic value (KES) preserved by BT-SmartDry's controlled solar drying across batches and hubs.
3. The platform currently runs only locally via Docker Compose; it needs automated cloud deployment configuration (Render + Supabase) that operates within free-tier constraints without exhausting monthly instance hours on 24/7 background telemetry simulation.
4. Objective 4 requires empirical proof of $\ge 80\%$ operator advisory comprehension across English and Kiswahili through a structured, documented evaluation protocol.

## Solution

Deliver the four integrated tracks of Milestone 4:
1. **Multi-Tier Alerts & Dashboard Audit UI**:
   - Support `SMS_PROVIDER_MODE=mock|sandbox|live` for cost-free testing, sandbox verification, and live SMS delivery via Africa's Talking.
   - Expose `/api/v1/alerts/` with role-scoped filtering (Operator hub-scoped, Administrator cross-hub).
   - Implement an in-dashboard Alert system using **shadcn UI** primitives: a top-level `/alerts` audit log table and a header notification bell with real-time unread badge opening an Alert slide-out drawer, polled on the 30-second React Query cycle.
2. **Avoided-Post-Harvest-Loss Estimator (Objective 6)**:
   - Calculate physical biomass preserved (`avoided_loss_kg`) and indicative economic value (`avoided_loss_kes`) upon batch completion, factoring in crop-specific baseline loss rates (Moringa 35% vs 5%, Prunus 30% vs 4%, Hibiscus 40% vs 6%) and market prices.
   - Apply Quality Grade pricing multipliers (Export = 100%, Standard = 90%, Downgraded = 50%) to penalize over-drying and under-drying.
   - Persist these metrics on the `batches` table upon completion.
   - Display batch savings on Batch Detail and Batch History with the explicit disclaimer: *"Indicative post-harvest metric; non-certified carbon or agronomic claim"*.
   - Aggregate total kilograms and value preserved across all hubs on the Administrator Analytics page.
3. **Cloud Deployment & On-Demand Telemetry (Objective 5)**:
   - Provide deployment configurations for Render (FastAPI Web Service + React Static Site) and Supabase (PostgreSQL), with Alembic migrations executing automatically on release.
   - Introduce an on-demand telemetry runner controllable via authenticated backend endpoints (`POST /api/v1/simulator/start`, `POST /api/v1/simulator/stop`, `GET /api/v1/simulator/status`) and a CLI script, preventing continuous compute-hour depletion on free-tier cloud infrastructure.
   - Update GitHub Actions CI/CD to validate the end-to-end build and test matrix.
4. **Bilingual Advisory Comprehension Evaluation Protocol (Objective 4)**:
   - Author `docs/evaluations/comprehension_test.md` defining a 5-scenario evaluation battery across English and Kiswahili administered to 5 participants.
   - Implement a standardized 3-point rubric (Correct 1.0, Partially Correct 0.5, Incorrect 0.0) targeting $\ge 80\%$ mean score, with a complete results recording sheet for the capstone dissertation.

## User Stories

1. As an Operator, I want to see an unread alert badge on a notification bell in the dashboard header, so that I immediately notice when a batch reaches near-completion, completion, or an anomaly without checking my phone.
2. As an Operator, I want to click the notification bell to open a slide-out drawer of recent alerts, so that I can quickly review trigger conditions and recommended actions while monitoring active batch curves.
3. As an Operator or Administrator, I want to navigate to a dedicated `/alerts` page, so that I can inspect the full historical audit trail of alerts sent across drying cycles.
4. As an Administrator, I want to filter the alerts table by Hub, Alert Type, and date range, so that I can audit communication reliability across all three hubs.
5. As a developer or tester, I want the backend to support `SMS_PROVIDER_MODE=mock`, so that automated test suites and local development execute instantly without external API credentials or network dependency.
6. As a presenter, I want to toggle `SMS_PROVIDER_MODE=live` with pre-allocated airtime credit, so that I can demonstrate real SMS alerts delivered to an evaluator's mobile phone during the defense.
7. As an Operator completing a drying batch, I want the system to calculate the avoided harvest loss in kilograms and financial value in KES, so that our hub can track post-harvest preservation achievements.
8. As an Operator, I want over-dried or under-dried batches graded as Downgraded to reflect a 50% economic discount in avoided loss value, so that quality degradation is realistically accounted for.
9. As an Operator, I want to see the avoided loss metrics prominently displayed on the Batch Detail and Batch History views alongside an indicative disclaimer, so that I understand this is an operational estimate rather than a certified claim.
10. As an Administrator, I want the Analytics page to display aggregate avoided loss metrics (total kg preserved, total KES value, and breakdown by crop and hub), so that I can present overall network impact to stakeholders.
11. As a cloud deployer, I want Render blueprint and pre-deploy configuration files, so that the backend, frontend, and Supabase database can be provisioned and updated automatically on Git pushes.
12. As a cloud administrator, I want to start and stop telemetry simulation on demand via the API or dashboard rather than running a 24/7 background daemon, so that we remain within Render's 750 free monthly compute hours.
13. As an evaluator or supervisor, I want to inspect a formal comprehension testing protocol and empirical results template, so that I can verify the scientific rigor of the $\ge 80\%$ advisory comprehension objective.
14. As an Operator using Kiswahili, I want the avoided loss labels, alert drawer titles, and table headers to be fully translated, so that the interface remains consistently accessible in my preferred language.

## Implementation Decisions

### 1. Database Schema & Migration
- Add `avoided_loss_kg` (Float, nullable) and `avoided_loss_kes` (Float, nullable) to the `batches` table.
- Create an Alembic migration (`add_avoided_loss_to_batches`) to apply these columns cleanly.
- Ensure existing completed batches in seed data have realistic calculated values populated.

### 2. Avoided Loss Calculation Module
- Module: `backend/app/services/loss_service.py`
- Formulation:
  - `kg_saved = initial_weight_kg * (baseline_loss_rate - smartdry_loss_rate)`
  - `kes_saved = kg_saved * market_price_per_kg * grade_multiplier`
- Crop constants:
  - Moringa: `baseline_loss_rate = 0.35`, `smartdry_loss_rate = 0.05`, `market_price_per_kg = 300.0`
  - Prunus: `baseline_loss_rate = 0.30`, `smartdry_loss_rate = 0.04`, `market_price_per_kg = 450.0`
  - Hibiscus: `baseline_loss_rate = 0.40`, `smartdry_loss_rate = 0.06`, `market_price_per_kg = 250.0`
- Grade multipliers:
  - Export: `1.0` (100%)
  - Standard: `0.9` (90%)
  - Downgraded: `0.5` (50%)
- Trigger: Calculated inside `batch_service.complete_batch` when the batch transitions to `completed`.
- Analytics: Update `backend/app/api/v1/endpoints/analytics.py` (or hub/batch queries) to include `total_avoided_loss_kg` and `total_avoided_loss_kes` in the aggregated response.

### 3. Multi-Tier Alert Service & API
- Configuration: Add `SMS_PROVIDER_MODE: str = "mock"` (values: `mock`, `sandbox`, `live`) to `backend/app/core/config.py`.
- Service logic: In `backend/app/services/alert_service.py`, branch execution:
  - If `mock`: record Alert with status `sent` (mocked) and log to stdout.
  - If `sandbox`: initialize Africa's Talking SDK with sandbox credentials and dispatch.
  - If `live`: initialize Africa's Talking SDK with live credentials and sender ID.
  - On network/API exception: record Alert with status `failed`.
- Endpoints in `backend/app/api/v1/endpoints/alerts.py`:
  - `GET /api/v1/alerts/`: List alerts with pagination and query filters (`hub_id`, `alert_type`, `limit`). Scoped so Operators only see alerts for batches in their hub; Administrators see all.
  - `GET /api/v1/alerts/unread-count`: Returns the number of recent unread alerts for the authenticated user's scope.
  - `POST /api/v1/alerts/{id}/read`: Mark alert as read/acknowledged.

### 4. On-Demand Simulator Controller
- Endpoints in `backend/app/api/v1/endpoints/simulator.py`:
  - `POST /api/v1/simulator/start`: Launches an asynchronous background simulation task (or runs in-process batch stepping) with configurable interval.
  - `POST /api/v1/simulator/stop`: Gracefully terminates the running simulation task.
  - `GET /api/v1/simulator/status`: Returns whether the simulator is actively running, active batch count, and last tick timestamp.
  - Restricted to authenticated users (Administrators or hub Operators).

### 5. Frontend UI with shadcn UI Primitives
- **Navigation & Layout**:
  - Add `/alerts` route to main navigation.
  - Add notification bell icon to `Navbar.tsx` displaying a badge count of recent alerts.
  - Clicking the bell opens a slide-out drawer (`Sheet` component from shadcn UI) listing recent alerts with relative timestamps and alert type badges.
- **Alerts Audit Page (`/alerts`)**:
  - Filterable data table using shadcn UI `Table`, `Badge`, `Select`, and `Input`.
  - Filter by Alert Type (`Near Completion`, `Completion`, `Anomaly`) and Hub.
- **Avoided Loss Presentation**:
  - `BatchDetailPage.tsx`: For completed batches, display an "Avoided Harvest Loss" card showing `kg_saved` and `kes_saved` alongside quality grade, with the required indicative disclaimer.
  - `BatchHistoryPage.tsx`: Add columns/badges for preserved weight and economic value.
  - `AnalyticsPage.tsx`: Add metric summary cards for total avoided loss (kg) and total revenue preserved (KES), plus visual breakdown by crop.
- **Translations (`locales/en.json`, `locales/sw.json`)**:
  - Complete bilingual coverage for all new UI text, table headers, drawer controls, and loss metrics.

### 6. Cloud Deployment & CI/CD Configuration
- Render configuration: `render.yaml` specifying:
  - Backend Web Service (Python 3.11, environment variables, pre-deploy `alembic upgrade head`, start `uvicorn app.main:app`).
  - Frontend Static Site (Build `npm run build`, publish directory `dist`, SPA rewrite rule).
- Updated GitHub Actions CI workflow in `.github/workflows/ci.yml` testing migrations, avoided loss calculations, alert endpoints, and frontend build.

### 7. Evaluation Protocol Document
- File: `docs/evaluations/comprehension_test.md`
- Contents:
  - Objectives and hypothesis.
  - 5 bilingual test scenarios with exact sensor triggers and advisory texts.
  - 5 participant profiles (including native Kiswahili speakers and hub operators).
  - 3-point scoring rubric (1.0 = Correct action, 0.5 = Partially correct, 0.0 = Misunderstood).
  - Target: Mean comprehension score $\ge 0.80$ (80%).
  - Pre-populated empirical test matrix with evaluation results ready for dissertation inclusion.

## Testing Decisions

- **Test Seam 1: Backend Integration (`backend/tests/`)**:
  - Test `test_loss_service.py`: Verify physical kg saved and KES value across all 3 crops, testing edge cases and grade multipliers (Export 1.0, Standard 0.9, Downgraded 0.5).
  - Test `test_batch_completion_loss.py`: Verify that completing a batch through `PATCH /api/v1/batches/{id}/complete` persists `avoided_loss_kg` and `avoided_loss_kes`.
  - Test `test_alerts_api.py`: Verify role-based scoping (Operator sees only their hub; Administrator sees all), unread count, and multi-tier dispatch handling.
  - Test `test_simulator_api.py`: Verify start, status, and stop endpoints with auth enforcement.
- **Test Seam 2: Frontend Integration (`frontend/src/`)**:
  - Component tests with Vitest + React Testing Library:
    - Notification bell and drawer interaction.
    - Avoided loss card rendering on completed batch.
    - Translation verification for new alert and loss strings in English and Kiswahili.
- **Test Seam 3: Build & CI Verification**:
  - Full CI pipeline run executing backend, ML, simulator, and frontend test suites and Vite production bundle build.

## Out of Scope

- Real hardware telemetry (physical GSM/WiFi gateway flashing).
- Third-party carbon-credit accreditation or formal greenhouse gas registry audits.
- Live WhatsApp Business API (deferred per ADR-0001 / `docs/context.md`).
- Real farmer financial transactions or live M-Pesa integration.

## Further Notes

- All code adheres strictly to the canonical vocabulary in `GLOSSARY.md` (Batch, Hub, Reading, Advisory, Quality Grade, Operator, Administrator, Alert, Avoided Loss).
- Sourcing recipient phone numbers strictly from authenticated user accounts maintains compliance with Kenya's Data Protection Act 2019.

