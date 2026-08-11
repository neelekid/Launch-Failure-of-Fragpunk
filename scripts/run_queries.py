import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data") / "game_analytics.db"


def execute_analytics():
    conn = sqlite3.connect(DB_PATH)

    print("\n" + "="*50)
    print("--- 30-DAY COLLAPSE RATE (CR_30) ---")
    print("="*50)
    
    cr30_query = """
    WITH LaunchPeaks AS (
        SELECT game_name, peak_ccu AS launch_peak_ccu 
        FROM daily_player_metrics WHERE days_post_launch = 0
    ),
    Day30Metrics AS (
        SELECT game_name, peak_ccu AS day_30_ccu 
        FROM daily_player_metrics WHERE days_post_launch = 30
    )
    SELECT 
        l.game_name,
        l.launch_peak_ccu,
        d.day_30_ccu,
        ROUND(((l.launch_peak_ccu - d.day_30_ccu) * 100.0 / l.launch_peak_ccu), 2) AS collapse_rate_pct
    FROM LaunchPeaks l
    JOIN Day30Metrics d ON l.game_name = d.game_name
    ORDER BY collapse_rate_pct DESC;
    """
    df_cr30 = pd.read_sql_query(cr30_query, conn)
    print(df_cr30.to_string(index=False))

    print("\n" + "="*50)
    print("--- REVIEW SENTIMENT & PLAYTIME ANALYSIS ---")
    print("="*50)
    
    review_query = """
    SELECT 
        game_name,
        COUNT(*) AS total_reviews,
        SUM(CASE WHEN voted_up = 1 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN voted_up = 0 THEN 1 ELSE 0 END) AS negative_reviews,
        ROUND(AVG(CASE WHEN voted_up = 0 THEN playtime_at_review ELSE NULL END), 2) AS avg_playtime_neg_hrs,
        ROUND(AVG(CASE WHEN voted_up = 1 THEN playtime_at_review ELSE NULL END), 2) AS avg_playtime_pos_hrs
    FROM game_reviews
    GROUP BY game_name;
    """
    df_review_summary = pd.read_sql_query(review_query, conn)
    print(df_review_summary.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    execute_analytics()