# Claims register

Every number or claim published in the README, dashboard or docs, with its status and where to
verify it. Statuses: **generated** (deterministic pipeline output, reproduce with `make all`),
**assumption** (authored input, editable in `config/model_assumptions.yml`), **public** (external
source, cited), **design choice** (methodological decision, defended in `docs/methodology.md`).

| Claim | Status | Verify in |
|---|---|---|
| 50,000 applications, 149,108 events | generated | `artifacts/summary.json` |
| Funnel: 42,398 / 28,551 / 16,949 / 7,597 | generated | `artifacts/funnel.csv` |
| Largest transition loss: 13,847 before document submission | generated | `artifacts/funnel.csv` |
| Baselines: 15.19% funded, 4.26% manual review, 7.23% support | generated | `artifacts/summary.json` |
| Checklist decision score 77.7/100; explainer 67.3; assisted recovery 47.2 | generated | `artifacts/intervention_scorecard.csv` |
| Mean uplift 91 funded / 10k, P10–P90 66–116 | generated | `artifacts/intervention_scorecard.csv` |
| Checklist wins 4 of 5 weight profiles; speed-first picks the explainer | generated | `artifacts/weight_sensitivity.csv` |
| Experiment: 6,103/arm, 12,206 total, ≈37 days at full traffic | generated | `artifacts/summary.json` |
| Median stage durations (4 / 6 / 12 / 73 minutes) | generated | `artifacts/stage_durations.csv` |
| Checklist lift 2–6 pp (most likely 4) on document submission | assumption | `config/model_assumptions.yml` |
| Explainer lift 1–4 pp; assisted recovery lift 2–8 pp | assumption | `config/model_assumptions.yml` |
| Guardrail deltas (−0.8/−0.2, −0.4/0.0, +1.5/+1.0 pp) | assumption | `config/model_assumptions.yml` |
| €45 12-month contribution per funded account; €5.5 support contact; €8.5 manual review; 10,000 applications/month | assumption | `config/model_assumptions.yml` |
| Fixed/variable costs and delivery weeks per intervention | assumption | `config/model_assumptions.yml` |
| Evidence-confidence values 0.62 / 0.55 / 0.48 | assumption | `config/model_assumptions.yml`; calibration protocol in `docs/french_research_protocol.md` |
| Decision weights 0.40/0.25/0.20/0.15 | assumption | `config/model_assumptions.yml` |
| EU remote-onboarding rules require auditable identity capture (EBA/GL/2022/15, applies since 2 Oct 2023) | public | [EBA guidelines](https://www.eba.europa.eu/sites/default/files/document_library/Publications/Guidelines/2022/EBA-GL-2022-15%20GL%20on%20remote%20customer%20onboarding/1043884/Guidelines%20on%20the%20use%20of%20Remote%20Customer%20Onboarding%20Solutions.pdf) |
| France certifies remote identity-verification providers via ANSSI's PVID scheme (since April 2021) | public | [ANSSI PVID](https://cyber.gouv.fr/offre-de-service/solutions-certifiees-et-qualifiees/services-de-securite-evalue/solutions-en-cours-de-qualification/prestataires-pvid/) |
| Net value excluded from the decision score | design choice | `docs/methodology.md` |
| Primary metric = document submission, not funded rate | design choice | `docs/methodology.md`, `docs/90_day_plan.md` |
| "Funded within 7 days" is a label, not a windowed computation, in the generator | design choice / limitation | `docs/methodology.md` |
| Segment gaps (e.g. residence permit 8.5% vs national ID 17.3% funded) | generated, **circular** — they replay generator coefficients | `artifacts/segment_friction.csv`, `docs/methodology.md` |

Anything not in this table and not in the code is not a claim this repository makes. In
particular, the repository makes **no** claims about Revolut's funnel, volumes, economics or
roadmap.
