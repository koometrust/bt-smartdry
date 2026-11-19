# Code Review — Milestone 3 Review-Fix Commit

**Commit:** `3568cf9` fix(review): address Milestone 3 standards and spec review findings  
**Fixed point:** `0a40371`  
**Reviewed:** 2026-11-18  
**Axes:** Standards (documented rules + smell baseline) · Spec (user stories + issue ACs)

---

## Standards

### `simulator/main.py`

**🔴 Hard violation — GLOSSARY.md: "Administrator / Avoid: admin"**

Default values introduced for `SIMULATOR_USERNAME` / `SIMULATOR_PASSWORD` are `"admin"` / `"adminpassword123"`:
```python
+SIMULATOR_USERNAME = os.getenv("SIMULATOR_USERNAME", "admin")
+SIMULATOR_PASSWORD = os.getenv("SIMULATOR_PASSWORD", "adminpassword123")
```
The GLOSSARY defines **Administrator** and explicitly commands *"Avoid: admin"*. The default string `"admin"` appears in source code (and in log output when the env var is unset), violating the vocabulary rule. The fix that was supposed to resolve the "Authenticates as Admin" bug now embeds the forbidden term as the fallback default.

---

### `frontend/src/pages/ActiveBatchesPage.tsx`

**🔴 Hard violation — `docs/context.md` Bilingual Frontend i18n**

Replacement empty-state string is hardcoded English, not routed through `react-i18next`:
```tsx
+  Click "+ New Batch" to load a harvest into the solar dryer.
```
Finding #4 was declared RESOLVED, but this hunk introduces a new hardcoded string in the same file.

**🟡 Judgement call — Primitive Obsession**

Capacity label inlines a magic constant and an untranslated fallback:
```tsx
{selectedHub?.name || 'Hub'} Dryer Capacity (200 kg)
```
`'Hub'` is not a translated string; `200 kg` is a magic constant inconsistent with the pattern used elsewhere.

---

### `frontend/src/pages/BatchHistoryPage.tsx`

**🔴 Hard violation — `docs/context.md` Bilingual Frontend i18n**

New table headers `"Batch / Crop"`, `"Harvest Weight"`, `"Times & Duration"`, and `"Target: {batch.target_moisture_pct}%"` are hardcoded English bypassing `react-i18next`. Other new columns were correctly added to both `en.json` and `sw.json`; these four were missed.

---

### `frontend/src/pages/BatchDetailPage.tsx`

**🔴 Hard violation — `docs/context.md` Bilingual Frontend i18n (surviving miss)**

```tsx
  Elapsed: {elapsedH}h {elapsedM}m
```
This hardcoded label is in a hunk the commit modifies, and was not addressed despite finding #4 being declared RESOLVED.

---

### `frontend/src/utils/formatters.ts` (new file)

**🟡 Judgement call — Speculative Generality**

`formatRemainingHours` returns `{ hours, minutes, formatted }` but all production callsites destructure only `formatted`. The `hours` and `minutes` fields go unused outside tests — returning a struct where a string suffices is YAGNI overhead.

**🟡 Judgement call — Duplicated Code (minor)**

`formatRemainingHours` and `formatBatchDuration` both implement the same `Math.floor` / `Math.round` hours-minutes arithmetic independently (~10 lines apart). A private `splitHoursMinutes(decimalHours)` helper would remove the duplication.

---

## Spec

### `simulator/main.py`

**🔴 Missing — Issue 05 AC: "authenticates using seed operator credentials"**

Credentials are now configurable, but the hardcoded *defaults* remain `"admin"` / `"adminpassword123"`. Out of the box — with no env override — the simulator still authenticates as the admin account, violating the AC. Structurally correct fix, incomplete execution.

**🔴 Missing — Issue 05 AC: "Handles batch completion when target moisture is reached"**

Removing the auto-`PATCH` was correct per `docs/context.md` (operator must confirm removal), but the simulator now has **no path whatsoever** to remove a batch from `self.batch_state` once moisture decays below the target. The batch remains in state forever and keeps generating sub-target readings, rather than halting simulation for that batch while awaiting operator action. The AC is unmet.

---

### `frontend/src/pages/BatchHistoryPage.tsx`

**🟡 Partial — Issue 03 AC: "Columns: Batch ID, Crop, Weight, Start/End times, Final Moisture, Final Quality Grade badge"**

Start and End times are merged into a combined "Times & Duration" cell alongside a duration string. The spec lists them as distinct required columns; the display is richer but diverges from the stated column structure.

---

### `frontend/src/utils/formatters.ts`

**🟡 Scope creep — `CROP_DEFAULT_TARGET_MOISTURE` exported but unused**

This constant is exported (not referenced anywhere in the diff) and was never requested. Dead exported surface area.

---

### `frontend/src/pages/ActiveBatchesPage.tsx`

**🟡 Scope creep — Empty-state "New Batch" shortcut button removed**

The original empty-state card included a shortcut `<Button>` to open the modal (removed in diff). No spec item requested its removal; this silently degrades discoverability for operators.

---

### `frontend/src/tests/authGuard.test.ts`

**🔴 Wrong — Issue 05 AC: "Frontend unit & component tests verifying authentication guards"**

`authGuard.test.ts` defines its own local `canAccessRoute` function that mirrors the guard logic, rather than importing and exercising the actual `ProtectedRoute` / `AuthContext`. The tests validate a reimplementation, not the real guard. A bug introduced into `ProtectedRoute.tsx` would not be caught by these tests.

---

### `frontend/src/pages/ActiveBatchesPage.tsx`

**🔴 Wrong — `spec.md` L34: "react-i18next with English and Kiswahili translations covering all labels"**

The remaining-time display branch hardcodes English:
```tsx
'Target reached'
```
instead of `t('...')`. All surrounding sensor labels were internationalized but this string was missed.

---

## Summary

| Axis | Hard violations | Judgement calls | Worst issue |
|------|----------------|-----------------|-------------|
| Standards | 4 | 3 | Bilingual i18n misses in 3 files (surviving from the finding declared RESOLVED) |
| Spec | 4 | 3 | Simulator batch-completion handling is fully broken — batches never leave `batch_state` after moisture decays below target |
