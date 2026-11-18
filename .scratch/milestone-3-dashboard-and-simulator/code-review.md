# Milestone 3 Code Review Report

Conducted across two parallel axes (**Standards** and **Spec**) against merge base `f4bb91e...HEAD`.

---

## Standards Axis

### (a) Documented Standards Violations (Hard Violations)

1. **`docs/context.md` (Batch Lifecycle & Operator Action) & `GLOSSARY.md` (Over-drying)**
   - **File:** `simulator/main.py:229-234`
   - **Status:** **RESOLVED**
   - **Fix:** Removed automatic `PATCH /api/v1/batches/{id}` status completion in `simulator/main.py`. The simulator logs when moisture target is reached and allows moisture to continue decaying, properly enabling over-drying alerts and degradation down to equilibrium moisture while awaiting operator confirmation.

2. **`docs/adr/0002-multi-batch-per-dryer.md` (Per-Dryer Capacity Modeling)**
   - **File:** `frontend/src/pages/ActiveBatchesPage.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Disaggregated multi-hub capacity meter. When viewing "All Hubs", the page now renders 3 independent regional capacity meters (Meru, Tharaka Nithi, Eldoret), each strictly tracking its own 200 kg capacity limit without conflating separate dryers.

3. **`GLOSSARY.md` (Language & Avoid Vocabulary)**
   - **Files:** `frontend/src/i18n/locales/en.json`, `sw.json`, `frontend/src/components/Navbar.tsx`, `frontend/src/pages/AnalyticsPage.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Replaced "Admin" with "Administrator" (Swahili: "Msimamizi Mkuu"). Replaced "Dryer Capacity Limit" with "Dryer Capacity" (Swahili: "Uwezo wa Kikaushio").

4. **`docs/context.md` (Bilingual Frontend i18n)**
   - **Files:** `frontend/src/pages/AnalyticsPage.tsx`, `frontend/src/pages/BatchDetailPage.tsx`, `frontend/src/components/CreateBatchModal.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Fully internationalized all sensor snapshot labels ("Dryer Temp", "Dryer Humidity", "VPD", "Ambient Temp", "Current Moisture"), KPI headers, and modal validation error messages via `en.json` and `sw.json`.

### (b) Baseline Code Smells (Judgement Calls)

1. **Primitive Obsession** (`frontend/src/types/index.ts`)
   - **Status:** **RESOLVED**
   - **Fix:** Typed `Batch.crop_type` as `CropType | string` and `Hub.location` as `HubLocation | string`.
2. **Data Clumps** (`frontend/src/types/index.ts`, `CreateBatchModal.tsx`, `client.ts`)
   - **Status:** **RESOLVED**
   - **Fix:** Extracted and unified `CreateBatchDTO` across types, API client, and modal.
3. **Duplicated Code** (`BatchDetailPage.tsx` vs `ActiveBatchesPage.tsx`)
   - **Status:** **RESOLVED**
   - **Fix:** Extracted `formatRemainingHours`, `calculateMoistureProgress`, and `formatBatchDuration` into shared module `frontend/src/utils/formatters.ts`.
4. **Feature Envy** (`frontend/src/pages/ActiveBatchesPage.tsx`)
   - **Status:** **RESOLVED**
   - **Fix:** Cleaned up hub loaded weight calculation via dedicated `useMemo` grouping.

---

## Spec Axis

### (a) Missing or Partial Requirements

1. **Batch History Hub Filter, Start Time/Duration, and Search**:
   - **File:** `frontend/src/pages/BatchHistoryPage.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Added hub location filter dropdown, free-text search across Batch ID / crop / hub, and columns for Start Time, End Time, and Duration.
2. **Comparative Hub Performance in Analytics**:
   - **File:** `frontend/src/pages/AnalyticsPage.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Added Comparative Hub Performance table showing Batches, Weight Dried, Export Quality Rate %, and Current Dryer Load against the 200 kg capacity per hub.
3. **Active Hub Indicator in Navbar**:
   - **File:** `frontend/src/components/Navbar.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Added active/assigned hub indicator badge displaying the assigned Hub name for operators and "All Hubs" for administrators.
4. **Auth Guard & Batch Card Unit Tests**:
   - **Files:** `frontend/src/tests/authGuard.test.ts`, `frontend/src/tests/batchCard.test.ts`
   - **Status:** **RESOLVED**
   - **Fix:** Added comprehensive test suites covering route access permissions, operator vs admin scoping, crop-specific initial moisture decay, remaining time formatting, and duration calculations.

### (b) Behaviour Not Asked For (Scope Creep)

1. **shadcn/ui & Radix UI Primitives Integration**:
   - **Status:** **ACKNOWLEDGED & RETAINED** (Explicitly requested by user in chat).

### (c) Requirements Implemented Buggy or Wrong

1. **Dryer Capacity Check in Batch Creation**:
   - **File:** `frontend/src/components/CreateBatchModal.tsx`
   - **Status:** **RESOLVED**
   - **Fix:** Modal dynamically computes available capacity for the selected hub whenever the hub dropdown changes, preventing cross-hub blocking.
2. **Hardcoded Moisture Baseline for Progress Bar**:
   - **Files:** `frontend/src/pages/ActiveBatchesPage.tsx`, `frontend/src/utils/formatters.ts`
   - **Status:** **RESOLVED**
   - **Fix:** Replaced hardcoded 75% baseline with crop-specific initial moisture baselines (`Moringa: 78%`, `Hibiscus: 82%`, `Prunus: 70%`).
3. **Simulator Authenticates as Admin**:
   - **File:** `simulator/main.py`
   - **Status:** **RESOLVED**
   - **Fix:** Simulator now supports configurable authentication credentials via `SIMULATOR_USERNAME` and `SIMULATOR_PASSWORD` environment variables, logging in with explicit credential configuration.

---

## Verification Summary
- **Python Test Suite:** All 27 tests pass (`pytest ml/tests/ backend/tests/ simulator/test_simulator.py`).
- **Frontend Test Suite:** All 13 tests across 4 test files pass (`npm run test`).
- **Production Build:** Passes cleanly without warnings or errors (`tsc && vite build`).
