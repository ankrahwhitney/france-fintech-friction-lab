# 90-day operating plan — document-readiness checklist test

Assumes 10,000 applications per month and the experiment parameters in
`config/model_assumptions.yml`. The plan is a template for how I would run the quarter, not a
commitment on behalf of any company.

## Sample-size arithmetic (why the windows are what they are)

- Primary metric: document submission, baseline 57.1% per started application.
- Minimum detectable effect 2.5 pp, α = 0.05 (two-sided), power = 0.80 → **6,103 per arm,
  12,206 total** (`_experiment_sample_size` in `src/friction_lab/metrics.py`).
- At 10,000 applications/month and 100% allocation that is **≈ 37 days of enrolment**, so the
  test window is 40 days. Funded-within-7-days needs 7 more days of maturity for the last
  enrollee, which is why analysis starts on day 71, not day 66.
- The modelled most-likely checklist effect is ~4 pp conditional on reaching the document step
  (~3.4 pp per started application), comfortably above the MDE. The funded-rate secondary
  (~0.9 pp modelled) is read directionally only; powering it as primary would need roughly
  five months of full traffic.

## Phases

| Window | Phase | Outcomes and exit criteria |
|---|---|---|
| Days 1–14 | **Instrument** | Event definitions validated against the funnel QA checklist; dashboards live; compliance and legal review of checklist copy started (EBA/GL/2022/15 and CNIL data-minimisation lens); guardrail tolerances pre-agreed and written down. |
| Days 15–30 | **Build** | Checklist prototype user-tested with French applicants including residence-permit holders (the worst-performing document segment); experiment plan signed off: primary metric, MDE, stopping rules, no peeking outside two pre-planned checks. |
| Days 31–70 | **Test** | 50/50 randomised rollout at 100% of eligible traffic; guardrails reviewed twice weekly; one interim safety check (guardrails only, no effect peeking) around day 50; kill-switch criteria: verification pass rate −2 pp or support contact +1.5 pp sustained for a week. |
| Days 71–80 | **Decide** | Primary-metric confidence interval vs threshold; secondary metric direction; segment consistency (device, document type, network quality); decision documented with the pre-agreed rule, whatever the outcome. |
| Days 81–90 | **Scale or stop** | If shipped: staged ramp with monitoring and a 30-day guardrail review. If stopped: learning written up, next-ranked intervention (contextual explainer) queued with updated priors. |

## Operating cadence

- Twice-weekly guardrail stand-up (ops, support, compliance) during the test window.
- Weekly one-page status to the decision owner: enrolment vs plan, guardrails, risks.
- All decisions against pre-registered rules; deviations require written sign-off.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Checklist adds a step and slows motivated applicants | Measure time-to-document-submission as a supporting metric; copy kept to one screen. |
| Effect concentrated in easy segments, none where it matters | Pre-planned segment consistency read (document type, network quality) before scale decision. |
| Compliance change mid-test | Compliance reviewer embedded from day 1; sequence changes pause enrolment rather than patch mid-flight. |
| Enrolment below plan | Day-50 check includes enrolment forecast; extend window before lowering power. |
