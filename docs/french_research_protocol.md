# French research protocol — replacing assumptions with evidence

The model's weakest inputs are its authored assumptions (lift ranges, guardrail deltas,
evidence-confidence values). This protocol specifies the France-specific research that would
replace each one before or during the instrument and build phases (days 1–30 of the 90-day
plan), and the regulatory anchors any onboarding change must respect.

## Regulatory anchors (verified public sources)

| Anchor | Why it constrains the checklist test |
|---|---|
| [EBA Guidelines on remote customer onboarding, EBA/GL/2022/15](https://www.eba.europa.eu/sites/default/files/document_library/Publications/Guidelines/2022/EBA-GL-2022-15%20GL%20on%20remote%20customer%20onboarding/1043884/Guidelines%20on%20the%20use%20of%20Remote%20Customer%20Onboarding%20Solutions.pdf) (applies since 2 Oct 2023) | EU-wide requirements for remote identification: document capture quality, liveness for unattended flows, auditable records. Checklist copy must not promise document types or shortcuts the KYC policy cannot honour. |
| [ANSSI PVID scheme](https://cyber.gouv.fr/offre-de-service/solutions-certifiees-et-qualifiees/services-de-securite-evalue/solutions-en-cours-de-qualification/prestataires-pvid/) (référentiel published 2021, run with the Direction Générale du Trésor) | France certifies remote identity-verification providers; which provider and certification level the bank uses determines what documents and capture flows the checklist may describe. |
| [CNIL / GDPR data-minimisation](https://www.cnil.fr/fr/reglement-europeen-protection-donnees) | The contextual explainer variant explains *why* each field is collected; its copy is a privacy-communication artifact and needs CNIL-lens review, not just marketing review. |
| [ACPR supervision](https://acpr.banque-france.fr/en) (AML/CFT under the Code monétaire et financier) | The French supervisor for onboarding/KYC compliance; any sequence change to identification steps goes through the compliance owner before experimentation. |

## Research workstreams → which config key each one updates

| # | Method | Sample | Updates |
|---|---|---|---|
| 1 | Moderated usability tests of the document-capture flow, French applicants, including residence-permit holders and low-bandwidth conditions | 12–16 sessions | `readiness_checklist.stage_lift_pp` (direction and plausibility of 2–6 pp), `evidence_confidence` |
| 2 | Support-ticket taxonomy: classify a quarter of onboarding contacts by stage and cause | full ticket export | `support_delta_pp` assumptions; validates that document questions dominate pre-submission contacts |
| 3 | Funnel replay on real event data: recompute `sql/01–04` on production events | n/a | replaces the entire synthetic baseline; the SQL is written to port as-is |
| 4 | Ops shadowing of manual-review queue: latency distribution, rework causes | 1 week | replaces the synthetic delay with arrival, capacity and SLA evidence; updates `manual_review_delta_pp` and kill-switch thresholds |
| 5 | Copy test of checklist + explainer wording (comprehension and trust, French language) | 200+ panel | explainer `stage_lift_pp`; the "copy reduces trust" reversal condition in the memo |
| 6 | Competitive teardown of document-readiness UX in French-market apps (public app flows only) | 5–8 apps | `delivery_weeks`, design scope; no proprietary data involved |

## Rules

- Findings update `config/model_assumptions.yml` in a reviewed change; the pipeline and CI then
  show whether the recommendation survives (`tests/test_analysis.py` pins the published ranking
  on purpose).
- No customer PII enters this repository under any workstream; aggregates only.
- If workstream 1 or 5 contradicts the checklist hypothesis, the explainer becomes the lead
  candidate per the speed-first sensitivity profile — that path is pre-agreed, not improvised.
