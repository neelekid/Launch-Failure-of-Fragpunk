import datetime
import numpy as np
import pandas as pd
from pathlib import Path

# --- Configuration ---
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Define games and launch dates for our comparative post-mortem baseline
GAMES_CONFIG = {
    "FragPunk": {
        "app_id": 2890730,
        "launch_peak_ccu": 85000,
        "decay_rate": 0.06,  # Rapid decay (Failure case)
        "floor_ccu": 3200
    },
    "Call_of_Duty": {
        "app_id": 1938090,
        "launch_peak_ccu": 190000,
        "decay_rate": 0.012, # Strong retention baseline
        "floor_ccu": 75000
    },
    "The_Finals": {
        "app_id": 2073850,
        "launch_peak_ccu": 242000,
        "decay_rate": 0.035, # Moderate competitor decay
        "floor_ccu": 22000
    }
}

DAYS_POST_LAUNCH = 60


def generate_post_launch_ccu_data() -> pd.DataFrame:
    """
    Generates 60-day post-launch daily peak CCU datasets 
    for target and competitor baseline titles.
    """
    print("[+] Building 60-day post-launch CCU daily dataset...")
    all_ccu_records = []

    # Use a fixed start date for alignment
    base_launch_date = datetime.date(2025, 3, 1)

    np.random.seed(42)  # For reproducible realistic noise

    for game_name, config in GAMES_CONFIG.items():
        peak = config["launch_peak_ccu"]
        decay = config["decay_rate"]
        floor = config["floor_ccu"]

        for day in range(DAYS_POST_LAUNCH):
            current_date = base_launch_date + datetime.timedelta(days=day)

            # Exponential decay model with weekend spikes & random noise
            decayed_ccu = (peak - floor) * np.exp(-decay * day) + floor
            
            # Weekend boost multiplier (Saturday/Sunday)
            is_weekend = current_date.weekday() in (5, 6)
            weekend_boost = 1.18 if is_weekend else 1.0

            # Daily random variance (+/- 5%)
            daily_noise = np.random.uniform(0.95, 1.05)

            final_ccu = int(decayed_ccu * weekend_boost * daily_noise)

            all_ccu_records.append({
                "game_name": game_name,
                "app_id": config["app_id"],
                "days_post_launch": day,
                "date": current_date.isoformat(),
                "peak_ccu": final_ccu
            })

    df = pd.DataFrame(all_ccu_records)
    return df


if __name__ == "__main__":
    df_ccu = generate_post_launch_ccu_data()
    output_file = DATA_DIR / "daily_ccu_data.csv"
    df_ccu.to_csv(output_file, index=False, encoding="utf-8")
    
    print(f"[✓] Successfully generated {len(df_ccu)} daily CCU records!")
    print(f"[✓] Saved to '{output_file}'")
    print("\n--- Phase 2 Complete! ---")