# 07: Halt simulator telemetry when batch moisture reaches target

**What to build:** Once a batch's simulated moisture decays to or below its target, the simulator stops emitting telemetry readings for that batch and logs that it is awaiting operator removal. The batch is not automatically completed — the operator must confirm removal via the UI — but the simulator does not keep generating sub-target readings indefinitely. If the operator never acts, the batch stays dormant in the simulator's state; it does not produce zombie readings.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] When a batch's current moisture falls at or below `target_moisture_pct`, the simulator stops scheduling further telemetry ticks for that batch
- [x] The simulator logs a clear message indicating the batch has reached its target and is awaiting operator removal (uses the vocabulary from GLOSSARY.md: "Operator", "Advisory", not "user" or "notification")
- [x] The batch entry is NOT removed from simulator state automatically — it remains so the simulator can resume if the operator removes and re-adds it
- [x] Other active batches continue receiving telemetry unaffected
- [x] A simulator integration test confirms: given a batch seeded at moisture just above target with a fast decay rate, telemetry stops after the threshold crossing and no further readings are emitted

