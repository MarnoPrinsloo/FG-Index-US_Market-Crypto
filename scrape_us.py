import csv
import os
from datetime import datetime, timezone, timedelta
import fear_greed

CSV_PATH = "data/us_market_fear_greed.csv"
HEADERS  = ["date", "score", "rating"]

def get_et_date():
    et = timezone(timedelta(hours=-4))  # EDT (UTC-4); change to -5 in winter
    return datetime.now(et).strftime("%Y-%m-%d")

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

def parse_index(index):
    if isinstance(index, dict):
        score  = index.get("value") or index.get("score")
        rating = index.get("value_classification") or index.get("rating") or index.get("description", "N/A")
    else:
        score  = index.value
        rating = index.description
    return score, rating

def main():
    today          = get_et_date()
    existing_dates = load_existing_dates()

    if today in existing_dates:
        print(f"[US Market] Entry for {today} already exists. Skipping.")
        return

    index = fear_greed.get()
    print(f"[US Market] Raw API response: {index}")
    score, rating = parse_index(index)
    append_row(today, score, rating)
    print(f"[US Market] Saved: {today} | Score: {score} | Rating: {rating}")

if __name__ == "__main__":
    main()
