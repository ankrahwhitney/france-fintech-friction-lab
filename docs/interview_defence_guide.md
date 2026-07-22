# Interview defence guide

The questions a demanding interviewer should ask about this repository, with the honest answers.
If an answer here ever contradicts the code, the code wins — say so and correct it.

**Q: Where do the lift ranges and evidence-confidence values come from?**
They are authored assumptions, not measurements — that is the point of the design. The triangular
ranges encode "checklist-type UX fixes plausibly move a document step by low single digits"; the
confidence values (0.62/0.55/0.48) rank how directly each hypothesis could be validated with
cheap research. I would not defend the specific numbers; I defend making them explicit, editable
in one file, and stress-tested across five weight profiles. The research protocol
(`docs/french_research_protocol.md`) is how they get replaced with evidence.

**Q: Why is the primary metric document submission and not funded accounts?**
Power. The funded-rate lift the model predicts (0.88 pp) needs 26,204 participants per arm —
52,408 total, or about 158 days at the authored traffic volume. Pretending it is powerable inside
one quarter designs an inconclusive test. The checklist acts on one stage, so the first read uses
that stage (MDE 2.5 pp against a ~3.4 pp expected per-applicant effect), keeps funded-in-seven-days
directional and on a longer holdout, and gates advancement on guardrails.

**Q: Your recommended intervention has mean net value of €5.9k against €45k fixed cost, with a
negative P10. Why proceed?**
Because the decision being made is "what do we test", not "what do we roll out". The test buys
information: it converts an assumed 2–6 pp lift into a measured one, at bounded cost and with
guardrail improvements rather than degradations. The rollout decision afterwards uses measured
lift in the same value model — and if measured lift lands at the low end, the honest answer is
not to scale. That is written into the decision rule, not left to enthusiasm.

**Q: Assisted recovery has the highest modelled impact. Why is it last?**
It scores worst on everything except impact: +1.5 pp support contacts, +1.0 pp manual review,
8 delivery weeks, lowest evidence confidence, and modelled net value of −€34,206 even after
charging its variable cost only to the 23% of applications that actually fail verification. Under
a growth-first weighting it still loses to the checklist (59.0 vs 66.8). I would revisit it if
support-cost assumptions improve or if the checklist test shows document friction is not the
binding constraint.

**Q: What did the segment analysis discover?**
Nothing — and I say so in `docs/methodology.md`. The gaps replay the generator's own
coefficients; they are circular. What the section demonstrates is the diagnostic cut I would run
on real data (document type × network quality first, because that is where verification friction
and compliance risk interact), and the caption on the dashboard says targeting decisions need
fairness and compliance review before anyone acts on segments.

**Q: What does the event stream add beyond the applications table?**
The stage-duration analysis (`sql/04_stage_durations.sql`) — medians and P90s per transition —
which is the shape of analysis that only exists on events. The model also separates manual-review
latency from straight-through verification (`sql/05_review_latency.sql`): 374-minute vs 12-minute
synthetic medians. Those are not market claims; the point is to avoid hiding a queue in one blended
conversion number.

**Q: "Funded within 7 days" — is there any 7-day logic in the code?**
Yes. The generator first creates an any-time first-funding timestamp after successful verification,
then sets `funded_7d` only if that timestamp is no later than seven days after application start.
The equality is pinned in `tests/test_data_contract.py`. The timing distribution is still authored,
so the KPI is technically correct without pretending the baseline is empirical.

**Q: If a fourth intervention were added, could the existing scores change?**
Not merely because it was added. Component scores use fixed caps from the config rather than the
best and worst options in the current set. Existing scores change only if assumptions or anchors
change. The anchors are still judgement inputs, which is why the component table and five weight
profiles remain visible.

**Q: Walk me through the sample-size formula.**
Two-proportion z-test: n per arm = (z₁₋α/2·√(2p̄(1−p̄)) + z₁₋β·√(p₁(1−p₁)+p₂(1−p₂)))² / (p₂−p₁)².
With p₁ = 0.571, MDE 2.5 pp, α = 0.05, power 0.80 → 6,103 per arm. At 10,000 applications a month
that is ~37 days of full-traffic enrolment; the plan gives it a 40-day window (days 31–70). The
primary metric resolves within the session, so analysis starts on day 71. The funded secondary
for the last enrollee matures seven days later, but the fully powered downstream read requires a
longer holdout because the expected effect is much smaller.

**Q: Why should I believe any of this transfers to France specifically?**
The synthetic model does not encode France beyond document-type mix and locale — I am explicit
about that. What is France-specific is the constraint set the test must respect: EBA/GL/2022/15
on remote onboarding, ANSSI's PVID certification regime for remote identity verification, CNIL
data-minimisation expectations, and the research protocol that would ground the assumptions in
French applicant behaviour before the build phase ends.

**Q: What would you do differently with real data?**
Model review as an actual queue with arrival rate, capacity, service levels and rework; replace
triangular assumptions with historical experiments and primary research; validate identity and
cross-device assignment; estimate heterogeneous downstream conversion for marginal applicants;
and keep measured net value as an explicit rollout gate. I would use sequential methods only if
they were pre-specified and operationally needed, not to peek until a result looks positive.
