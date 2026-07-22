# Data dictionary and event contract

All records are synthetic. The schema intentionally excludes names, contact details, dates of
birth, account numbers and direct identifiers. `application_id` is a generated key used only to
join the two synthetic tables.

## Application table

| Field | Type | Definition |
|---|---|---|
| `application_id` | string | Unique generated application key (`FR-0000001` format) |
| `started_at` | UTC timestamp | Onboarding start |
| `week_start` | date | Week bucket used by the monitoring query |
| `device` | category | iOS, Android or Web |
| `acquisition_channel` | category | Organic, Referral, Paid social or Partner |
| `locale` | category | `fr-FR` or `en-GB` |
| `document_type` | category | National ID, Passport or Residence permit |
| `network_quality` | category | Strong, Standard or Unstable synthetic connection band |
| `returning_session` | boolean | Whether the generated applicant is modelled as returning |
| `profile_completed` | boolean | Profile stage reached |
| `document_submitted` | boolean | Document stage reached |
| `manual_review` | boolean | Application enters the modelled manual-review path |
| `verified` | boolean | Verification succeeds |
| `verification_failed` | boolean | Documents submitted but verification does not succeed |
| `funded` | boolean | A first funding event occurs at any modelled time |
| `funded_7d` | boolean | First funding occurs no later than seven days after start |
| `support_contact` | boolean | A support-contact event occurs |
| `*_at` fields | UTC timestamp | Timestamp for the corresponding reached stage or event |

## Event table

One row per generated application event, ordered by `application_id`, then `event_at`.

| Event | Meaning |
|---|---|
| `application_started` | Onboarding begins |
| `profile_completed` | Required profile fields are completed |
| `document_submitted` | Identity document is submitted |
| `manual_review_started` | Application is routed to manual review |
| `verification_completed` | Verification succeeds |
| `verification_failed` | Verification fails after document submission |
| `account_funded` | First account-funding event; may occur after day seven |
| `support_contacted` | Applicant contacts support |

## Invariants enforced in tests

- Application identifiers are unique and events reference known applications.
- Events are chronological within each application.
- A document cannot be submitted before profile completion; verification cannot succeed before
  submission; funding cannot occur before verification.
- `funded_7d` is recomputed from timestamps and tested as a real seven-day window.
- Manual review creates a measurable verification delay.
- Prohibited PII-shaped columns fail the data contract.

The generated quality report is committed as `artifacts/data_quality.json` and rebuilt in CI.
