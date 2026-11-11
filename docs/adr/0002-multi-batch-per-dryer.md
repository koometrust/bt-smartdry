# Multiple concurrent batches per dryer

Each hub has one physical dryer, but operators routinely load multiple crops at the same time when a single crop doesn't fill the 200 kg capacity. We model this as multiple concurrent batches per dryer rather than one batch per dryer.

Each batch is a single crop type with its own weight, moisture trajectory, predictions, and alerts. The dryer's ambient conditions (temperature, humidity, VPD) are shared across all batches at a given timestamp; per-batch readings duplicate the ambient fields for query simplicity. A new batch is allowed only if the sum of active batch weights plus the new weight does not exceed the dryer's capacity. When a batch is completed and removed, its weight is freed.

This enables the key use case: staggered removal alerts. Moringa dries faster than hibiscus, so the operator is told "remove moringa now" while hibiscus keeps drying. The "remove now" alert is time-critical because over-drying degrades quality grade.

**Considered alternatives:**
- **One batch per dryer (simpler):** would force operators to dry only one crop at a time, which doesn't match real usage. The downstream complexity (capacity checking, per-batch readings) is modest.
- **Dryer-level readings + batch-level readings in separate tables:** cleaner normalisation, but adds join complexity for every query. Duplicating ambient fields per-batch is a few extra floats per row on a ~200K-row table.

