import csv
import os
import requests
from datetime import datetime, timezone, timedelta

CSV_PATH   = "data/crypto_fear_greed.csv"
HEADERS    = ["date", "score", "rating"]
CRYPTO_URL = "https://api.alternative.me/fng/?limit=1&format=json"

def get_utc_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def load_existing_dates():
    if not os.path.exists(CSV_PATH):
        return set()
    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)
        return {row["date"] for row in reader}

def append_row(date, score, rating):
    file_exists = os.path.exists(CSV_PATH)
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"date": date, "score": round(float(score), 2), "rating": rating})

def main():
    today          = get_utc_date()
    existing_dates = load_existing_dates()

    if today in existing_dates:
        print(f"[Crypto] Entry for {today} already exists. Skipping.")
        return

    resp = requests.get(CRYPTO_URL, timeout=10)
    resp.raise_for_status()
    entry  = resp.json()["data"][0]
    score  = entry["value"]
    rating = entry["value_classification"]

    append_row(today, score, rating)
    print(f"[Crypto] Saved: {today} | Score: {score} | Rating: {rating}")

if __name__ == "__main__":
    main()
