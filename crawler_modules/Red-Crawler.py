# crawler_modules/Red-Crawler.py

import os
import time
import pickle
import praw
import pandas as pd
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

    # Load symbol list (NASDAQ/NYSE)
    symbols_df = pd.read_excel("data/NAS-NYSE-cleaned.xlsx")
    symbols = set(symbols_df["ACT Symbol"].dropna().str.upper())

    mention_counter = {}
    subreddits = ["wallstreetbets", "stocks", "investing"]
    posts_per_subreddit = 100

    for sub in subreddits:
        for submission in reddit.subreddit(sub).new(limit=posts_per_subreddit):
            title = submission.title.upper()
            for symbol in symbols:
                if f"${symbol}" in title or f" {symbol} " in title:
                    mention_counter[symbol] = mention_counter.get(symbol, 0) + 1
                    print(f"→ {symbol}: {mention_counter[symbol]} Treffer")

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
