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
Power. The funded-rate lift the model itself predicts (~0.9 pp) would need ~5 months of full
traffic to detect; pretending otherwise designs a test that ends inconclusive. The checklist acts
on exactly one stage, so the test reads that stage (MDE 2.5 pp against a ~3.4 pp expected
per-applicant effect), keeps funded-in-7-days as a directional secondary, and gates shipping on
guardrails. If the primary moves but funding does not follow directionally, we do not ship.

**Q: Your recommended intervention has mean net value of €7k against €45k fixed cost, with a
negative P10. Why proceed?**
Because the decision being made is "what do we test", not "what do we roll out". The test buys
information: it converts an assumed 2–6 pp lift into a measured one, at bounded cost and with
guardrail improvements rather than degradations. The rollout decision afterwards uses measured
lift in the same value model — and if measured lift lands at the low end, the honest answer is
not to scale. That is written into the decision rule, not left to enthusiasm.

**Q: Assisted recovery has the highest modelled impact. Why is it last?**
It scores worst on everything except impact: +1.5 pp support contacts, +1.0 pp manual review,
8 delivery weeks, lowest evidence confidence, and modelled net value of −€32,659 even after
charging its variable cost only to the 23% of applications that actually fail verification. Under
a growth-first weighting it still loses to the checklist (69.8 vs 74.9). I would revisit it if
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
which is the shape of analysis that only exists on events. In this synthetic version durations
are minute-scale by construction; on real data the same query is the first place verification
SLAs and manual-review tails would show up.

**Q: "Funded within 7 days" — is there any 7-day logic in the code?**
No. The generator draws funding as a Bernoulli after verification with minute-scale timestamps.
It is a labelled simplification (`docs/methodology.md`, item 1), kept because it is the metric a
real test would define properly over event timestamps. Same class of simplification: manual
review does not gate verification in the generator.

**Q: If a fourth intervention were added, could the existing scores change?**
Yes — impact is normalised by the best option, so scores are relative to the option set. For
ranking three candidates that is fine; a standing portfolio would need an absolute scale. The
weight-sensitivity table exists precisely because single-number scores are fragile.

**Q: Walk me through the sample-size formula.**
Two-proportion z-test: n per arm = (z₁₋α/2·√(2p̄(1−p̄)) + z₁₋β·√(p₁(1−p₁)+p₂(1−p₂)))² / (p₂−p₁)².
With p₁ = 0.571, MDE 2.5 pp, α = 0.05, power 0.80 → 6,103 per arm. At 10,000 applications a month
that is ~37 days of full-traffic enrolment, which is why the test window in the 90-day plan is
40 days and analysis starts on day 71 (7-day maturity for the secondary metric).

**Q: Why should I believe any of this transfers to France specifically?**
The synthetic model does not encode France beyond document-type mix and locale — I am explicit
about that. What is France-specific is the constraint set the test must respect: EBA/GL/2022/15
on remote onboarding, ANSSI's PVID certification regime for remote identity verification, CNIL
data-minimisation expectations, and the research protocol that would ground the assumptions in
French applicant behaviour before the build phase ends.

**Q: What would you do differently with real data?**
Compute funded-in-7-days as a true event-window metric; let manual review gate verification and
measure its latency; replace triangular assumptions with priors fitted from past experiments;
add sequential testing instead of fixed-horizon; and move the decision score to an absolute
scale with net value as an explicit rollout gate.
