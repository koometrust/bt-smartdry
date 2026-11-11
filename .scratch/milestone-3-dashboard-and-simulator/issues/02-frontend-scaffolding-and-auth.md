# 02: Frontend Scaffolding, i18n & Authentication

**What to build:**
Scaffold the modern React frontend application in `frontend/` using Vite, TypeScript, and Tailwind CSS. Implement bilingual internationalization (`react-i18next`) supporting English and Kiswahili, JWT authentication management, API client configuration, navigation shell, and the responsive Login view with quick-fill test account presets.

**Blocked by:** None (can start immediately)

**Status:** resolved

## Acceptance Criteria
- [x] Initialize `frontend/` with Vite, React 18+, TypeScript, Tailwind CSS, TanStack React Query, Lucide icons, and `react-i18next`.
- [x] Configure `react-i18next` with complete English and Kiswahili locale translation dictionaries covering navigation, forms, grades, crops, and advisory statuses.
- [x] Build global Auth Context / store managing JWT token in `localStorage`, user profile state (role, hub_id, preferred language), and automatic Axios/fetch Bearer authorization headers.
- [x] Build responsive Navigation bar with language switcher (English/Kiswahili), user profile badge, active hub indicator, and logout button.
- [x] Build the `/login` page with accessible form inputs, error handling, and one-click quick-fill buttons for demo credentials (Admin and 3 Hub Operators).
- [x] Implement Route Guards restricting admin-only routes (`/hubs`, `/analytics`) from operator access and redirecting unauthenticated users to `/login`.

## Comments
- Scaffolded Vite + React 18 + TypeScript + Tailwind CSS application in `frontend/`.
- Configured bilingual `react-i18next` with full English (`locales/en.json`) and Kiswahili (`locales/sw.json`) parity.
- Implemented `AuthContext.tsx` with JWT persistence, user profile caching, and automatic language synchronization.
- Implemented `Navbar.tsx` with mobile menu, language toggle, and role badges.
- Implemented `LoginPage.tsx` with one-click quick presets for demo operator and admin accounts.
- Added comprehensive unit tests in `src/tests/i18n.test.ts` verifying translation key parity; 100% pass.
