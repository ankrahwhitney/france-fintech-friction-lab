WITH verification_paths AS (
    SELECT
        CASE WHEN manual_review THEN 'Manual review' ELSE 'Straight-through' END
            AS verification_path,
        DATE_DIFF('minute', document_submitted_at, verification_completed_at) AS minutes
    FROM applications
    WHERE verified
)
SELECT
    verification_path,
    COUNT(*) AS applications,
    ROUND(MEDIAN(minutes), 1) AS median_minutes,
    ROUND(QUANTILE_CONT(minutes, 0.90), 1) AS p90_minutes,
    ROUND(QUANTILE_CONT(minutes, 0.95), 1) AS p95_minutes
FROM verification_paths
GROUP BY verification_path
ORDER BY median_minutes;
