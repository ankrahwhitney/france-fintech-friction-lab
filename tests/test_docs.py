from __future__ import annotations

import json
import re

from friction_lab.config import ARTIFACT_DIR, ROOT


def test_relative_markdown_links_resolve() -> None:
    markdown_files = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    missing: list[str] = []
    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean_target = target.split("#", maxsplit=1)[0]
            if clean_target and not (document.parent / clean_target).resolve().exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")
    assert not missing, f"Broken relative links: {missing}"


def test_readme_decision_numbers_match_generated_summary() -> None:
    summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    score = f"{summary['recommended_decision_score']:.1f}/100"

    assert f"{summary['applications']:,} applications" in readme
    assert f"{summary['events']:,} events" in readme
    assert score in readme
    assert f"{summary['experiment_total_sample']:,} participants" in readme
    assert f"{summary['funded_secondary_total_sample']:,} participants" in readme
    assert f"about {summary['funded_secondary_days_full_traffic']} days" in readme


def test_claims_register_contains_every_generated_artifact() -> None:
    claims = (ROOT / "docs" / "claims_register.md").read_text(encoding="utf-8")
    public_artifacts = {
        path.name
        for path in ARTIFACT_DIR.iterdir()
        if path.is_file() and path.name != "intervention_simulations.parquet"
    }
    missing = sorted(name for name in public_artifacts if name not in claims)
    assert not missing, f"Generated artifacts missing from claims register: {missing}"
