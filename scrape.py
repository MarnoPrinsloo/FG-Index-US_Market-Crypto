import csv
import os
import requests
from datetime import datetime, timezone, timedelta
import fear_greed

# File paths
US_CSV_PATH = "data/us_market_fear_greed.csv"
CRYPTO_CSV_PATH = "data/crypto_fear_greed.csv"
HEADERS = ["date", "score", "rating"]

# Alternative.me crypto fear & greed API (free, no key required)
CRYPTO_API_URL = "https://api.alternative.me/fng/?limit=1&format=json"

def get_et_date():
    et = timezone(timedelta(hours=-4))  # EDT (UTC-4); change to -5 in winter
    return datetime.now(et).strftime("%Y-%m-%d")

def load_existing_dates(csv_path):
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        return {row["date"] for row in reader}

def append_row(csv_path, date, score, rating):
    file_exists = os.path.exists(csv_path)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"date": date, "score": round(float(score), 2), "rating": rating})

def parse_us_index(index):
    """Handle both object and dict return types across fear-greed library versions."""
    if isinstance(index, dict):
        score = index.get("value") or index.get("score")
        rating = index.get("value_classification") or index.get("rating") or index.get("description", "N/A")
    else:
        score = index.value
        rating = index.description
    return score, rating

def get_crypto_index():
    """Fetch crypto fear & greed from Alternative.me (free, no API key needed)."""
    response = requests.get(CRYPTO_API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    entry = data["data"][0]
    score = entry["value"]
    rating = entry["value_classification"]
    return score, rating

def scrape_us_market(today):
    """Scrape CNN US market fear & greed index."""
    existing_dates = load_existing_dates(US_CSV_PATH)
    if today in existing_dates:
        print(f"[US Market] Entry for {today} already exists. Skipping.")
        return

    index = fear_greed.get()
    print(f"[US Market] Raw API response: {index}")
    score, rating = parse_us_index(index)
    append_row(US_CSV_PATH, today, score, rating)
    print(f"[US Market] Saved: {today} | Score: {score} | Rating: {rating}")

def scrape_crypto(today):
    """Scrape Alternative.me crypto fear & greed index."""
    existing_dates = load_existing_dates(CRYPTO_CSV_PATH)
    if today in existing_dates:
        print(f"[Crypto] Entry for {today} already exists. Skipping.")
        return

    score, rating = get_crypto_index()
    append_row(CRYPTO_CSV_PATH, today, score, rating)
    print(f"[Crypto] Saved: {today} | Score: {score} | Rating: {rating}")

def main():
    today = get_et_date()
    scrape_us_market(today)
    scrape_crypto(today)

if __name__ == "__main__":
    main()
