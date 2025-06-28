# crawler_modules/webhook_notifier.py
import os
import requests
from datetime import datetime
from crawler_modules.config import get_config

cfg = get_config()
AI_PROVIDER = cfg.ai_provider.lower()

# Configure OpenAI client
if AI_PROVIDER == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=cfg.openai_api_key)

def build_prompt(symbol: str, mentions_count: int, price_history: list[float], current_price: float) -> str:
    hist_str = ", ".join(f"{p:.2f}" for p in price_history)
    return (
        f"You are a trading assistant AI.\n"
        f"Symbol: {symbol}\n"
        f"Mentions: {mentions_count}\n"
        f"Price history: {hist_str}\n"
        f"Current price: {current_price:.2f}\n\n"
        "Predict the short-term trend: will it rise (↑) or fall (↓)? "
        "Reply with '↑' or '↓' and a short reason."
    )

def predict_trend(symbol: str, mentions_count: int, price_history: list[float], current_price: float) -> str:
    prompt = build_prompt(symbol, mentions_count, price_history, current_price)

    if AI_PROVIDER == "openai":
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        return resp.choices[0].message.content.strip()

    elif AI_PROVIDER == "gemini":
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-pro:generateContent"
            f"?key={cfg.gemini_api_key}"
        )
        body = {
            "prompt": prompt,
            "temperature": 0.3,
            "maxOutputTokens": 50,
        }
        r = requests.post(url, json=body, timeout=10)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"].strip()

    else:
        raise RuntimeError(f"Unknown AI Provider: {cfg.ai_provider}")

def notify_webhook(symbol: str, data: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trend = data["trend"]
    mentions = data["mentions_count"]
    price_hist = data["price_history"]
    current_price = data["current_price"]

    try:
        prediction = predict_trend(symbol, mentions, price_hist, current_price)
    except Exception as e:
        prediction = f"Prediction error: {str(e)}"

    content = (
        f"**📈 Reddit Stock Alert**\n"
        f"**Symbol:** `{symbol}`\n"
        f"**Mentions:** `{mentions}`\n"
        f"**Trend:** `{trend}`\n"
        f"**Current Price:** `${current_price:.2f}`\n"
        f"**Prediction:** `{prediction}`\n"
        f"_Generated: {timestamp}_"
    )

    response = requests.post(cfg.webhook_url, json={"content": content}, timeout=10)
    response.raise_for_status()
