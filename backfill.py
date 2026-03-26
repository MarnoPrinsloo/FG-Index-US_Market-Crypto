"""
One-time backfill script — run locally, not via GitHub Actions.
Fetches historical Fear & Greed data from 2019-01-01 to today
and writes two CSVs:
  data/us_market_fear_greed.csv
  data/crypto_fear_greed.csv
"""

import csv
import os
import requests
from datetime import datetime, timezone, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
START_DATE         = "2019-01-01"
US_CSV_PATH        = "data/us_market_fear_greed.csv"
CRYPTO_CSV_PATH    = "data/crypto_fear_greed.csv"
HEADERS            = ["date", "score", "rating"]

CNN_API_URL        = f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata/{START_DATE}"
CRYPTO_API_URL     = "https://api.alternative.me/fng/?limit=0&format=json"

# ── Helpers ───────────────────────────────────────────────────────────────────

def score_to_rating(score):
    """Convert a numeric score to a rating label (matches CNN's labels)."""
    if score <= 25:   return "Extreme Fear"
    elif score <= 44: return "Fear"
    elif score <= 55: return "Neutral"
    elif score <= 75: return "Greed"
    else:             return "Extreme Greed"

def write_csv(path, rows):
    """Write sorted rows to CSV, skipping duplicates by date."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    seen = {}
    for row in rows:
        seen[row["date"]] = row   # last write wins for any duplicate dates
    sorted_rows = sorted(seen.values(), key=lambda r: r["date"])
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(sorted_rows)
    print(f"  Written {len(sorted_rows)} rows → {path}")

# ── US Market (CNN) ───────────────────────────────────────────────────────────

def backfill_us():
    print(f"\n[US Market] Fetching from CNN API (start: {START_DATE})...")
    resp = requests.get(CNN_API_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    data = resp.json()

    # CNN returns a list of [unix_ms_timestamp, score] pairs
    raw = data.get("fear_and_greed_historical", {}).get("data", [])
    if not raw:
        # Fallback key names seen in some API versions
        raw = data.get("data", [])

    print(f"  Received {len(raw)} raw data points")

    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    rows = []
    for entry in raw:
        # Entry is either a dict with 'x'/'y' keys, or a two-element list
        if isinstance(entry, dict):
            ts_ms = entry.get("x") or entry.get("timestamp")
            score  = entry.get("y") or entry.get("value")
            rating = entry.get("rating") or score_to_rating(float(score))
        else:
            ts_ms, score = entry[0], entry[1]
            rating = score_to_rating(float(score))

        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        if dt < start_dt:
            continue
        rows.append({
            "date":   dt.strftime("%Y-%m-%d"),
            "score":  round(float(score), 2),
            "rating": rating
        })

    write_csv(US_CSV_PATH, rows)

# ── Crypto (Alternative.me) ───────────────────────────────────────────────────

def backfill_crypto():
    print(f"\n[Crypto] Fetching all history from Alternative.me...")
    resp = requests.get(CRYPTO_API_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    print(f"  Received {len(data)} raw data points")

    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    rows = []
    for entry in data:
        dt = datetime.fromtimestamp(int(entry["timestamp"]), tz=timezone.utc)
        if dt < start_dt:
            continue
        rows.append({
            "date":   dt.strftime("%Y-%m-%d"),
            "score":  round(float(entry["value"]), 2),
            "rating": entry["value_classification"]
        })

    write_csv(CRYPTO_CSV_PATH, rows)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Fear & Greed Historical Backfill")
    print(f"  Start date: {START_DATE}")
    print("=" * 55)

    backfill_us()
    backfill_crypto()

    print("\nDone! Now push the data/ folder to GitHub:")
    print("  git add data/")
    print('  git commit -m "feat: add historical fear & greed data from 2019"')
    print("  git push origin main")

if __name__ == "__main__":
    main()
