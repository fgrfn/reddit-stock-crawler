# 🧠 Reddit Stock Crawler

A Python-based tool to scan Reddit posts for NASDAQ/NYSE stock tickers, track mention trends, and send alerts via Discord – now with AI-powered predictions using OpenAI or Gemini.

---

## 🚀 Features

✅ Scans Reddit posts for ticker symbols from a verified stock list  
✅ Supports `r/wallstreetbets`, `r/stocks`, and `r/investing`  
✅ Filters out common false positives via a **blacklist**  
✅ Counts Reddit mentions and identifies top trending stocks  
✅ Stores the complete mention log as a CSV (`full_mention_log.csv`)  
✅ Saves pickled result files for archival and analysis  
✅ Sends alerts via **Discord Webhooks**  
✅ Adds AI prediction using **OpenAI** or **Gemini**  
✅ Cronjob and systemd support for automation  
✅ Optional **Streamlit dashboard** for data visualization  

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/reddit-stock-crawler.git
cd reddit-stock-crawler
chmod +x install_reddit_crawler.sh
./install_reddit_crawler.sh
```

During installation, you’ll be prompted to provide API keys, a Discord webhook, and define your scheduling preferences.

---

## 📁 Project Structure

```
reddit-stock-crawler/
├── install_reddit_crawler.sh         # Installer with cron & systemd support
├── run_reddit_crawler.sh            # Manual runner
├── config.yaml                      # All credentials & settings
├── data/
│   ├── NAS-NYSE-cleaned.xlsx        # Ticker list
│   ├── logs/full_mention_log.csv    # CSV with all symbol mentions
│   └── pickle/                      # Pickled top results (e.g. 5 records)
├── crawler_modules/
│   ├── Red-Crawler.py               # Main Reddit crawler
│   ├── webhook_notifier.py          # Discord + AI notification logic
│   ├── config.py                    # Configuration loader
│   ├── cleanup_pickle_files.py      # Auto-delete old pickle files
│   └── upload_to_gsheets.py         # Optional Google Sheets export
└── dashboard/
    └── dashboard.py                 # Streamlit visualization (optional)
```

---

## 🔄 Automation

- 🕒 **Cronjob** support: schedule regular crawler execution (hourly, daily, etc.)
- 🖥️ **Systemd** unit: optional service to auto-launch the Streamlit dashboard on boot

---

## 📦 Output

- `data/logs/full_mention_log.csv`: all ticker mentions for full transparency  
- `data/pickle/results_*.pkl`: top 5 symbols of each run  
- Discord message example:

```
📈 Reddit Stock Alert
Symbol: AAPL
Mentions: 123
Trend: up
Current Price: $153.00
Prediction: ↑
The short-term trend for AAPL seems to be rising due to a growing number of mentions and an upward price trend.
Generated: 2025-06-28 03:10:12
```

---

## 🔐 API Access

Required:
- Reddit API credentials (client ID, secret, user agent)
- OpenAI or Gemini API key
- Discord Webhook URL  
Optional:
- Google Sheets credentials (service account key)

---

## 🤖 AI Prediction

The AI model analyzes:
- Reddit mention volume  
- Price history  
- Current stock price  
Then returns a **↑ or ↓ trend symbol** with a short rationale.

---

## 🧹 Cleanup

Old `.pkl` files are automatically deleted after `X` days (as defined in `config.yaml`).

---

## 🔮 Future Ideas

- Trend heatmap over time  
- Dashboard filters (by ticker, date, mention count)  
- Notion / Google Sheets sync  
- Discord bot with query support (`!trend TSLA`)

---

## 🧑‍💻 License

MIT – free for personal and commercial use.

---

> 📘 Based on the Heise guide:  
> “[Reddit-Crawler für Aktien in Python bauen – Schritt für Schritt](https://www.heise.de/ratgeber/Reddit-Crawler-fuer-Aktien-in-Python-bauen-Schritt-fuer-Schritt-9666547.html)”
