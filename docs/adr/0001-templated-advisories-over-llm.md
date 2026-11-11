# Templated advisories instead of LLM-generated text

The proposal specified an LLM (small open-source model, LoRA fine-tuned or few-shot prompted) to turn ML predictions into plain-language operator advisories in English and Kiswahili. We decided to use bilingual template strings with variable slots instead.

The advisory messages are structurally simple — they report a predicted time, a grade, or an anomaly and tell the operator what to do. An LLM adds latency, inference cost, hallucination risk, and a GPU/API dependency for what amounts to string formatting. Templates are deterministic, instantly bilingual (the author writes both versions), and eliminate the risk of the model producing unsafe agronomic advice. The ML predictions (XGBoost regressor, gradient-boosted classifier) remain the substantive AI contribution; the advisory layer is a delivery mechanism, not a prediction.

**Considered alternatives:**
- **LLM for all advisories (proposal default):** more natural variation, but operator messages must be precise and actionable — variation is a liability, not a feature.
- **Templates for core alerts, LLM for optional "explain more":** adds the LLM as a non-critical-path feature. Rejected for scope: the comprehension test validates the templates, and the optional button adds integration work for marginal demo value.

