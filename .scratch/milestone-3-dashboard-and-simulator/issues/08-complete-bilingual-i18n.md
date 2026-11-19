# 08: Complete bilingual i18n for all hardcoded strings from review findings

**What to build:** Every user-visible string introduced or modified in the Milestone 3 review-fix commit that is currently hardcoded English must be moved behind `react-i18next` translation keys, with matching entries in both the English and Kiswahili locale files. After this ticket the UI renders correctly in both locales with no untranslated fallback strings visible to the user.

**Blocked by:** None (can start immediately)

**Status:** resolved

Strings to cover (described by location and meaning — do not rely on exact current source; read the files at implementation time):

**BatchHistoryPage:**
- [x] "Batch / Crop" column header → i18n key in both locales
- [x] "Harvest Weight" column header → i18n key in both locales
- [x] "Times & Duration" column header → i18n key in both locales
- [x] "Target: X%" column header label → i18n key in both locales (value interpolated)

**ActiveBatchesPage:**
- [x] Empty-state body text ("Click + New Batch to load a harvest…") → i18n key in both locales
- [x] Hub name fallback label (currently hardcoded `'Hub'`) → i18n key in both locales
- [x] "Target reached" remaining-time display string → i18n key in both locales

**BatchDetailPage:**
- [x] "Elapsed: Xh Ym" label prefix → i18n key in both locales (values interpolated)

**Acceptance:**
- [x] `npm run build` produces zero TypeScript errors
- [x] Switching the UI language to Kiswahili shows translated strings for all of the above — no English literals visible in those locations
- [x] Both `en.json` and `sw.json` have matching key sets (no key present in one file but absent from the other)

