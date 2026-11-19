# 06: Fix simulator default credentials to use seed Operator account

**What to build:** The simulator should authenticate out-of-the-box as a seeded Operator, not as the Administrator. When no environment variables are set, the simulator logs in with the Operator username and password that the seed script creates, so a developer running the simulator against a fresh database gets Operator-scoped behaviour by default.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] The default value for `SIMULATOR_USERNAME` env var matches the username of a seeded Operator account (as defined in the seed script), not the Administrator account
- [x] The default value for `SIMULATOR_PASSWORD` env var matches that seeded Operator's password
- [x] The string literal `"admin"` does not appear as a default credential value anywhere in the simulator source or its log output
- [x] The simulator still accepts override credentials via `SIMULATOR_USERNAME` / `SIMULATOR_PASSWORD` env vars
- [x] Existing simulator tests pass with the new defaults

