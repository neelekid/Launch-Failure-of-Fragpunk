import random
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Realistic complaint text templates based on public feedback
NEGATIVE_TEMPLATES = [
    "The card balance RNG ruins competitive play. Deck cards are way too overpowered.",
    "Servers have terrible netcode and severe desync. I keep getting shot behind walls.",
    "FPS drops and stuttering every time a card ability is activated. Poor optimization.",
    "Matchmaking and SBMM are horrible. Getting destroyed by cheaters and smurfs every match.",
    "Battle pass is predatory and microtransactions are overpriced for a game in this state.",
    "Game constantly crashes to desktop. Unplayable server lag and high ping.",
    "Cards mechanic feels totally RNG and unfair in ranked mode.",
    "Connection lost every two matches. Desync makes gunplay feel unresponsive.",
    "Guns feel okay but card abilities break game balance completely."
]

POSITIVE_TEMPLATES = [
    "Really fun fresh take on hero shooters with the card system!",
    "Gunplay is crisp and art style is super stylish.",
    "Love the card mechanics, brings a fresh tactical twist to FPS.",
    "Great concept, hoping the devs fix the server issues soon."
]


def generate_fragpunk_dataset(num_reviews=1000):
    print(f"[+] Generating {num_reviews} calibrated FragPunk reviews...")
    random.seed(42)
    reviews = []

    for i in range(num_reviews):
        # 65% negative reviews to reflect post-launch collapse
        is_positive = random.random() > 0.65
        voted_up = 1 if is_positive else 0

        if is_positive:
            text = random.choice(POSITIVE_TEMPLATES)
            playtime = round(random.uniform(5.0, 45.0), 2)
        else:
            text = random.choice(NEGATIVE_TEMPLATES)
            playtime = round(random.uniform(0.5, 12.0), 2)

        reviews.append({
            "review_id": 200000000 + i,
            "review_text": text,
            "voted_up": voted_up,
            "votes_up": random.randint(0, 15),
            "playtime_at_review": playtime,
            "timestamp_created": 1710000000 + (i * 300)
        })

    df = pd.DataFrame(reviews)
    output_path = DATA_DIR / "FragPunk_reviews.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[✓] Saved {len(df)} FragPunk reviews to '{output_path}'!")


if __name__ == "__main__":
    generate_fragpunk_dataset()