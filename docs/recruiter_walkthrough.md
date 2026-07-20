# Three-minute walkthrough

A script for presenting the case live, timed to three minutes.

**0:00 — The question (20s).**
"Which onboarding intervention should a digital bank in France test first to get more verified,
funded accounts — without blowing up support, manual review or compliance? Everything you'll see
is synthetic and reproducible from one command; the point is the decision method, not the data."

**0:20 — The diagnosis (40s).**
"Fifty thousand generated applications. The funnel loses most — 13,847 applications — before
document submission, more than at verification or funding. The segment cuts point the same way:
residence-permit holders and unstable-network sessions struggle exactly at the document and
verification stages. That's where an intervention should aim first."

**1:00 — The options and the decision (50s).**
"Three candidates: a document-readiness checklist, a data-use explainer, and assisted recovery
after failed submissions. Scored on conversion impact, guardrails, speed to learn and evidence
confidence, the checklist wins at 77.7 — not because it has the biggest modelled impact (assisted
recovery does) but because it's the only one that improves the guardrails while moving the worst
stage. And the ranking is stress-tested: under five different management priorities the checklist
wins four; a speed-first leadership would pick the explainer instead. The model tells you where
the decision depends on priorities instead of hiding it."

**1:50 — The test (40s).**
"The model's job ends at 'what to test'. The test: randomise the checklist before the document
step, primary metric document submission — the one stage it targets and the only metric powerable
in a quarter — 12,206 applicants, about 37 days of enrolment. Funded-in-seven-days reads
directionally; verification pass rate, manual review and support contact are guardrails with
pre-agreed kill-switches. Ship only if the interval clears the threshold and no guardrail breaks."

**2:30 — Why this is the job (30s).**
"Strategy & Operations is deciding under uncertainty with explicit assumptions and reversible
steps. Every assumption in this case lives in one config file, every claim has a register entry
saying whether it's generated, assumed or public, and the whole thing rebuilds deterministically
with `make all`. Change my assumptions and the repo tells you honestly whether the decision
changes."

**If only 60 seconds:** show the README's "60-second decision" block and the dashboard's
executive page; offer `docs/claims_register.md` as proof that every number is accounted for.
