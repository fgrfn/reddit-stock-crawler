import requests
from crawler_modules.config import get_config

def send_top_stocks_webhook(results_dict: dict, run_id: str):
    config = get_config()
    webhook_url = config.get("webhook_url")

    if not webhook_url:
        print("🔕 No webhook URL configured. Skipping notification.")
        return

    # Sort results by count descending
    top_items = sorted(results_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    if not top_items:
        print("📭 No results to send via webhook.")
        return

    content_lines = [f"📈 **Top 5 Trending Stocks – Run {run_id}**"]
    for i, (symbol, count) in enumerate(top_items, 1):
        content_lines.append(f"{i}. `{symbol}` – {count} mentions")

    payload = {
        "content": "\n".join(content_lines)
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204 or response.ok:
            print("✅ Webhook notification sent successfully.")
        else:
            print(f"⚠️ Webhook failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Exception during webhook call: {e}")
