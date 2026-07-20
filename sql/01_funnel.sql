WITH stage_counts AS (
    SELECT 1 AS stage_order, 'Application started' AS stage, COUNT(*) AS applications
    FROM applications
    UNION ALL
    SELECT 2, 'Profile completed', COUNT(*) FILTER (WHERE profile_completed)
    FROM applications
    UNION ALL
    SELECT 3, 'Document submitted', COUNT(*) FILTER (WHERE document_submitted)
    FROM applications
    UNION ALL
    SELECT 4, 'Verification completed', COUNT(*) FILTER (WHERE verified)
    FROM applications
    UNION ALL
    SELECT 5, 'Funded within 7 days', COUNT(*) FILTER (WHERE funded_7d)
    FROM applications
)
SELECT
    stage_order,
    stage,
    applications,
    ROUND(100.0 * applications / FIRST_VALUE(applications) OVER (ORDER BY stage_order), 2)
        AS start_conversion_pct,
    ROUND(
        100.0 * applications
        / LAG(applications) OVER (ORDER BY stage_order),
        2
    ) AS previous_stage_conversion_pct
FROM stage_counts
ORDER BY stage_order;

