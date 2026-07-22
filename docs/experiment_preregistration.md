# Experiment pre-registration — document-readiness checklist

This is a decision contract for a hypothetical test. It prevents the team from rewriting the
question after seeing the result. All baselines, volumes and effect assumptions are synthetic.

## Hypothesis and unit

- **Hypothesis:** showing accepted-document guidance and capture tips before KYC increases the
  probability that a started application reaches document submission.
- **Randomisation unit:** application ID, 1:1 assignment.
- **Population:** eligible new applicants beginning remote onboarding in France.
- **Analysis:** intention-to-treat; assignment is analysed regardless of later engagement.

## Metrics

| Type | Metric | Decision use |
|---|---|---|
| Primary | Document submitted / application started | Detect the stage directly affected by treatment |
| Secondary | Funded within seven days of start | Confirm downstream direction; continue measurement beyond the first-quarter read |
| Guardrail | Verification pass rate | Detect lower-quality submissions |
| Guardrail | Manual-review rate and latency | Detect added operations load |
| Guardrail | Support-contact rate | Detect confusing guidance or failure displacement |
| Guardrail | Fraud/compliance indicators | Mandatory owner-defined safety gate before launch |

## Statistical design

- Two-sided α = 0.05, power = 0.80.
- Primary baseline = 57.1%; MDE = 2.5 pp.
- Required sample = 6,103 per arm, 12,206 total.
- At 10,000 applications/month and 100% allocation: about 37 enrolment days.
- Minimum practically interesting point estimate = 1.5 pp.
- The modelled funded lift is 0.88 pp. Powering that outcome by itself requires 26,204 per arm,
  52,408 total, or about 158 days at the same traffic assumption.

## Validity checks

Before reading treatment effects:

1. validate event coverage and timestamp order against `artifacts/data_quality.json`;
2. test sample-ratio mismatch against the planned 50/50 allocation;
3. check duplicate assignment and cross-device identity rules;
4. apply only pre-registered eligibility and data-quality exclusions;
5. freeze the query version and analysis population.

One interim review is allowed for safety guardrails only. The primary effect is not read early.

## Decision rule

Advance to a staged rollout only when all conditions hold:

1. the primary 95% confidence interval excludes zero in the positive direction;
2. the primary point estimate is at least 1.5 pp;
3. the funded secondary shows no material adverse direction and remains on a longer holdout;
4. verification, review, support and compliance guardrails remain inside pre-agreed tolerances;
5. qualitative research finds no material loss of trust or comprehension.

If the primary is positive but a downstream or compliance signal is ambiguous, do not declare a
win: extend the holdout or run the necessary diagnostic. If the primary misses, document the null
and update the intervention priors rather than searching post hoc for a winning segment.

## Planned cuts

Device, document type and network quality are read for consistency and implementation risk. They
are not separately powered confirmatory hypotheses. Any apparent subgroup win is labelled
exploratory and requires a follow-up test plus fairness and compliance review.
