import time
import requests
import pandas as pd
from pathlib import Path

# --- Configuration ---
# Steam AppIDs: FragPunk = 2890730, Call of Duty = 1938090
GAMES = {
    "FragPunk": 2890730,
    "Call_of_Duty": 1938090
}

REVIEWS_PER_GAME = 1000  # Number of reviews to fetch per game for our first batch
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)  # Ensures 'data' folder exists


def fetch_steam_reviews(app_id: int, max_reviews: int = 1000) -> pd.DataFrame:
    """
    Fetches reviews from Steam API using cursor pagination.
    """
    print(f"\n[+] Starting extraction for AppID: {app_id}...")
    reviews_list = []
    cursor = "*"  # Steam API uses '*' to request the first page
    
    while len(reviews_list) < max_reviews:
        # Steam API review endpoint
        url = f"https://store.steampowered.com/appreviews/{app_id}"
        params = {
            "json": 1,
            "filter": "all",
            "language": "english",
            "review_type": "all",
            "purchase_type": "all",
            "num_per_page": 100,  # Max allowed per request by Steam
            "cursor": cursor
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Check if request was successful
            if data.get("success") != 1:
                print(f"[!] API call failed for AppID {app_id}")
                break
                
            fetched_reviews = data.get("reviews", [])
            if not fetched_reviews:
                print("[i] No more reviews available.")
                break
                
            # Extract key fields from each review
            for item in fetched_reviews:
                reviews_list.append({
                    "review_id": item.get("recommendationid"),
                    "review_text": item.get("review"),
                    "voted_up": item.get("voted_up"),  # True = Positive, False = Negative
                    "votes_up": item.get("votes_up"),    # Helpful votes
                    "playtime_at_review": item.get("author", {}).get("playtime_at_review", 0) / 60.0, # Hours
                    "timestamp_created": item.get("timestamp_created")
                })
            
            print(f" -> Downloaded {len(reviews_list)} / {max_reviews} reviews...")
            
            # Get next page cursor
            new_cursor = data.get("cursor")
            if new_cursor == cursor or not new_cursor:
                break
            cursor = new_cursor
            
            # Rate Limiting: Sleep 1 second so Steam doesn't block our IP
            time.sleep(1)
            
        except Exception as e:
            print(f"[!] Error occurred: {e}")
            break

    df = pd.DataFrame(reviews_list)
    return df


if __name__ == "__main__":
    for game_name, app_id in GAMES.items():
        df_reviews = fetch_steam_reviews(app_id, max_reviews=REVIEWS_PER_GAME)
        
        # Save output to CSV file in data/ folder
        output_file = DATA_DIR / f"{game_name}_reviews.csv"
        df_reviews.to_csv(output_file, index=False, encoding="utf-8")
        print(f"[✓] Saved {len(df_reviews)} reviews to '{output_file}'")

    print("\n--- Phase 2 Review Extraction Complete! ---")
    