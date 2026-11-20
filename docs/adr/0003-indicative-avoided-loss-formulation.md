# Indicative avoided-loss formulation instead of dynamic chemical or carbon-credit modeling

The proposal identified Objective 6 (avoided-post-harvest-loss estimator) as a time-permitting addition. We implement this as an indicative, deterministic engineering formulation calibrated to published Kenyan horticultural post-harvest loss baselines, rather than dynamic biochemical modeling or a certified carbon-offset methodology.

Open-air sun drying in Kenya suffers severe spoilage, mold, dust contamination, and insect infestation, typically losing 30% to 40% of harvest mass. Controlled solar drying in BT-SmartDry reduces physical loss to 4% to 6%. When an operator marks a batch as completed, the system calculates and persists:
1. Physical biomass preserved: `kg_saved = initial_weight_kg * (baseline_loss_rate - smartdry_loss_rate)`
2. Indicative economic value: `kes_saved = kg_saved * market_price_per_kg * grade_multiplier`

Quality Grade directly modulates value realization: Export batches achieve 100% market price, Standard batches receive 90%, and Downgraded batches (e.g. from over-drying or under-drying) receive 50%. The UI and analytics explicitly label these values as: *"Indicative post-harvest metric; non-certified carbon or agronomic claim"*.

**Considered alternatives:**
- **Dynamic biochemical/spoilage simulation based on reading curves:** would require empirical microbiological decay models per crop that cannot be validated without wet-lab physical testing. Rejected as unfeasible and unnecessary for an indicative capstone target.
- **Formal carbon-credit greenhouse gas avoidance accounting:** requires accredited third-party methodologies (e.g. Gold Standard / Verra) and regional grid displacement factors. Out of scope per the project brief.
- **Computing avoided loss on-the-fly without database persistence:** would require recalculating over thousands of batch rows during every analytics dashboard query. Persisting `avoided_loss_kg` and `avoided_loss_kes` upon batch completion enables simple, instantaneous SQL indexing and aggregations.

