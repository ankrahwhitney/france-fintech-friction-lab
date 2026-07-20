SELECT
    week_start,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(funded_7d::INT), 2) AS funded_7d_pct,
    ROUND(100.0 * AVG(manual_review::INT), 2) AS manual_review_pct,
    ROUND(100.0 * AVG(support_contact::INT), 2) AS support_contact_pct
FROM applications
GROUP BY week_start
ORDER BY week_start;

