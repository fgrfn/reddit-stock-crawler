# crawler_modules/Red-Crawler.py
import os
import time
import pickle
from crawler_modules.config import get_config
from crawler_modules.webhook_notifier import notify_webhook

def run_reddit_crawler():
    """
    Deine Haupt-Crawler-Logik für Reddit.
    Muss ein Dict zurückgeben:
      { symbol: { 'trend': str,
                  'timestamp': str,
                  'mentions_count': int,
                  'price_history': List[float],
                  'current_price': float }
      }
    """
    # Beispiel-Implementierung (platzhalter)
    # Hier ersetzt du das mit deinem echten Crawling-Code:
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    return {
        'AAPL': {
            'trend': 'up',
            'timestamp': now,
            'mentions_count': 123,
            'price_history': [150.0, 151.2, 152.5],
            'current_price': 153.0
        },
        'TSLA': {
            'trend': 'down',
            'timestamp': now,
            'mentions_count': 98,
            'price_history': [700.0, 695.5, 690.0],
            'current_price': 688.0
        }
    }

def main():
    cfg = get_config()
    # 1) Crawler ausführen
    top_results = run_reddit_crawler()

    # 2) Pickle ablegen
    output_path = cfg.get('pickle_output_path')
    os.makedirs(output_path, exist_ok=True)
    filename = f"results_{int(time.time())}.pkl"
    pickle_file = os.path.join(output_path, filename)
    with open(pickle_file, 'wb') as f:
        pickle.dump(top_results, f)
    print(f"🔢 {len(top_results)} records pickled to {pickle_file}")

    # 3) Webhook-Benachrichtigung
    for symbol, data in top_results.items():
        try:
            notify_webhook(symbol, data)
            print(f"✅ Webhook sent for {symbol}")
        except Exception as e:
            print(f"🚫 Error sending webhook for {symbol}: {e}")

if __name__ == '__main__':
    main()
