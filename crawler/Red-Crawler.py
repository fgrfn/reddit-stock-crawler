import pickle
import praw
from datetime import datetime, timedelta
from collections import Counter
import re
import os
from dotenv import load_dotenv
from crawler.config import get_config
from webhook_notifier import send_top_stocks_webhook

def reddit_crawler():
    run_id = datetime.now().strftime("%y%m%d-%H%M")
    print(f"Crawler run ID: {run_id}")

    config = get_config()
    reddit = praw.Reddit(
        client_id=config["reddit"]["client_id"],
        client_secret=config["reddit"]["client_secret"],
        user_agent=config["reddit"]["user_agent"]
    )

    pattern_template = r"(?<!\w)(\${symbol}|{symbol})(?!\w)"
    with open("data/symbols_list.pkl", "rb") as f:
        all_symbols = pickle.load(f)

    blacklist = {
        'BE', 'GO', 'IT', 'OR', 'SO', 'NO', 'UP', 'FOR', 'ON', 'BY', 'AS',
        'HE', 'AM', 'AN', 'AI', 'DD', 'OP', 'ALL', 'YOU', 'TV', 'PM', 'HAS',
        'ARM', 'ARE', 'PUMP', 'EOD', 'DAY', 'WTF', 'HIT', 'NOW'
    }
    symbols = [s for s in all_symbols if s not in blacklist]

    symbol_counts = Counter()
    subreddit = reddit.subreddit("wallstreetbets")
    cutoff_time = datetime.now() - timedelta(days=1)

    post_count = 0
    for post in subreddit.new(limit=100):
        if datetime.fromtimestamp(post.created_utc) < cutoff_time:
            continue
        post_count += 1
        search_text = f"{post.title} {post.selftext}"
        post.comments.replace_more(limit=30)
        for comment in post.comments.list():
            search_text += f" {comment.body}"
        for symbol in symbols:
            pattern = pattern_template.format(symbol=re.escape(symbol))
            matches = len(re.findall(pattern, search_text))
            if matches > 0:
                symbol_counts[symbol] += matches
                print(f"→ {symbol}: {matches} mentions")

    filtered = {s: c for s, c in symbol_counts.items() if c > 5}
    if filtered:
        data = {'run_id': run_id, 'results': filtered, 'total_posts': post_count}
        os.makedirs('data/pickle', exist_ok=True)
        file_path = f'data/pickle/{run_id}_crawler-results.pkl'
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"\n✅ Results saved in: {file_path}")

        # ✅ Send webhook notification
        send_top_stocks_webhook(filtered, run_id)
    else:
        print("\n🚫 No symbols above threshold found.")

if __name__ == "__main__":
    reddit_crawler()
