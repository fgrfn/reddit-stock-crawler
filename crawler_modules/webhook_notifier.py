import os
import requests
from datetime import datetime
from crawler_modules.config import get_config

cfg = get_config()

# Erstelle einmalig den Provider-Namen
AI_PROVIDER = cfg.ai_provider.lower()

# OpenAI-Client konfigurieren
if AI_PROVIDER == "openai":
    import openai
    openai.api_key = cfg.openai_api_key

def build_prompt(symbol: str,
                 mentions_count: int,
                 price_history: list[float],
                 current_price: float) -> str:
    hist_str = ", ".join(f"{p:.2f}" for p in price_history)
    return (
        f"Du bist ein KI-Trader-Assistant.\n"
        f"Symbol: {symbol}\n"
        f"Anzahl Social-Mentions: {mentions_count}\n"
        f"Kursverlauf der letzten Tage: {hist_str}\n"
        f"Aktueller Kurs: {current_price:.2f}\n\n"
        "Gib in zwei Sätzen eine Einschätzung, "
        "ob der Kurs kurzfristig steigen (↑) oder fallen (↓) wird. "
        "Antworte mit '↑' oder '↓' gefolgt von einer kurzen Erklärung."
    )

def predict_trend(symbol: str,
                  mentions_count: int,
                  price_history: list[float],
                  current_price: float) -> str:
    prompt = build_prompt(symbol, mentions_count, price_history, current_price)

    if AI_PROVIDER == "openai":
        resp = openai.ChatCompletion.create(
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
        # Je nach Gemini-Response-Format musst du hier ggf. anpassen:
        return r.json()["candidates"][0]["content"].strip()

    else:
        raise RuntimeError(f"Unbekannter AI Provider: {cfg.ai_provider}")

def notify_webhook(symbol: str, data: dict):
    """
    Sendet das Basis-Payload plus KI-Prognose an den konfigurierten Webhook.
    """
    # 1) Basis-Payload
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "symbol": symbol,
        "trend": data["trend"],
        "timestamp": data["timestamp"],
        "run_timestamp": run_timestamp,
    }

    # 2) KI-Prognose holen
    try:
        payload["prediction"] = predict_trend(
            symbol,
            mentions_count=data["mentions_count"],
            price_history=data["price_history"],
            current_price=data["current_price"]
        )
    except Exception as e:
        # Fallback: ohne Prognose senden
        payload["prediction_error"] = str(e)

    # 3) Abschicken
    resp = requests.post(cfg.webhook_url, json=payload, timeout=5)
    resp.raise_for_status()
