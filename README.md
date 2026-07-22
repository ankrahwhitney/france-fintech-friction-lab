# France Fintech Friction Lab

[![quality](https://github.com/ankrahwhitney/france-fintech-friction-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/ankrahwhitney/france-fintech-friction-lab/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-2457d6)
![Data](https://img.shields.io/badge/data-100%25%20synthetic-172033)

**A transparent Strategy & Operations case: diagnosing remote-onboarding friction, prioritising one
intervention and designing the test that could prove or disprove it.**

> **Evidence boundary:** Every application, event, conversion rate and commercial assumption in this
> repository is synthetic. This is not Revolut data, not an estimate of Revolut's performance and not
> causal proof. Public sources define the operating context; the model selects what to test next.

![Executive decision dashboard](assets/dashboard_preview.png)

## The 60-second decision

**Question:** Which onboarding intervention should a digital bank test first to increase verified and
funded accounts in France without creating disproportionate operational or compliance risk?

**Recommendation:** Test a **document-readiness checklist** before remote verification. In this
scenario it addresses the largest modelled source of avoidable friction while remaining faster to
learn and operationally safer than assisted recovery.

The generated baseline contains **50,000 applications and 162,892 events**. The largest absolute
transition loss is before document submission (13,847 applications). The modelled checklist ranks
first with a 72.8/100 decision score and a mean uplift of 88 funded accounts per 10,000 applications;
the 10th–90th percentile range is 64–113. These figures are scenario outputs, not performance claims.

The checklist wins four of five plausible decision-weight profiles. Under a speed-first profile the
contextual explainer wins, making the dependency on management priorities visible rather than
hard-coding one answer.

**Do not roll it out on the model alone.** Run a controlled experiment sized on the stage the
checklist targets: document submission as the primary metric (12,206 participants, about 37 days
of enrolment at 10,000 applications per month), funded account within seven days as the
directional secondary metric, and verification, manual review, support contact and compliance
indicators as guardrails. Powering the funded rate alone for the modelled ~0.9 pp lift would take
52,408 participants, or about 158 days at full traffic; the first test therefore reads the targeted
stage first and keeps a longer holdout for downstream confirmation.

**What would change the decision:** the primary document-submission 95% confidence interval does
not exclude zero in the positive direction; its point estimate is below the pre-agreed 1.5 pp
practical threshold; a funded-account, operational or compliance guardrail is materially adverse;
or qualitative research shows that the copy reduces trust.

## Why this repository exists

The case demonstrates the work of Strategy & Operations rather than a decorative dashboard:

1. define one decision and its constraints;
2. design an auditable event model;
3. diagnose funnel and segment friction with SQL;
4. make uncertain assumptions explicit;
5. compare interventions using impact and guardrails;
6. turn the recommendation into a 90-day operating plan.

## Skills demonstrated

| Role signal | Evidence in this repository |
|---|---|
| Optimise customer and internal experience | Funnel loss, review-queue latency and guardrail diagnosis |
| Research and propose processes | Three intervention hypotheses plus a France-specific evidence protocol |
| Translate data into action | SQL outputs → decision score → test recommendation → 90-day plan |
| Work through regulatory constraints | EBA, ANSSI, CNIL and ACPR anchors with explicit compliance gates |
| Deliver and communicate outcomes | Reproducible pipeline, executive memo, dashboard and decision rules |

## Outputs

| Recruiter path | Artifact |
|---|---|
| Read the recommendation | [`docs/executive_memo.md`](docs/executive_memo.md) |
| Scan the decision logic | [`docs/decision_one_pager.md`](docs/decision_one_pager.md) |
| See the execution plan | [`docs/90_day_plan.md`](docs/90_day_plan.md) |
| Check every public claim | [`docs/claims_register.md`](docs/claims_register.md) |
| Prepare for the interview | [`docs/interview_defence_guide.md`](docs/interview_defence_guide.md) |
| Present the case in three minutes | [`docs/recruiter_walkthrough.md`](docs/recruiter_walkthrough.md) |
| Field the France-specific research | [`docs/french_research_protocol.md`](docs/french_research_protocol.md) |
| Audit the event model | [`docs/data_dictionary.md`](docs/data_dictionary.md) |
| Review the experiment contract | [`docs/experiment_preregistration.md`](docs/experiment_preregistration.md) |
| Map evidence to operating skills | [`docs/role_evidence_map.md`](docs/role_evidence_map.md) |
| Explore the analysis | `streamlit run dashboard/app.py` |
| Audit assumptions | [`config/model_assumptions.yml`](config/model_assumptions.yml) |
| Review evidence boundaries | [`docs/methodology.md`](docs/methodology.md) |
| Inspect SQL | [`sql/`](sql/) |

## Reproduce the case

**Python 3.12 is required** and recorded in `.python-version`. The project intentionally has one
runtime contract so local reproduction and CI use the same analytics stack.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install uv==0.11.16
make setup
make all
make dashboard
```

The pipeline creates 50,000 synthetic applications and their event history, runs DuckDB SQL,
simulates uncertainty around three interventions and writes recruiter-facing artifacts.

Current generated baseline: 14.81% funded within seven days, 4.40% manual review and 7.23% support
contact. Run the pipeline to verify every figure from source code.

**Packaging contract:** this is an application repository, not a redistributable Python library.
Config and SQL are versioned repository resources. Run it from the clone root using the locked,
editable environment above; building and installing the wheel elsewhere is intentionally unsupported.

## Repository map

```text
assets/                   Committed dashboard screenshot
config/                   Explicit intervention and economic assumptions
dashboard/                Streamlit decision interface
data/processed/           Reproducible synthetic Parquet datasets (generated, not committed)
artifacts/                Generated metrics, quality report and model outputs
docs/                     Decision, methodology, risks and 90-day plan
scripts/                  Pipeline entry points
sql/                      Funnel, segment, weekly KPI and stage-duration analysis
src/friction_lab/         Data generation and decision model
tests/                    Data-contract, analysis and dashboard tests
```

## Technology

Python · pandas · NumPy · DuckDB · SQL · Parquet · Plotly · Streamlit · pytest · Ruff · GitHub Actions

## Candidate

**Whitney Ankrah** — B.Sc. Business Information Systems candidate with experience in banking IT
project management, process analysis, Python automation, entrepreneurship and an upcoming HR
Digitalisation & Analytics internship at Porsche AG.
