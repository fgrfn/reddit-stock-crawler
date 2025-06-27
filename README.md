# 📈 Reddit Stock Crawler (r/wallstreetbets)

This tool helps you **easily and quickly identify which stocks are currently trending** on the r/wallstreetbets subreddit.

It scans Reddit posts and comments for ticker mentions (e.g. `NVDA`, `$TSLA`) from the past 24 hours, aggregates the results, and presents them in a **color-coded Excel dashboard** – making it simple to spot hyped or rising stocks before the news hits.

---

## 🚀 Features

- 🧠 Scans latest Reddit posts + comments (past 24h)
- 🔍 Detects mentions of US stock tickers (e.g. `GOOG`, `$AAPL`)
- ⚠️ Ignores false positives via configurable blacklist
- 📁 Stores results as Pickle files with timestamps
- 📊 Generates a **color-coded Excel sheet** showing ticker trends over time
- ⚙️ Fully automatable via cronjobs or scheduled scripts

---

## 🛠️ Installation

```bash
git clone https://github.com/youruser/reddit-stock-crawler.git
cd reddit-stock-crawler
chmod +x install_reddit_crawler.sh
./install_reddit_crawler.sh
