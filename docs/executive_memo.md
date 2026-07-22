# Executive memo — what to test first in French remote onboarding

**Author:** Whitney Ankrah · **Scope:** fully synthetic scenario model, not Revolut data
**Decision owner (hypothetical):** Head of Onboarding Operations, France

## The question

Which onboarding intervention should a digital bank test first to increase verified and funded
accounts in France without creating disproportionate operational or compliance risk?

## Recommendation

Test a **document-readiness checklist** shown before remote identity verification: which documents
are accepted, what a valid capture looks like, and what to have ready.

## Why this one first

1. **It targets the largest modelled loss.** Of 50,000 generated applications, the biggest
   absolute transition loss is before document submission: 13,847 applications, versus 11,660
   before verification and 7,602 before profile completion (`artifacts/funnel.csv`).
2. **It scores best on the stated decision lens.** Against conversion impact (40%), guardrails
   (25%), speed to learn (20%) and evidence confidence (15%), the checklist scores 72.8/100,
   ahead of the contextual explainer (65.0) and assisted recovery (40.5)
   (`artifacts/intervention_scorecard.csv`).
3. **It is operationally conservative.** Its modelled guardrail deltas are favourable (support
   contacts −0.8 pp, manual review −0.2 pp), whereas assisted recovery adds load to both queues.
4. **The ranking survives most priority shifts.** The checklist wins four of five plausible
   decision-weight profiles; a speed-first profile selects the explainer instead
   (`artifacts/weight_sensitivity.csv`). The dependency on management priorities is explicit.

## What the model does and does not say

- Modelled mean uplift: **88 incremental funded accounts per 10,000 applications** (10th–90th
  percentile 64–113), from a triangular 2–6 pp lift assumption on the document-submission stage.
- Modelled annual net value: **+€5,940 mean, with a 10th percentile of −€7,224** against €45,000
  fixed cost. The economics are close to break-even at these assumptions — the case for testing
  rests on learning value and guardrail safety, not on a guaranteed financial return. Net value
  is deliberately excluded from the test-selection score (see `docs/methodology.md`).
- Assisted recovery has the **highest** modelled conversion impact (125 per 10k) but fails the
  decision lens on guardrails, cost and delivery time, with a modelled net value of −€34,206.
- Every input is an authored assumption listed in `config/model_assumptions.yml`. Nothing here is
  a Revolut or French-market measurement.

## The test, not the rollout

Primary metric: **document submission rate**, the stage the checklist targets, where the modelled
most-likely lift (~3.4 pp per started application) exceeds the 2.5 pp minimum detectable effect.
12,206 participants ≈ 37 days of enrolment at 10,000 applications per month. Funded within seven
days is the directional secondary metric: at the modelled 0.88 pp lift it needs 52,408 participants
and about 158 days for equivalent power. Verification pass rate, manual-review load and latency,
support contact and compliance indicators are guardrails. Full design in `docs/90_day_plan.md`.

## What would change the recommendation

- Evidence that the checklist increases review queues or slows verification.
- A realised primary-metric lift below the pre-agreed threshold.
- Customer research showing the copy reduces trust instead of building it.
- A compliance or legal requirement that changes the proposed sequence (see
  `docs/french_research_protocol.md` for the regulatory anchors to check first).
