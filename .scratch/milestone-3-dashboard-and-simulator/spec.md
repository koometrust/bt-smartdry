# Milestone 3 Spec: Telemetry Simulator & React Operator/Admin Dashboard

## Problem Statement
Hub operators and central administrators need a real-time, responsive, bilingual monitoring interface and a continuous stream of IoT sensor data to observe solar dryer conditions, view embedded ML predictions (remaining drying time and quality grade), receive bilingual advisories, and manage batches without needing manual hardware intervention during testing and evaluation.

## Solution
Build the simulated IoT telemetry runner (`simulator/`) and the full-featured, mobile-first React dashboard (`frontend/`) in accordance with `docs/context.md` and the system architecture:
1. A multi-batch, multi-hub Python simulator generating physically coherent sensor readings and streaming them via REST API.
2. A Vite + React + TypeScript + Tailwind CSS dashboard with 6 pages, bilingual i18n (English and Kiswahili via `react-i18next`), React Query polling every 30 seconds, role-based access control (Operator hub-scoped vs Admin multi-hub), and responsive visualizations for mobile/desktop.

## User Stories
1. As an operator or admin, I want to log in using my credentials so that my session is authenticated and scoped to my assigned hub role.
2. As an operator, I want to switch between English and Kiswahili on any page so that instructions and advisories match my language preference.
3. As an operator, I want to view active batches for my dryer hub so that I can monitor current moisture levels, estimated drying hours remaining, and predicted quality grade.
4. As an operator, I want to create a new drying batch (crop type, initial weight up to 200kg hub capacity, target moisture) so that the dryer can accept fresh harvest batches.
5. As an operator, I want to view detailed batch progress including interactive sensor curves (temperature, humidity, moisture over time) and clear bilingual advisories on what action to take next.
6. As an operator, I want to mark a batch as completed when drying finishes so that the capacity is released and final quality grade is recorded.
7. As an operator or admin, I want to inspect historical batches with their final grades, durations, and moisture metrics.
8. As an administrator, I want to view the Hub Overview across Meru, Tharaka Nithi, and Eldoret, showing real-time capacity utilization against the 200kg limit per dryer.
9. As an administrator, I want an Analytics dashboard displaying crop distribution, quality grade breakdown, and comparative hub performance.
10. As a tester or demo presenter, I want a Python simulator that continuously feeds live sensor readings for multiple batches across hubs at configurable intervals (from 5 minutes down to 1 second) to simulate days of drying in minutes.

## Implementation Decisions
- **Simulator (`simulator/`)**:
  - Python process using `httpx` and `pydantic`.
  - Generates realistic diurnal fluctuations and thin-layer exponential moisture decay using shared physical formulas consistent with `ml/synthetic/physics.py`.
  - Configurable interval via `SIMULATOR_INTERVAL_SECONDS` (default 5s for demo, up to 300s).
  - Automatically provisions test batches via `/api/v1/batches/` using operator credentials if none exist, then streams readings to `/api/v1/readings/`.
  - Supports concurrent batches across Meru, Tharaka Nithi, and Eldoret.
- **Frontend (`frontend/`)**:
  - React 18 / 19 + TypeScript + Vite.
  - Tailwind CSS for responsive styling, dark/light contrast suitable for low-cost Android displays.
  - TanStack Query (React Query) configured with `refetchInterval: 30000` (30s polling, no WebSockets per `docs/context.md`).
  - `react-i18next` with English (`locales/en.json`) and Kiswahili (`locales/sw.json`) translations covering all labels, actions, grades, and agronomic advisories.
  - Charting via lightweight SVG / Canvas (Recharts or Chart.js / custom responsive SVG charts) avoiding heavy client bundles.
  - JWT Auth store in `localStorage` with Bearer tokens attached to all API requests.
  - 6 routes:
    1. `/login`: Authentication form with quick-fill buttons for pre-seeded test accounts.
    2. `/`: Active Batches list with hub filter (for admin) and quick-create batch modal.
    3. `/batches/:id`: Batch Detail with sensor chart, prediction card, advisory card, and complete batch button.
    4. `/history`: Completed Batches table with filters and quality badges.
    5. `/hubs`: Hub Overview (Admin only) showing capacity meters (out of 200 kg) and active batch counters.
    6. `/analytics`: Analytics dashboard (Admin only) with historical throughput, grade distribution, and hub charts.

## Testing Decisions
- Simulator: Unit tests verifying physics integration, batch registration, reading payload conformity, and API resilience.
- Frontend: Automated tests (Vitest / React Testing Library or Node verification) verifying authentication handling, role guards, i18n translation completeness, capacity checks, and component rendering.
- Integration: Verification of end-to-end telemetry flow from simulator to backend to frontend API endpoints.

## Out of Scope
- Real hardware sensor wiring or physical gateway flashing (simulated only).
- WebSockets or Server-Sent Events (explicitly polled via React Query per `docs/context.md`).
- Third-party payment / banking integrations.

