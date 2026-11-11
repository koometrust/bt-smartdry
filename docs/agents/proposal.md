# BT-SmartDry: Proposal Brief

Condensed from the full final-year proposal. Source of truth for scope, targets and constraints. Decisions made later in grilling go in `docs/context.md` and ADRs, and override this file where they conflict.

## 1. What it is
An AI monitoring and advisory system for Botanic Treasures' IoT smart solar dryers (3 women-led hubs: Meru, Tharaka Nithi, Eldoret; crops: moringa, prunus, seamoss-adjacent botanicals).

It does two things the dryers don't do today:
1. **Predicts** remaining drying time and final quality grade from sensor readings.
2. **Explains** results to hub operators in plain English and Kiswahili, via a web dashboard and an SMS/WhatsApp fallback (for operators without reliable smartphone data).

Operators are semi-technical, so output must read as an instruction ("what to do next"), not a number.

## 2. Objectives and measurable targets
| # | Objective | Target |
|---|---|---|
| 1 | IoT ingestion pipeline plus operator dashboard showing live batch status | Working end to end |
| 2 | Drying-time regression (XGBoost, LightGBM as alternative) | **R² ≥ 0.85** on held-out test set |
| 3 | Quality-grade classifier (export / standard / downgraded) | **≥ 80% accuracy** on held-out test set |
| 4 | LLM advisory in English and Kiswahili | **≥ 80% operator comprehension** (testers restate the action correctly) |
| 5 | Deploy on free-tier cloud with CI/CD | Public URL reachable |
| 6 | *Time-permitting:* indicative avoided-post-harvest-loss estimator | Non-registered, not a carbon-credit claim |

The 0.85 target is deliberately conservative: published lab results hit 0.99 on single-crop, stable conditions, while this dataset spans 3 crops and 3 hubs under variable weather.

## 3. Key decisions (already made)
- **Data is synthetic**, generated in code, about **2,000 batch records**. It is calibrated to real dryer sizes, hubs and crop mix, and to published benchmarks (for example a 2-to-3-day drying window, a 25-to-45% loss reduction range). Reported accuracy describes simulated data only, and the report must say so.
- **Fields:** temperature, humidity, vapour pressure difference, crop type, batch weight, hub location, weather forecast variables; outputs are drying time, final moisture, quality grade.
- **Models:** gradient-boosted regressor for time. For grade, Random Forest or a gradient-boosted classifier, whichever wins on the validation split. 80/20 split with 5-fold CV. Check class balance and use resampling or class weights if needed.
- **LLM is for text only**, never for regression on sensor data. Use a small open-source instruction-tuned model via Hugging Face (LoRA fine-tune on author-written example advisories, or structured prompting if compute is a problem).
- **Evaluate the advisory by comprehension testing**, not BLEU: 3 to 5 outside testers, ideally including a hub operator, who restate the recommended action.
- **Stack:** React + Tailwind (dashboard, mobile-first, low-bandwidth); FastAPI (API); Python ML and LLM services; PostgreSQL; Africa's Talking (SMS) and WhatsApp Business API sandbox.
- **Hosting:** Render free tier (Supabase as DB fallback); GitHub Actions for CI/CD; about KES 500 total (live SMS credit).
- **Process:** Agile, 2-week sprints. Backend, DB and dashboard shell first so a demo exists before the ML is done.

## 4. Architecture and data flow
Components: IoT sensors → hub gateway/edge cache → FastAPI backend + PostgreSQL → ML prediction service → LLM advisory service → dashboard and SMS/WhatsApp.

Flow: operator starts batch → sensors log at an interval → API stores readings → ML loads latest batch features → prediction (time to dry, grade) saved → LLM turns it into a plain-language message → dashboard updates; SMS/WhatsApp alert sent when a threshold is crossed (for example batch nearing completion).

## 5. Scope
- **In:** working prototype, 25 weeks, Kenya only, two roles (hub operator, administrator/founder-operator), two prediction problems, bilingual advisory, alerts, deployment.
- **Out:** production security audit, formal carbon-credit registration, live payments/banking/government integration, use of real farmer or operator data.

## 6. Hard constraints (affect the code)
- **No real personal data.** Synthetic only. No farmer names, contacts or finances in the system.
- Test-account passwords hashed with **bcrypt**; all traffic over **HTTPS**.
- Tester phone numbers for SMS/WhatsApp sandboxes are stored only during testing, then deleted.
- **Advisory output is a draft for review, not unsupervised agronomic advice** (LLM hallucination risk).
- **Fairness check:** compare predicted time and grade distributions across crop and hub; flag any subgroup with systematically worse predictions. Spot-check English vs Kiswahili message quality for parity.
- **Accessibility:** sufficient colour contrast, text labels not colour alone, responsive layout for small low-cost Android screens.
- Check the chosen LLM's licence allows fine-tuning and redistributing adapted weights. List all packages with versions in `requirements.txt` / `package.json`. Cite any copied code.
- Data Protection Act 2019 applies to anything personal collected incidentally (testers' phone numbers).

## 7. Testing
PyTest (backend and ML), a Postman collection for the full flow (batch registration to advisory delivery), and usability testing in week 20.

## 8. Schedule (25 weeks; proposal phase done)
| Weeks | Deliverable |
|---|---|
| 5-6 | Backend API, DB schema, batch/hub CRUD |
| 7-8 | React dashboard shell (hub view, batch list, live status) |
| 9-10 | Synthetic dataset generator |
| 11-12 | Train and evaluate models; **MVP: prediction end to end** |
| 13 | Mid-project demo; decide if Objective 6 is still realistic |
| 14-15 | LLM advisory (English/Kiswahili) in dashboard |
| 16-17 | SMS/WhatsApp alerts |
| 18-19 | Avoided-loss estimator (if on schedule) |
| 20 | Usability/comprehension testing |
| 21-22 | Fixes, CI/CD, load/latency testing; **feature-complete** |
| 23-24 | Report draft, final integration, defense rehearsal |
| 25 | Final submission and defense |

## 9. Open questions to settle in the first grilling session
*(My additions, not from the proposal.)*
- The proposal says inference runs **at the hub** with periodic cloud sync, but the architecture and budget host everything on Render. Which is it for the prototype?
- Do real sensors feed the system during the capstone, or only a simulated device script? (Data is synthetic, but the sensors exist.)
- Which small LLM, and is there enough Colab GPU time for a LoRA fine-tune?
- Who writes the Kiswahili example advisories, and who checks their quality?
- What counts as "early-batch readings" for predicting remaining time?
