# Milestone 3 Code Review Report

Conducted across two parallel axes (**Standards** and **Spec**) against merge base `f4bb91e...HEAD`.

---

## Standards Axis

### (a) Documented Standards Violations (Hard Violations)

1. **`docs/context.md` (Batch Lifecycle & Operator Action) & `GLOSSARY.md` (Over-drying)**
   - **File:** `simulator/main.py:229-234`
   - **Violation:** The simulator automatically marks batches completed via `PATCH /api/v1/batches/{id}` with `{"status": "completed"}` when `new_m <= target_m`. `docs/context.md` explicitly specifies: *"Batch states: active (drying) and completed (operator confirmed removal). Transition is an explicit operator action."* Auto-completing circumvents the operator removal action and prevents over-drying from ever occurring or being alerted.

2. **`docs/adr/0002-multi-batch-per-dryer.md` (Per-Dryer Capacity Modeling)**
   - **File:** `frontend/src/pages/ActiveBatchesPage.tsx:78-81, 148`
   - **Violation:** ADR-0002 dictates that each hub has one physical 200 kg dryer. When an Administrator views "All Hubs" (`selectedHubId === ''`), `currentLoadedWeight` sums batch weights across all hubs and passes it to a single 200 kg `CapacityMeter`, erroneously conflating three separate regional dryers into one.

3. **`GLOSSARY.md` (Language & Avoid Vocabulary)**
   - **Files:** `frontend/src/i18n/locales/en.json:15`, `frontend/src/components/Navbar.tsx:88`
     - **Violation:** `GLOSSARY.md` defines **Administrator** and commands: *"Avoid: admin, superuser, manager"*. UI displays `"Admin"`.
   - **Files:** `frontend/src/pages/AnalyticsPage.tsx:131`, `frontend/src/i18n/locales/en.json:93`
     - **Violation:** `GLOSSARY.md` defines **Dryer Capacity** and commands: *"Avoid: limit, maximum load"*. Code uses `"Dryer Capacity Limit"` and `"(200 kg limit per dryer)"`.

4. **`docs/context.md` (Bilingual Frontend i18n)**
   - **Files:** `frontend/src/pages/AnalyticsPage.tsx:75-150`, `frontend/src/pages/BatchDetailPage.tsx:213-236`, `frontend/src/components/CreateBatchModal.tsx:50-58`
   - **Violation:** Hardcoded English strings (KPI card titles, sensor labels like "Dryer Temp", modal validation errors) bypass `react-i18next`, breaking bilingual requirements.

### (b) Baseline Code Smells (Judgement Calls)

1. **Primitive Obsession** (`frontend/src/types/index.ts:21, 28`)
   - `Batch.crop_type` and `Hub.location` are typed as `string` instead of using the domain unions `CropType` and `HubLocation`.
2. **Data Clumps** (`frontend/src/types/index.ts`, `CreateBatchModal.tsx:16-21`, `client.ts:50`)
   - `{ hub_id, crop_type, initial_weight_kg, target_moisture_pct }` is re-declared inline across modal, API client, and pages without a named `CreateBatchDTO`.
3. **Duplicated Code** (`BatchDetailPage.tsx:68-69` vs `ActiveBatchesPage.tsx:218-219`)
   - Remaining hours/minutes extraction logic (`Math.floor(remHours)` and `Math.round((remHours - h) * 60)`) is copy-pasted across pages.
4. **Feature Envy** (`frontend/src/pages/ActiveBatchesPage.tsx:78-81`)
   - Page logic manually calculates hub capacity utilization over batches instead of delegating to a hub helper, causing the multi-hub aggregation bug.

---

## Spec Axis

### (a) Missing or Partial Requirements

1. **Batch History Hub Filter, Start Time/Duration, and Search**:
   - **Spec quote:** `"Displays table/list of completed batches with filters by crop type, hub location, and quality grade."`, `"Columns: Batch ID, Crop, Weight, Start/End times, Final Moisture, and Final Quality Grade badge."`, and `"Search and filter support."` (`issues/04-history-hub-overview-and-analytics.md` L12–14; `spec.md` L18).
   - **Finding:** `BatchHistoryPage.tsx` omits the hub location filter (only crop & grade exist), start time and batch duration columns (only completed date is shown), and free-text search.
2. **Comparative Hub Performance in Analytics**:
   - **Spec quote:** `"Analytics dashboard displaying crop distribution, quality grade breakdown, and comparative hub performance."` (`spec.md` L20; `issues/04...` L4).
   - **Finding:** `AnalyticsPage.tsx` displays KPI cards, grade ratios, and crop throughput, but completely lacks comparative hub performance metrics or regional hub charts.
3. **Active Hub Indicator in Navbar**:
   - **Spec quote:** `"Build responsive Navigation bar with language switcher (English/Kiswahili), user profile badge, active hub indicator, and logout button."` (`issues/02...` L14).
   - **Finding:** `Navbar.tsx` displays username and role badge, but omits the active/assigned hub indicator.
4. **Auth Guard & Batch Card Unit Tests**:
   - **Spec quote:** `"Frontend unit & component tests verifying authentication guards, i18n translation rendering, capacity calculator, and batch cards."` (`issues/05...` L11).
   - **Finding:** Only `capacity.test.ts` and `i18n.test.ts` exist; route guard and batch card component tests were omitted.

### (b) Behaviour Not Asked For (Scope Creep)

1. **shadcn/ui & Radix UI Primitives Integration**:
   - **Spec quote:** `"Tailwind CSS for responsive styling, dark/light contrast suitable for low-cost Android displays."` (`spec.md` L32).
   - **Finding:** Commit `e81e8ce` introduced `@radix-ui` dependencies, `components.json`, and 7 shadcn/ui components (`src/components/ui/*`), which was not requested in the originating spec (though requested by user in chat).

### (c) Requirements Implemented Buggy or Wrong

1. **Dryer Capacity Check in Batch Creation**:
   - **Spec quote:** `"'New Batch' modal with validation: crop type selection, weight input with real-time remaining capacity check against 200 kg limit"` (`issues/03...` L15).
   - **Bug:** In `ActiveBatchesPage.tsx:78-81`, `currentLoadedWeight` sums batches across *all* hubs when unfiltered. In `CreateBatchModal.tsx:44`, `availableWeight` is static and does not recompute when changing hubs in the dropdown, blocking batch creation if aggregate cross-hub weight exceeds 200kg.
2. **Hardcoded Moisture Baseline for Progress Bar**:
   - **Spec quote:** `"Cards display ... and progress bar towards target moisture."` (`issues/03...` L14).
   - **Bug:** `ActiveBatchesPage.tsx:188` hardcodes initial moisture to `75%` (`(75 - currM)/(75 - targetM)`), skewing progress calculations for Prunus (~60% initial moisture).
3. **Simulator Authenticates as Admin**:
   - **Spec quote:** `"authenticates using seed operator credentials"` (`issues/01...` L12; `spec.md` L28).
   - **Bug:** `simulator/main.py:81` logs in as `admin` instead of operator credentials.

---

## Summary
- **Standards:** 8 findings (worst: auto-completing batches in simulator circumvents operator removal action required in `docs/context.md` and ADR-0002 multi-hub capacity conflation).
- **Spec:** 8 findings (worst: static multi-hub capacity aggregation blocking batch creation in `CreateBatchModal`).
