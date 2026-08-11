import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path

# Set aesthetic styling
sns.set_theme(style="darkgrid")
plt.rcParams.update({'font.size': 12})

DATA_DIR = Path("data")
DASHBOARD_DIR = Path("dashboards")
DASHBOARD_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "game_analytics.db"


def plot_lifecycle_collapse(conn):
    """Chart 1: 60-Day Post-Launch CCU Decay Curve."""
    print("[+] Plotting Chart 1: Lifecycle Collapse Curve...")
    df_ccu = pd.read_sql_query("SELECT * FROM daily_player_metrics", conn)

    plt.figure(figsize=(12, 6))
    palette = {"FragPunk": "#E63946", "Call_of_Duty": "#1D3557", "The_Finals": "#457B9D"}

    ax = sns.lineplot(
        data=df_ccu,
        x="days_post_launch",
        y="peak_ccu",
        hue="game_name",
        palette=palette,
        linewidth=2.5,
    )

    plt.title(
        "Launch Lifecycle Collapse: 60-Day Post-Launch CCU Decay",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Days Post-Launch", fontsize=12)
    plt.ylabel("Peak Concurrent Users (CCU)", fontsize=12)
    plt.legend(title="Game", frameon=True)

    # Save output
    output_path = DASHBOARD_DIR / "1_lifecycle_collapse.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f" [✓] Saved '{output_path}'")


def plot_complaint_distribution(conn):
    """Chart 2: Share of Negative Review Complaint Buckets."""
    print("[+] Plotting Chart 2: Root-Cause Complaint Distribution...")
    query = """
    SELECT game_name, complaint_category 
    FROM review_sentiments 
    WHERE voted_up = 0 AND complaint_category != 'Positive / Neutral'
    """
    df_neg = pd.read_sql_query(query, conn)

    # Calculate percentage share per game
    df_counts = (
        df_neg.groupby(["game_name", "complaint_category"])
        .size()
        .reset_index(name="count")
    )
    df_totals = (
        df_neg.groupby("game_name")["complaint_category"]
        .count()
        .reset_index(name="total")
    )
    df_merged = pd.merge(df_counts, df_totals, on="game_name")
    df_merged["pct_share"] = (
        df_merged["count"] / df_merged["total"]
    ) * 100.0

    plt.figure(figsize=(12, 6))
    palette = {"FragPunk": "#E63946", "Call_of_Duty": "#1D3557", "The_Finals": "#457B9D"}

    ax = sns.barplot(
        data=df_merged,
        x="complaint_category",
        y="pct_share",
        hue="game_name",
        palette=palette,
    )

    plt.title(
        "Root-Cause Analysis: Negative Review Share by Category (%)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Complaint Bucket", fontsize=12)
    plt.ylabel("% Share of Negative Reviews", fontsize=12)
    plt.xticks(rotation=15, ha="right")
    plt.legend(title="Game", frameon=True)

    # Save output
    output_path = DASHBOARD_DIR / "2_complaint_distribution.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f" [✓] Saved '{output_path}'")


def plot_playtime_threshold(conn):
    """Chart 3: Average Playtime at Review Submission (Positive vs. Negative)."""
    print("[+] Plotting Chart 3: Playtime at Review Threshold...")
    query = """
    SELECT 
        game_name,
        CASE WHEN voted_up = 1 THEN 'Positive' ELSE 'Negative' END AS review_type,
        AVG(playtime_at_review) AS avg_playtime_hrs
    FROM game_reviews
    GROUP BY game_name, review_type
    """
    df_playtime = pd.read_sql_query(query, conn)

    plt.figure(figsize=(10, 6))
    palette = {"Positive": "#2A9D8F", "Negative": "#E76F51"}

    ax = sns.barplot(
        data=df_playtime,
        x="game_name",
        y="avg_playtime_hrs",
        hue="review_type",
        palette=palette,
    )

    plt.title(
        "Player Frustration Wall: Average Playtime at Review Submission",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Game", fontsize=12)
    plt.ylabel("Average Playtime (Hours)", fontsize=12)
    plt.legend(title="Review Type", frameon=True)

    # Save output
    output_path = DASHBOARD_DIR / "3_playtime_threshold.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f" [✓] Saved '{output_path}'")


def run_dashboard_generator():
    conn = sqlite3.connect(DB_PATH)
    plot_lifecycle_collapse(conn)
    plot_complaint_distribution(conn)
    plot_playtime_threshold(conn)
    conn.close()
    print("\n--- Phase 5 Visualization Deck Created Successfully! ---")


if __name__ == "__main__":
    run_dashboard_generator()