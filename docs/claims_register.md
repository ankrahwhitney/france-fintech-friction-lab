# Claims register

Every number or claim published in the README, dashboard or docs, with its status and where to
verify it. Statuses: **generated** (deterministic pipeline output, reproduce with `make all`),
**assumption** (authored input, editable in `config/model_assumptions.yml`), **public** (external
source, cited), **design choice** (methodological decision, defended in `docs/methodology.md`).

**Public sources last verified:** 2026-07-22. A scheduled GitHub Actions check re-tests every
external link monthly; source meaning and applicability still require human review.

| Claim | Status | Verify in |
|---|---|---|
| 50,000 applications, 162,892 events | generated | `artifacts/summary.json` |
| Funnel: 42,398 / 28,551 / 16,891 / 7,407 | generated | `artifacts/funnel.csv` |
| Largest transition loss: 13,847 before document submission | generated | `artifacts/funnel.csv` |
| Baselines: 14.81% funded, 4.40% manual review, 7.23% support | generated | `artifacts/summary.json` |
| Checklist decision score 72.8/100; explainer 65.0; assisted recovery 40.5 | generated | `artifacts/intervention_scorecard.csv` |
| Mean uplift 88 funded / 10k, P10–P90 64–113 | generated | `artifacts/intervention_scorecard.csv` |
| Checklist wins 4 of 5 weight profiles; speed-first picks the explainer | generated | `artifacts/weight_sensitivity.csv` |
| Experiment: 6,103/arm, 12,206 total, ≈37 days at full traffic | generated | `artifacts/summary.json` |
| Median stage durations (4 / 6 / 12 / 1,463 minutes) | generated | `artifacts/stage_durations.csv` |
| Review-path latency: 374-minute median vs 12 minutes straight-through | generated | `artifacts/review_latency.csv` |
| Funded-secondary sizing: 26,204/arm, 52,408 total, ≈158 days | generated | `artifacts/summary.json` |
| Weekly KPI movement is stationary sampling noise, not a trend | generated / limitation | `artifacts/weekly_kpis.csv`, `docs/methodology.md` |
| Checklist lift 2–6 pp (most likely 4) on document submission | assumption | `config/model_assumptions.yml` |
| Explainer lift 1–4 pp; assisted recovery lift 2–8 pp | assumption | `config/model_assumptions.yml` |
| Guardrail deltas (−0.8/−0.2, −0.4/0.0, +1.5/+1.0 pp) | assumption | `config/model_assumptions.yml` |
| €45 12-month contribution per funded account; €5.5 support contact; €8.5 manual review; 10,000 applications/month | assumption | `config/model_assumptions.yml` |
| Fixed/variable costs and delivery weeks per intervention | assumption | `config/model_assumptions.yml` |
| Evidence-confidence values 0.62 / 0.55 / 0.48 | assumption | `config/model_assumptions.yml`; calibration protocol in `docs/french_research_protocol.md` |
| Decision weights 0.40/0.25/0.20/0.15 | assumption | `config/model_assumptions.yml` |
| Absolute score anchors: 1.5 pp impact, 2.5 pp guardrail load, 4–8 delivery weeks | assumption | `config/model_assumptions.yml` |
| EU remote-onboarding rules require auditable identity capture (EBA/GL/2022/15, applies since 2 Oct 2023) | public | [EBA guidelines](https://www.eba.europa.eu/sites/default/files/document_library/Publications/Guidelines/2022/EBA-GL-2022-15%20GL%20on%20remote%20customer%20onboarding/1043884/Guidelines%20on%20the%20use%20of%20Remote%20Customer%20Onboarding%20Solutions.pdf) |
| France certifies remote identity-verification providers via ANSSI's PVID scheme (référentiel published 2021) | public | [ANSSI PVID](https://cyber.gouv.fr/offre-de-service/solutions-certifiees-et-qualifiees/services-de-securite-evalue/solutions-en-cours-de-qualification/prestataires-pvid/) |
| Net value excluded from the decision score | design choice | `docs/methodology.md` |
| Primary metric = document submission, not funded rate | design choice | `docs/methodology.md`, `docs/90_day_plan.md` |
| Funded within 7 days is computed from first-funding and start timestamps | generated and tested | `src/friction_lab/generate.py`, `tests/test_data_contract.py` |
| Segment gaps (e.g. residence permit 8.6% vs national ID 16.7% funded) | generated, **circular** — they replay generator coefficients | `artifacts/segment_friction.csv`, `docs/methodology.md` |
| No contract failures or PII-shaped columns | generated and tested | `artifacts/data_quality.json`, `tests/` |

Anything not in this table and not in the code is not a claim this repository makes. In
particular, the repository makes **no** claims about Revolut's funnel, volumes, economics or
roadmap.
