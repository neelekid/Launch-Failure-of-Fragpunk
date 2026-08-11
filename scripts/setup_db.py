import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "game_analytics.db"


def initialize_database():
    """
    Creates SQL tables and populates them with data from CSV files.
    """
    print("[+] Initializing SQLite Database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. Load CCU Data into SQL ---
    ccu_csv = DATA_DIR / "daily_ccu_data.csv"
    if ccu_csv.exists():
        df_ccu = pd.read_csv(ccu_csv)
        df_ccu.to_sql("daily_player_metrics", conn, if_exists="replace", index=False)
        print(f" [✓] Loaded {len(df_ccu)} rows into 'daily_player_metrics' table.")

    # --- 2. Load Reviews into SQL ---
    reviews_files = {
        "FragPunk": DATA_DIR / "FragPunk_reviews.csv",
        "Call_of_Duty": DATA_DIR / "Call_of_Duty_reviews.csv",
        "The_Finals": DATA_DIR / "The_Finals_reviews.csv"
    }

    all_reviews = []
    for game_name, file_path in reviews_files.items():
        if file_path.exists():
            df_rev = pd.read_csv(file_path)
            df_rev["game_name"] = game_name
            all_reviews.append(df_rev)

    if all_reviews:
        df_combined_reviews = pd.concat(all_reviews, ignore_index=True)
        df_combined_reviews.to_sql("game_reviews", conn, if_exists="replace", index=False)
        print(f" [✓] Loaded {len(df_combined_reviews)} rows into 'game_reviews' table.")

    conn.commit()
    conn.close()
    print(f"[✓] Database successfully created at '{DB_PATH}'!")


if __name__ == "__main__":
    initialize_database()