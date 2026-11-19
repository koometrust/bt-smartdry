# 10: (wontfix) Auth guard tests exercise a reimplementation, not the real ProtectedRoute

**What to build:** N/A — deferred.

**Blocked by:** None

**Status:** wontfix

## Context

`authGuard.test.ts` defines a local `canAccessRoute` function that mirrors the real route guard logic and tests that, rather than importing and exercising `ProtectedRoute` / `AuthContext` from the application. A bug introduced into the real guard would not be caught.

## Why wontfix for now

The real `ProtectedRoute` behaviour is verified end-to-end by the running application and manual testing. Improving the test coverage is worthwhile but not a correctness blocker for the supervisor demo. Revisit when a dedicated frontend testing pass is scoped.

## Comments

Deferred by decision on 2026-11-19. Re-open and label `ready-for-agent` when addressing frontend test quality as a standalone effort.

