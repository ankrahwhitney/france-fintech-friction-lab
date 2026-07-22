from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

st.set_page_config(
    page_title="France Fintech Friction Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    :root { --ink: #172033; --muted: #5d6678; --accent: #2457d6; --line: #dfe4ec; }
    .stApp { background: #f8fafc; color: var(--ink); }
    [data-testid="stToolbar"], .stAppDeployButton { visibility: hidden; }
    .block-container { max-width: 1320px; padding-top: 2.2rem; }
    h1, h2, h3 { letter-spacing: -0.035em; }
    [data-testid="stMetric"] {
        background: white; border: 1px solid var(--line); border-radius: 12px;
        padding: 16px 18px; box-shadow: 0 3px 12px rgba(23,32,51,.05);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    .decision-box {
        background: #172033; color: white; padding: 26px 28px;
        border-radius: 12px; margin: 10px 0 18px 0;
    }
    .decision-box small { color: #b9c8ef; text-transform: uppercase; letter-spacing: .08em; }
    .decision-box h3 { color: white; margin: .4rem 0 .6rem 0; }
    .decision-box p { color: #e4e9f4; max-width: 900px; margin-bottom: 0; }
    .disclaimer {
        border-left: 4px solid var(--accent); padding: 12px 16px; background: #edf3ff;
        border-radius: 0 10px 10px 0; color: #243c73;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_artifacts() -> tuple[
    dict,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    required = [
        ARTIFACTS / "summary.json",
        ARTIFACTS / "funnel.csv",
        ARTIFACTS / "segment_friction.csv",
        ARTIFACTS / "weekly_kpis.csv",
        ARTIFACTS / "stage_durations.csv",
        ARTIFACTS / "review_latency.csv",
        ARTIFACTS / "intervention_scorecard.csv",
        ARTIFACTS / "weight_sensitivity.csv",
    ]
    if not all(path.exists() for path in required):
        try:
            from friction_lab.generate import generate_datasets
            from friction_lab.metrics import build_analysis_artifacts

            generate_datasets()
            build_analysis_artifacts()
        except Exception as error:
            st.error(
                "Analysis artifacts are missing and automatic regeneration failed "
                f"({error}). Run `make all` from the repository root, then restart "
                "the dashboard."
            )
            st.stop()
    if not all(path.exists() for path in required):
        st.error(
            "Analysis artifacts are missing. Run `make all` from the repository root, "
            "then restart the dashboard."
        )
        st.stop()
    summary = json.loads((ARTIFACTS / "summary.json").read_text(encoding="utf-8"))
    return (
        summary,
        pd.read_csv(ARTIFACTS / "funnel.csv"),
        pd.read_csv(ARTIFACTS / "segment_friction.csv"),
        pd.read_csv(ARTIFACTS / "weekly_kpis.csv"),
        pd.read_csv(ARTIFACTS / "stage_durations.csv"),
        pd.read_csv(ARTIFACTS / "review_latency.csv"),
        pd.read_csv(ARTIFACTS / "intervention_scorecard.csv"),
        pd.read_csv(ARTIFACTS / "weight_sensitivity.csv"),
    )


summary, funnel, segments, weekly, durations, review_latency, scorecard, sensitivity = (
    load_artifacts()
)

with st.sidebar:
    st.markdown("### France Fintech Friction Lab")
    st.caption("Strategy & Operations portfolio case · Whitney Ankrah")
    st.divider()
    page = st.radio(
        "View",
        ["Executive decision", "Funnel diagnosis", "Segment drill-down", "Test design"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**Decision lens**")
    st.caption("Conversion impact · Guardrails · Speed to learn · Evidence confidence")
    st.markdown("**Data**")
    st.caption(f"{summary['applications']:,} synthetic applications")
    st.caption(f"{summary['events']:,} synthetic events")
    st.success("Data contract: passed", icon="✅")

st.title("France Fintech Friction Lab")
st.markdown(
    "Which onboarding intervention should a digital bank test first to increase "
    "verified and funded "
    "accounts in France without creating disproportionate operational or compliance risk?"
)
st.markdown(
    '<div class="disclaimer"><strong>Portfolio simulation:</strong> all application-level data and '
    "commercial assumptions are synthetic. This is not Revolut data, not a claim about Revolut's "
    "current funnel, and not causal evidence.</div>",
    unsafe_allow_html=True,
)

if page == "Executive decision":
    recommended = scorecard.iloc[0]
    st.markdown(
        f"""
        <div class="decision-box">
          <small>Recommendation for a controlled test</small>
          <h3>{recommended["intervention"]}</h3>
          <p>Prioritise the intervention with the best modelled balance of conversion potential,
          operational guardrails, implementation speed and evidence confidence. Run a staged A/B
          test before any broad rollout.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    stage_labels = {
        "Profile completed": "Profile",
        "Document submitted": "Documents",
        "Verification completed": "Verification",
        "Funded within 7 days": "Funding",
    }
    drop_stage = summary["largest_absolute_drop_before_stage"]
    cols = st.columns(4)
    cols[0].metric("Funded within 7 days", f"{summary['funded_7d_pct']:.1f}%")
    cols[1].metric("Largest loss before", stage_labels.get(drop_stage, drop_stage))
    cols[2].metric("Manual review", f"{summary['manual_review_pct']:.1f}%")
    cols[3].metric("Support contact", f"{summary['support_contact_pct']:.1f}%")

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Intervention scorecard")
        chart = px.bar(
            scorecard.sort_values("decision_score"),
            x="decision_score",
            y="intervention",
            orientation="h",
            color="decision_score",
            color_continuous_scale=["#dbe7ff", "#2457d6", "#173477"],
            labels={"decision_score": "Decision score", "intervention": ""},
            text="decision_score",
        )
        chart.update_layout(
            coloraxis_showscale=False,
            height=330,
            margin=dict(l=10, r=20, t=10, b=20),
        )
        st.plotly_chart(chart, width="stretch")
    with right:
        st.subheader("Modelled impact range")
        impact = scorecard.sort_values("incremental_funded_per_10k_mean")
        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=impact["incremental_funded_per_10k_mean"],
                y=impact["intervention"],
                mode="markers",
                marker=dict(size=13, color="#2457d6"),
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=impact["incremental_funded_per_10k_p90"]
                    - impact["incremental_funded_per_10k_mean"],
                    arrayminus=impact["incremental_funded_per_10k_mean"]
                    - impact["incremental_funded_per_10k_p10"],
                ),
            )
        )
        figure.update_layout(
            height=330,
            margin=dict(l=10, r=20, t=10, b=20),
            xaxis_title="Incremental funded accounts per 10k applications",
            yaxis_title="",
        )
        st.plotly_chart(figure, width="stretch")

    st.subheader("Weight sensitivity")
    winners = sensitivity.loc[sensitivity["winner"], ["weight_profile", "intervention"]]
    st.dataframe(winners, hide_index=True, width="stretch")
    top_intervention = scorecard.iloc[0]["intervention"]
    top_wins = int((winners["intervention"] == top_intervention).sum())
    other_winners = sorted(set(winners["intervention"]) - {top_intervention})
    dissent = (
        f" Other profiles select: {', '.join(other_winners)}." if other_winners else ""
    )
    st.caption(
        f"{top_intervention} wins {top_wins} of {len(winners)} plausible weighting profiles, "
        f"showing where the ranking depends on management priorities.{dissent}"
    )

    st.subheader("Why the recommendation wins")
    components = scorecard[
        [
            "intervention",
            "impact_score",
            "guardrail_score",
            "speed_score",
            "confidence_score",
            "decision_score",
        ]
    ].rename(
        columns={
            "intervention": "Intervention",
            "impact_score": "Impact",
            "guardrail_score": "Guardrails",
            "speed_score": "Speed",
            "confidence_score": "Evidence",
            "decision_score": "Total",
        }
    )
    st.dataframe(components, hide_index=True, width="stretch")
    st.caption(
        "Component scores use fixed anchors from config/model_assumptions.yml, so adding another "
        "candidate does not silently rescale every existing option."
    )

    st.subheader("What would change the decision?")
    st.markdown(
        "The recommendation should be revisited if the readiness checklist increases "
        "manual reviews, "
        "if the realised funded-account lift is below the pre-agreed minimum detectable effect, or "
        "if compliance review identifies additional information requirements."
    )

elif page == "Funnel diagnosis":
    cols = st.columns([1.45, 1])
    with cols[0]:
        st.subheader("Onboarding funnel")
        figure = go.Figure(
            go.Funnel(
                y=funnel["stage"],
                x=funnel["applications"],
                textinfo="value+percent initial+percent previous",
                marker={"color": ["#172033", "#243c73", "#2457d6", "#4c78e6", "#90adf4"]},
            )
        )
        figure.update_layout(height=470, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(figure, width="stretch")
    with cols[1]:
        st.subheader("Loss by transition")
        drops = funnel.iloc[1:].copy()
        drop_chart = px.bar(
            drops,
            x="drop_from_previous",
            y="stage",
            orientation="h",
            color="drop_from_previous",
            color_continuous_scale=["#dbe7ff", "#2457d6"],
            labels={"drop_from_previous": "Applications lost", "stage": "Before stage"},
        )
        drop_chart.update_layout(
            coloraxis_showscale=False, height=470, margin=dict(l=10, r=20, t=10, b=20)
        )
        st.plotly_chart(drop_chart, width="stretch")

    st.subheader("Time between stages")
    duration_view = durations.rename(
        columns={
            "transition": "Transition",
            "applications": "Applications",
            "median_minutes": "Median minutes",
            "p90_minutes": "P90 minutes",
        }
    )[["Transition", "Applications", "Median minutes", "P90 minutes"]]
    st.dataframe(duration_view, hide_index=True, width="stretch")
    st.caption(
        "Computed from the event stream (sql/04_stage_durations.sql). The synthetic generator "
        "draws stage durations, so these are illustrative of the analysis pattern, "
        "not of real verification turnaround times."
    )

    st.subheader("Verification latency by operating path")
    latency_view = review_latency.rename(
        columns={
            "verification_path": "Path",
            "applications": "Applications",
            "median_minutes": "Median minutes",
            "p90_minutes": "P90 minutes",
            "p95_minutes": "P95 minutes",
        }
    )
    st.dataframe(latency_view, hide_index=True, width="stretch")
    st.caption(
        "Manual review is modelled as a real delay. This cut separates queue performance from "
        "straight-through verification instead of hiding both in one median."
    )

    st.subheader("Guardrails over time")
    selected = weekly.melt(
        id_vars="week_start",
        value_vars=["manual_review_pct", "support_contact_pct"],
        var_name="metric",
        value_name="rate_pct",
    )
    selected["metric"] = selected["metric"].map(
        {"manual_review_pct": "Manual review", "support_contact_pct": "Support contact"}
    )
    line = px.line(
        selected,
        x="week_start",
        y="rate_pct",
        color="metric",
        color_discrete_map={"Manual review": "#2457d6", "Support contact": "#c75a36"},
        labels={"week_start": "Week", "rate_pct": "Rate (%)", "metric": ""},
    )
    st.plotly_chart(line, width="stretch")
    st.caption(
        "The generator is stationary, so weekly movement here is sampling noise. The view "
        "demonstrates the monitoring layout a real test would use, not a trend."
    )

elif page == "Segment drill-down":
    dimension = st.selectbox("Segment dimension", segments["dimension"].unique())
    filtered = segments.loc[segments["dimension"] == dimension].sort_values("funded_7d_pct")
    metric = st.radio(
        "Metric",
        ["funded_7d_pct", "manual_review_pct", "support_contact_pct"],
        horizontal=True,
        format_func={
            "funded_7d_pct": "Funded in 7 days",
            "manual_review_pct": "Manual review",
            "support_contact_pct": "Support contact",
        }.get,
    )
    bar = px.bar(
        filtered,
        x=metric,
        y="segment",
        orientation="h",
        color=metric,
        color_continuous_scale=["#dbe7ff", "#2457d6", "#173477"],
        text=metric,
        labels={metric: "Rate (%)", "segment": ""},
    )
    bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    bar.update_layout(coloraxis_showscale=False, height=440)
    st.plotly_chart(bar, width="stretch")
    st.caption(
        "Segments are diagnostic, not causal. Any targeting decision requires fairness, "
        "privacy and "
        "compliance review; the synthetic dataset intentionally excludes direct identifiers and "
        "protected characteristics."
    )

else:
    st.subheader("Minimum viable experiment")
    cols = st.columns(4)
    cols[0].metric("Total sample", f"{summary['experiment_total_sample']:,}")
    cols[1].metric("Per arm", f"{summary['experiment_sample_per_arm']:,}")
    cols[2].metric("Detectable lift", f"{summary['minimum_detectable_lift_pp']:.1f} pp")
    cols[3].metric("Days at full traffic", f"{summary['experiment_days_full_traffic']}")
    st.markdown(
        f"""
- **Population:** eligible new applicants starting onboarding in France.
- **Control:** current onboarding sequence.
- **Treatment:** document-readiness checklist before the document step.
- **Primary metric:** {summary["experiment_primary_metric"].lower()} — the stage the checklist
  directly targets, where the modelled most-likely lift (~3.4 pp per started application)
  exceeds the {summary["minimum_detectable_lift_pp"]:.1f} pp minimum detectable effect.
- **Secondary metric:** {summary["experiment_secondary_metric"].lower()}, read directionally:
  its modelled lift (~0.9 pp) needs {summary["funded_secondary_total_sample"]:,} applicants,
  or about {summary["funded_secondary_days_full_traffic"]} days at full traffic, to power on its
  own, so the first-quarter read is directional.
- **Guardrails:** verification pass rate, manual-review rate, support-contact rate, fraud and
  compliance monitoring.
- **Decision rule:** advance only if the primary effect is statistically positive, its point
  estimate is at least {summary["minimum_practical_lift_pp"]:.1f} pp, the funded secondary does
  not show a material adverse direction, and no guardrail breaches its tolerance.
        """
    )
    st.caption(
        f"Sample sized on a {summary['experiment_primary_base_rate_pct']:.1f}% baseline "
        f"{summary['experiment_primary_metric'].lower()} rate: "
        f"{summary['experiment_total_sample']:,} applicants is about "
        f"{summary['experiment_days_full_traffic']} days of enrolment at "
        f"{summary['monthly_applications']:,} applications per month with 100% allocation, "
        "which fits the 40-day test window below."
    )
    st.subheader("90-day operating cadence")
    timeline = pd.DataFrame(
        [
            ("Days 1-14", "Instrument", "Validate event definitions, QA funnel, compliance review"),
            (
                "Days 15-30",
                "Build",
                "Prototype checklist, user-test copy, finalise experiment plan",
            ),
            ("Days 31-70", "Test", "Run controlled rollout, review guardrails twice weekly"),
            ("Days 71-80", "Decide", "Analyse effect and segment consistency, document decision"),
            (
                "Days 81-90",
                "Scale or stop",
                "Ramp with monitoring or close test and capture learning",
            ),
        ],
        columns=["Window", "Phase", "Outcome"],
    )
    st.dataframe(timeline, hide_index=True, width="stretch")
    st.subheader("Validity checks before reading the result")
    st.markdown(
        """
- Pre-register eligibility, assignment unit, metrics and exclusions before enrolment.
- Confirm event completeness and run a sample-ratio-mismatch check before effect estimation.
- Report intention-to-treat first; do not exclude applicants based on post-treatment behaviour.
- Use one guardrail-only safety review; do not peek at the primary effect mid-test.
- Read pre-planned segments for consistency, not as independent discoveries.
        """
    )
