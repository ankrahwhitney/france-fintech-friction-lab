WITH segments AS (
    SELECT 'Device' AS dimension, device AS segment, * FROM applications
    UNION ALL
    SELECT 'Acquisition channel', acquisition_channel, * FROM applications
    UNION ALL
    SELECT 'Document type', document_type, * FROM applications
    UNION ALL
    SELECT 'Network quality', network_quality, * FROM applications
    UNION ALL
    SELECT 'Locale', locale, * FROM applications
)
SELECT
    dimension,
    segment,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(profile_completed::INT), 2) AS profile_completion_pct,
    ROUND(100.0 * AVG(document_submitted::INT), 2) AS document_submission_pct,
    ROUND(100.0 * AVG(verified::INT), 2) AS verification_pct,
    ROUND(100.0 * AVG(funded_7d::INT), 2) AS funded_7d_pct,
    ROUND(100.0 * AVG(manual_review::INT), 2) AS manual_review_pct,
    ROUND(100.0 * AVG(support_contact::INT), 2) AS support_contact_pct
FROM segments
GROUP BY dimension, segment
HAVING COUNT(*) >= 250
ORDER BY dimension, funded_7d_pct DESC;

