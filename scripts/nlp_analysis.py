import re
import sqlite3
import pandas as pd
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DB_PATH = Path("data") / "game_analytics.db"

# --- 5 Key Complaint Buckets (Keywords & N-Grams) ---
COMPLAINT_BUCKETS = {
    "Netcode & Servers": [
        "netcode", "server", "lag", "ping", "desync", "disconnect", "packet loss", "latency", "host"
    ],
    "Gameplay & Card Balance": [
        "card", "cards", "rng", "overpowered", "op", "balance", "ability", "gunplay", "deck", "mechanic"
    ],
    "Matchmaking & Cheaters": [
        "matchmaking", "sbmm", "cheater", "hacker", "smurf", "queue", "wait time", "bot", "ranked"
    ],
    "Monetization": [
        "microtransaction", "battle pass", "battlepass", "skin", "overpriced", "store", "greedy", "price"
    ],
    "Performance & Technical": [
        "crash", "stutter", "fps", "performance", "optimization", "unoptimized", "gpu", "black screen"
    ]
}


def clean_text(text: str) -> str:
    """Preprocesses text by lowercasing and stripping punctuation/noise."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # remove URLs
    text = re.sub(r'[^a-z\s]', '', text)                                    # keep letters only
    return text.strip()


def classify_complaint(text_clean: str) -> str:
    """Matches review text against defined complaint keyword buckets."""
    counts = {bucket: 0 for bucket in COMPLAINT_BUCKETS}
    
    for bucket, keywords in COMPLAINT_BUCKETS.items():
        for kw in keywords:
            if kw in text_clean:
                counts[bucket] += 1
                
    # Return bucket with maximum keyword matches; default to 'Other / General'
    best_bucket = max(counts, key=counts.get)
    if counts[best_bucket] > 0:
        return best_bucket
    return "Other / General Gameplay"


def run_nlp_pipeline():
    print("[+] Connecting to SQL Database for NLP Processing...")
    conn = sqlite3.connect(DB_PATH)
    
    # Load all reviews from database
    df_reviews = pd.read_sql_query("SELECT * FROM game_reviews", conn)
    
    print("[+] Running VADER Sentiment Analysis...")
    analyzer = SentimentIntensityAnalyzer()
    
    # Calculate VADER compound sentiment score (-1.0 to +1.0)
    df_reviews["cleaned_text"] = df_reviews["review_text"].apply(clean_text)
    df_reviews["vader_compound"] = df_reviews["review_text"].apply(
        lambda txt: analyzer.polarity_scores(str(txt))["compound"]
    )
    
    print("[+] Categorizing Negative Review Root Causes...")
    # Classify complaints specifically for negative reviews (voted_up == False / 0)
    df_reviews["complaint_category"] = "Positive / Neutral"
    neg_mask = df_reviews["voted_up"] == 0
    df_reviews.loc[neg_mask, "complaint_category"] = df_reviews.loc[neg_mask, "cleaned_text"].apply(classify_complaint)
    
    # Save processed NLP table back into SQLite
    df_reviews.to_sql("review_sentiments", conn, if_exists="replace", index=False)
    conn.close()
    
    print("[✓] NLP Analysis Complete! Results stored in table 'review_sentiments'.\n")
    
    # --- Print Root Cause Breakdown ---
    print("=" * 65)
    print("--- NEGATIVE REVIEW COMPLAINT BREAKDOWN (% SHARE) ---")
    print("=" * 65)
    
    df_negatives = df_reviews[df_reviews["voted_up"] == 0]
    breakdown = (
        pd.crosstab(
            df_negatives["game_name"], 
            df_negatives["complaint_category"], 
            normalize="index"
        ) * 100
    ).round(2)
    
    print(breakdown.to_string())


if __name__ == "__main__":
    run_nlp_pipeline()