from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_DIR, load_config


@dataclass(frozen=True)
class GeneratedPaths:
    applications: Path
    events: Path


def _sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def _event_rows(applications: pd.DataFrame) -> pd.DataFrame:
    stages = [
        ("application_started", "started_at", pd.Series(True, index=applications.index)),
        ("profile_completed", "profile_completed_at", applications["profile_completed"]),
        ("document_submitted", "document_submitted_at", applications["document_submitted"]),
        ("manual_review_started", "manual_review_at", applications["manual_review"]),
        ("verification_completed", "verification_completed_at", applications["verified"]),
        ("verification_failed", "verification_failed_at", applications["verification_failed"]),
        ("account_funded", "first_funded_at", applications["funded"]),
        ("support_contacted", "support_contacted_at", applications["support_contact"]),
    ]
    frames: list[pd.DataFrame] = []
    for event_name, timestamp_column, mask in stages:
        frame = applications.loc[mask, ["application_id", timestamp_column]].copy()
        frame = frame.rename(columns={timestamp_column: "event_at"})
        frame["event_name"] = event_name
        frames.append(frame)
    events = pd.concat(frames, ignore_index=True)
    return events.sort_values(["application_id", "event_at"]).reset_index(drop=True)


def generate_datasets(output_dir: Path = DATA_DIR) -> GeneratedPaths:
    """Create reproducible, fully synthetic onboarding data with no personal information."""
    config = load_config()
    n = int(config["project"]["generated_applications"])
    rng = np.random.default_rng(int(config["project"]["seed"]))

    started_at = pd.Timestamp("2026-01-05", tz="UTC") + pd.to_timedelta(
        rng.integers(0, 26 * 7 * 24 * 60, size=n), unit="m"
    )
    device = rng.choice(["iOS", "Android", "Web"], n, p=[0.46, 0.44, 0.10])
    channel = rng.choice(
        ["Organic", "Referral", "Paid social", "Partner"], n, p=[0.38, 0.22, 0.25, 0.15]
    )
    locale = rng.choice(["fr-FR", "en-GB"], n, p=[0.88, 0.12])
    document_type = rng.choice(
        ["National ID", "Passport", "Residence permit"], n, p=[0.56, 0.31, 0.13]
    )
    network = rng.choice(["Strong", "Standard", "Unstable"], n, p=[0.41, 0.48, 0.11])
    is_returning = rng.random(n) < 0.18

    profile_score = (
        1.72
        + 0.24 * (device == "iOS")
        - 0.28 * (device == "Web")
        - 0.42 * (network == "Unstable")
        + 0.20 * is_returning
        + rng.normal(0, 0.42, n)
    )
    profile_completed = rng.random(n) < _sigmoid(profile_score)

    document_score = (
        0.76
        + 0.24 * (document_type == "National ID")
        - 0.58 * (document_type == "Residence permit")
        - 0.46 * (network == "Unstable")
        - 0.20 * (device == "Web")
        + 0.13 * is_returning
        + rng.normal(0, 0.55, n)
    )
    document_submitted = profile_completed & (rng.random(n) < _sigmoid(document_score))

    manual_review_probability = np.clip(
        0.06 + 0.11 * (document_type == "Residence permit") + 0.05 * (network == "Unstable"),
        0,
        0.40,
    )
    manual_review = document_submitted & (rng.random(n) < manual_review_probability)

    verification_score = (
        0.35
        + 0.28 * (document_type == "National ID")
        - 0.62 * (document_type == "Residence permit")
        - 0.30 * (network == "Unstable")
        - 0.16 * manual_review
        + rng.normal(0, 0.65, n)
    )
    verified = document_submitted & (rng.random(n) < _sigmoid(verification_score))
    verification_failed = document_submitted & ~verified

    funding_score = (
        -0.28
        + 0.28 * (channel == "Referral")
        - 0.21 * (channel == "Paid social")
        + 0.19 * is_returning
        - 0.15 * manual_review
        + rng.normal(0, 0.60, n)
    )
    funded = verified & (rng.random(n) < _sigmoid(funding_score))

    support_probability = np.clip(
        0.035
        + 0.10 * (profile_completed & ~document_submitted)
        + 0.08 * manual_review
        + 0.06 * (network == "Unstable"),
        0,
        0.45,
    )
    support_contact = rng.random(n) < support_probability

    profile_minutes = np.maximum(1, rng.lognormal(1.55, 0.45, n))
    document_minutes = np.maximum(1, rng.lognormal(1.85, 0.60, n))
    verification_minutes = np.maximum(2, rng.lognormal(2.45, 0.70, n))
    # A review creates a real operational delay rather than only a classification flag.
    review_delay_minutes = np.where(manual_review, rng.lognormal(5.90, 0.85, n), 0.0)
    verification_minutes = verification_minutes + review_delay_minutes
    # Funding can occur across several days, which makes the 7-day KPI a true event window.
    funding_minutes = np.maximum(5, rng.lognormal(7.27, 0.95, n))

    def timestamp_after(
        base: pd.DatetimeIndex, minutes: np.ndarray, mask: np.ndarray
    ) -> pd.DatetimeIndex:
        values = base + pd.to_timedelta(minutes, unit="m")
        return values.where(mask)

    profile_completed_at = timestamp_after(started_at, profile_minutes, profile_completed)
    document_submitted_at = timestamp_after(
        profile_completed_at, document_minutes, document_submitted
    )
    manual_review_at = timestamp_after(document_submitted_at, rng.uniform(2, 30, n), manual_review)
    verification_completed_at = timestamp_after(
        document_submitted_at, verification_minutes, verified
    )
    verification_failed_at = timestamp_after(
        document_submitted_at, verification_minutes, verification_failed
    )
    first_funded_at = timestamp_after(verification_completed_at, funding_minutes, funded)
    funded_7d = funded & (first_funded_at <= started_at + np.timedelta64(7, "D"))
    support_contacted_at = timestamp_after(started_at, rng.uniform(5, 240, n), support_contact)

    applications = pd.DataFrame(
        {
            "application_id": [f"FR-{value:07d}" for value in range(1, n + 1)],
            "started_at": started_at,
            "week_start": started_at.tz_localize(None).to_period("W").start_time.date,
            "device": device,
            "acquisition_channel": channel,
            "locale": locale,
            "document_type": document_type,
            "network_quality": network,
            "returning_session": is_returning,
            "profile_completed": profile_completed,
            "document_submitted": document_submitted,
            "verified": verified,
            "verification_failed": verification_failed,
            "manual_review": manual_review,
            "funded": funded,
            "funded_7d": funded_7d,
            "support_contact": support_contact,
            "profile_completed_at": profile_completed_at,
            "document_submitted_at": document_submitted_at,
            "manual_review_at": manual_review_at,
            "verification_completed_at": verification_completed_at,
            "verification_failed_at": verification_failed_at,
            "first_funded_at": first_funded_at,
            "support_contacted_at": support_contacted_at,
        }
    )
    events = _event_rows(applications)

    output_dir.mkdir(parents=True, exist_ok=True)
    applications_path = output_dir / "applications.parquet"
    events_path = output_dir / "events.parquet"
    applications.to_parquet(applications_path, index=False)
    events.to_parquet(events_path, index=False)
    return GeneratedPaths(applications=applications_path, events=events_path)
