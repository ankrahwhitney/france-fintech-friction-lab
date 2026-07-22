# 90-day operating plan — document-readiness checklist test

Assumes 10,000 applications per month and the experiment parameters in
`config/model_assumptions.yml`. The plan is a template for how I would run the quarter, not a
commitment on behalf of any company.

## Sample-size arithmetic (why the windows are what they are)

- Primary metric: document submission, baseline 57.1% per started application.
- Minimum detectable effect 2.5 pp, α = 0.05 (two-sided), power = 0.80 → **6,103 per arm,
  12,206 total** (`_experiment_sample_size` in `src/friction_lab/metrics.py`).
- At 10,000 applications/month and 100% allocation that is **≈ 37 days of enrolment**; the test
  window is 40 days (days 31–70), which covers that with buffer. Document submission resolves
  within the application session, so the primary metric is readable from day 71. The last
  enrollee needs 7 more days before the funded secondary matures, which still lands inside the
  Decide window (days 71–80) rather than extending the test.
- The modelled most-likely checklist effect is ~4 pp conditional on reaching the document step
  (~3.4 pp per started application), comfortably above the MDE. The funded-rate secondary
  (0.88 pp modelled) is read directionally in the first window; powering it as primary requires
  26,204 per arm, 52,408 total, or about 158 days at full traffic.

## Phases

| Window | Phase | Outcomes and exit criteria |
|---|---|---|
| Days 1–14 | **Instrument** | Event definitions validated against the funnel QA checklist; dashboards live; compliance and legal review of checklist copy started (EBA/GL/2022/15 and CNIL data-minimisation lens); guardrail tolerances pre-agreed and written down. |
| Days 15–30 | **Build** | Checklist prototype user-tested with French applicants including residence-permit holders (the worst-performing document segment); experiment plan signed off: primary metric, MDE, stopping rules, no peeking outside two pre-planned checks. |
| Days 31–70 | **Test** | 50/50 randomised rollout at 100% of eligible traffic; sample-ratio mismatch and event-quality checks; guardrails reviewed twice weekly; one interim safety check (guardrails only, no primary-effect peeking) around day 50; kill-switch criteria: verification pass rate −2 pp or support contact +1.5 pp sustained for a week. |
| Days 71–80 | **Decide** | Primary 95% interval and point estimate vs the 1.5 pp practical threshold; secondary direction; pre-planned segment consistency (device, document type, network quality); decision documented against the registered rule, whatever the outcome. |
| Days 81–90 | **Scale or stop** | If shipped: staged ramp with monitoring and a 30-day guardrail review. If stopped: learning written up, next-ranked intervention (contextual explainer) queued with updated priors. |

## Operating cadence

- Twice-weekly guardrail stand-up (ops, support, compliance) during the test window.
- Weekly one-page status to the decision owner: enrolment vs plan, guardrails, risks.
- All decisions against pre-registered rules; deviations require written sign-off.

## Ownership map

Hypothetical roles, used to show the operating contract rather than infer any company structure.

| Workstream | Accountable | Responsible | Consulted / informed |
|---|---|---|---|
| Decision and scope | Head of Onboarding Operations | Strategy & Operations manager | Product, Data, Compliance, Market lead |
| Event contract and QA | Data lead | Analyst / Analytics engineer | Product Operations, Engineering |
| Checklist build | Product lead | Product designer + Engineer | Operations, Support, Localisation |
| Regulatory review | Compliance owner | Compliance + Legal reviewers | Product, Data protection, Operations |
| Experiment execution | Product Operations lead | Strategy & Operations manager | Data, Engineering, Support |
| Scale / stop decision | Head of Onboarding Operations | Strategy & Operations manager prepares recommendation | All workstream owners |

## Weekly decision update (one-page structure)

1. **Decision needed:** one sentence and named owner.
2. **Progress:** milestone status, enrolment vs plan and next seven days.
3. **Evidence:** primary metric remains blinded during the test; guardrails and data quality only.
4. **Risks:** owner, probability/impact, mitigation and escalation date.
5. **Changes:** any deviation from the registered design, with written approver.

This keeps senior reporting short while preserving a decision log that another market team could
audit or reuse.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Checklist adds a step and slows motivated applicants | Measure time-to-document-submission as a supporting metric; copy kept to one screen. |
| Effect concentrated in easy segments, none where it matters | Pre-planned segment consistency read (document type, network quality) before scale decision. |
| Compliance change mid-test | Compliance reviewer embedded from day 1; sequence changes pause enrolment rather than patch mid-flight. |
| Enrolment below plan | Day-50 check includes enrolment forecast; extend window before lowering power. |
