# 09: Remove "admin" string literal from simulator source and logs

**What to build:** After ticket 06 replaces the default credentials with Operator values, this ticket does a final sweep to confirm the forbidden term "admin" (per GLOSSARY.md vocabulary rule: use "Administrator", avoid "admin") does not appear anywhere in simulator source as a string literal, default value, or log message. This is a narrow vocabulary-compliance sweep, not a functional change.

**Blocked by:** 06 — simulator-operator-credentials (must replace the default value first)

**Status:** resolved

- [x] A grep of the simulator source for the string `"admin"` (case-insensitive, as a string literal or default) returns no hits related to credentials or role names
- [x] Log messages emitted by the simulator that refer to the authenticated account use "Operator" or the actual username, not "admin"
- [x] No regression in simulator startup or authentication behaviour
- [x] `pytest simulator/` passes

