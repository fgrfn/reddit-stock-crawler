# crawler_modules/Red-Crawler.py

import os
import time
import pickle
import praw
import pandas as pd
import sys
from crawler_modules.config import get_config
from crawler_modules.webhook_notifier import notify_webhook

def run_reddit_crawler():
    cfg = get_config()

    # Init Reddit client
    reddit = praw.Reddit(
        client_id=cfg.reddit_client_id,
        client_secret=cfg.reddit_client_secret,
        user_agent=cfg.reddit_user_agent
    )

    # Load symbol list from Excel
    excel_path = "data/NAS-NYSE-cleaned.xlsx"

    try:
        symbols_df = pd.read_excel(excel_path)
        print(f"📥 Loaded Excel file: {excel_path}")
        print(f"🧪 Columns found: {symbols_df.columns.tolist()}")

        # Try different column name variants
        possible_columns = ["ACT Symbol", "Symbol", "Ticker"]
        symbol_column = next((col for col in possible_columns if col in symbols_df.columns), None)

        if not symbol_column:
            print("❌ No valid symbol column found in Excel file.")
            sys.exit(1)

        symbols = set(symbols_df[symbol_column].dropna().astype(str).str.upper())
        print(f"✅ {len(symbols)} symbols loaded from column: {symbol_column}")

    except Exception as e:
        print(f"❌ Error reading Excel file '{excel_path}': {e}")
        sys.exit(1)

    # Apply blacklist from original Heise article
    blacklist = {
        "FOR", "ON", "ARE", "YOU", "ALL", "GO", "IT", "AS", "OR",
        "BY", "TO", "IN", "OUT", "GET", "HAS", "WAS", "HAD", "JUNE", "MAY", "AI"
    }
    symbols -= blacklist

    mention_counter = {}
    subreddits = ["wallstreetbets", "wallstreetbetsGER"]
    posts_per_subreddit = 100
    logs = []

    print("\n🔍 Scanning Reddit posts...")
    for sub in subreddits:
        print(f"🔸 Checking /r/{sub}...")
        for submission in reddit.subreddit(sub).new(limit=posts_per_subreddit):
            title = submission.title.upper()
            for symbol in symbols:
                if f"${symbol}" in title or f" {symbol} " in title:
                    mention_counter[symbol] = mention_counter.get(symbol, 0) + 1
                    log = f"→ {symbol}: {mention_counter[symbol]} Treffer"
                    print(log)
                    logs.append(log)

    # Take top 5 mentioned symbols
    top_symbols = sorted(mention_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    result = {}
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    print("\n📊 Top 5 meistgenannte Symbole:")
    for symbol, count in top_symbols:
        print(f"→ {symbol}: {count} Treffer")
        result[symbol] = {
            "trend": "neutral",
            "timestamp": now,
            "mentions_count": count,
            "price_history": [],
            "current_price": 0.0
        }

    # Optional: write CSV export for reference
    pd.DataFrame([
        {"Symbol": s, "Mentions": c} for s, c in sorted(mention_counter.items(), key=lambda x: x[1], reverse=True)
    ]).to_csv("data/logs/full_mention_log.csv", index=False)

    return result

def main():
    cfg = get_config()

    # Run crawler
    top_results = run_reddit_crawler()

    # Save results to pickle
    output_path = cfg.get('pickle_output_path')
    os.makedirs(output_path, exist_ok=True)
    filename = f"results_{int(time.time())}.pkl"
    pickle_file = os.path.join(output_path, filename)
    with open(pickle_file, 'wb') as f:
        pickle.dump(top_results, f)
    print(f"🔢 {len(top_results)} records pickled to {pickle_file}")

    # Send Discord webhooks
    for symbol, data in top_results.items():
        try:
            notify_webhook(symbol, data)
            print(f"✅ Webhook sent for {symbol}")
        except Exception as e:
            print(f"🚫 Error sending webhook for {symbol}: {e}")

if __name__ == '__main__':
    main()
