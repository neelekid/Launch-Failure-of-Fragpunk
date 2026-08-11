-- ====================================================================
-- PHASE 3 ANALYTICAL QUERIES
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: 30-Day Collapse Rate (CR_30) Calculation
-- Calculates launch peak CCU vs. Day 30 CCU and drop-off percentage
-- --------------------------------------------------------------------
WITH LaunchPeaks AS (
    SELECT 
        game_name,
        peak_ccu AS launch_peak_ccu
    FROM daily_player_metrics
    WHERE days_post_launch = 0
),
Day30Metrics AS (
    SELECT 
        game_name,
        peak_ccu AS day_30_ccu
    FROM daily_player_metrics
    WHERE days_post_launch = 30
)
SELECT 
    l.game_name,
    l.launch_peak_ccu,
    d.day_30_ccu,
    ROUND(((l.launch_peak_ccu - d.day_30_ccu) * 100.0 / l.launch_peak_ccu), 2) AS collapse_rate_pct
FROM LaunchPeaks l
JOIN Day30Metrics d ON l.game_name = d.game_name
ORDER BY collapse_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Sentiment Ratio & Playtime Threshold Summary
-- Analyzes positive/negative review ratios and playtime averages
-- --------------------------------------------------------------------
SELECT 
    game_name,
    COUNT(*) AS total_reviews,
    SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews,
    ROUND(AVG(CASE WHEN voted_up = 0 THEN playtime_at_review ELSE NULL END), 2) AS avg_playtime_negative_hrs,
    ROUND(AVG(CASE WHEN voted_up = 1 THEN playtime_at_review ELSE NULL END), 2) AS avg_playtime_positive_hrs
FROM game_reviews
GROUP BY game_name;