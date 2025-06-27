import pickle
import praw
from datetime import datetime, timedelta
from collections import Counter
import re
import os
from dotenv import load_dotenv

def reddit_crawler():
    run_id = datetime.now().strftime("%y%m%d-%H%M")
    print(f"Crawler run ID: {run_id}")

    load_dotenv(dotenv_path='secret.env')
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

    pattern_template = r'(?<!\w)(\${symbol}|{symbol})(?!\w)'
    with open('symbols_list.pkl', 'rb') as f:
        all_symbols = pickle.load(f)

    blacklist = {
        'BE', 'GO', 'IT', 'OR', 'SO', 'NO', 'UP', 'FOR', 'ON', 'BY', 'AS',
        'HE', 'AM', 'AN', 'AI', 'DD', 'OP', 'ALL', 'YOU', 'TV', 'PM', 'HAS',
        'ARM', 'ARE', 'PUMP', 'EOD', 'DAY', 'WTF', 'HIT', 'NOW'
    }
    symbols = [s for s in all_symbols if s not in blacklist]

    symbol_counts = Counter()
    subreddit = reddit.subreddit('wallstreetbets')
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
                print(f"→ {symbol}: {matches} matches")

    filtered = {s: c for s, c in symbol_counts.items() if c > 5}
    if filtered:
        data = {'run_id': run_id, 'results': filtered, 'total_posts': post_count}
        os.makedirs('pickle', exist_ok=True)
        with open(f'pickle/{run_id}_crawler_result.pkl', 'wb') as f:
            pickle.dump(data, f)
        print(f"\n✅ Results saved to: {run_id}_crawler_result.pkl")
    else:
        print("\n🚫 No matches found above the threshold.")

if __name__ == "__main__":
    reddit_crawler()
