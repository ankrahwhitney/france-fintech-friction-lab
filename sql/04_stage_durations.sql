WITH stamped AS (
    SELECT
        application_id,
        MAX(CASE WHEN event_name = 'application_started' THEN event_at END) AS started,
        MAX(CASE WHEN event_name = 'profile_completed' THEN event_at END) AS profile_done,
        MAX(CASE WHEN event_name = 'document_submitted' THEN event_at END) AS documents_done,
        MAX(CASE WHEN event_name = 'verification_completed' THEN event_at END) AS verified_done,
        MAX(CASE WHEN event_name = 'account_funded' THEN event_at END) AS funded_done
    FROM events
    GROUP BY application_id
),
durations AS (
    SELECT 1 AS transition_order, 'Start to profile' AS transition,
           DATE_DIFF('minute', started, profile_done) AS minutes
    FROM stamped WHERE profile_done IS NOT NULL
    UNION ALL
    SELECT 2, 'Profile to documents', DATE_DIFF('minute', profile_done, documents_done)
    FROM stamped WHERE documents_done IS NOT NULL
    UNION ALL
    SELECT 3, 'Documents to verified', DATE_DIFF('minute', documents_done, verified_done)
    FROM stamped WHERE verified_done IS NOT NULL
    UNION ALL
    SELECT 4, 'Verified to funded', DATE_DIFF('minute', verified_done, funded_done)
    FROM stamped WHERE funded_done IS NOT NULL
)
SELECT
    transition_order,
    transition,
    COUNT(*) AS applications,
    ROUND(MEDIAN(minutes), 1) AS median_minutes,
    ROUND(QUANTILE_CONT(minutes, 0.90), 1) AS p90_minutes
FROM durations
GROUP BY transition_order, transition
ORDER BY transition_order;
