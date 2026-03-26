import csv
import os
from datetime import datetime, timezone, timedelta
import fear_greed

# File path
CSV_PATH = "data/fear_greed.csv"
HEADERS = ["date", "score", "rating"]

def get_et_date():
    et = timezone(timedelta(hours=-4))  # EDT (UTC-4); change to -5 for EST in winter
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
        writer.writerow({"date": date, "score": round(score, 2), "rating": rating})

def main():
    today = get_et_date()
    existing_dates = load_existing_dates()

    if today in existing_dates:
        print(f"Entry for {today} already exists. Skipping.")
        return

    index = fear_greed.get()
    score = index.value
    rating = index.description

    append_row(today, score, rating)
    print(f"Saved: {today} | Score: {score} | Rating: {rating}")

if __name__ == "__main__":
    main()
