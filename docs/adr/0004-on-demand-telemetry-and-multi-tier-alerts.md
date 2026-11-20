# On-demand telemetry control and multi-tier alert dispatch

Deploying BT-SmartDry to cloud infrastructure (Render free tier and Supabase) introduces strict resource limits: Render free-tier web instances provide 750 monthly compute hours and spin down after 15 minutes of idle time. Running the multi-hub IoT telemetry simulator as a continuous 24/7 background worker would rapidly exhaust free instance hours and prevent the web dashboard from remaining accessible.

We resolve this by:
1. **On-demand cloud simulator:** Telemetry streaming is controlled via authenticated API endpoints (`POST /api/v1/simulator/start` and `POST /api/v1/simulator/stop`) and a CLI script. During demonstrations and testing, live streaming can be triggered on demand without continuous resource consumption.
2. **Three-tier alert dispatch (`SMS_PROVIDER_MODE=mock|sandbox|live`):**
   - `mock`: Logs SMS alerts directly to the database and backend console without external network requests (used in local development and GitHub Actions CI).
   - `sandbox`: Dispatches alerts through Africa's Talking Sandbox simulator for API payload verification.
   - `live`: Dispatches real SMS over cellular networks using pre-allocated airtime credit (KES 500) to verified recipient phone numbers during defense rehearsals and the final capstone presentation.

In addition, an in-dashboard Alert History page (`/alerts`) and a header notification bell drawer provide real-time visibility into all triggered alerts for Operators and Administrators, ensuring evaluators can verify alert generation without relying exclusively on physical mobile handsets.

**Considered alternatives:**
- **Dedicated 24/7 simulator background service on Render:** burns all free-tier hours within the first month and incurs unnecessary hosting costs.
- **Requiring live Africa's Talking API calls in all environments:** causes CI test failures when credentials are unset or airtime runs out, and risks rapid depletion of defense demo credits.

