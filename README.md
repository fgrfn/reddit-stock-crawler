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
```

The installer will:
- Prompt for an installation path and Reddit API credentials
- Create a virtual Python environment (`venv`)
- Install all required dependencies
- Set up the base scripts and launcher

---

## 🔐 Requirements

### ✅ Reddit API Access

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click **Create App**, choose **Script**
3. Use `http://localhost:8080` as redirect URI
4. Note down:
   - **Client ID**
   - **Client Secret**
   - **User Agent** (e.g. `python:reddit-crawler:v1.0 (by /u/yourusername)`)

---

## 📦 Dependencies

Installed automatically into a virtual environment:

- `praw` – Reddit API wrapper
- `pandas` – data processing
- `openpyxl` – Excel writing
- `python-dotenv` – for loading `.env` credentials

---

## 🧪 Usage

Run the full crawler + Excel update:

```bash
./run_reddit_crawler.sh
```

This will:
1. Search for ticker mentions in the last 100 posts/comments on r/wallstreetbets
2. Store results in `./pickle/<timestamp>_crawler-ergebnis.pkl`
3. Update your Excel report (`crawler_results_aktuell.xlsx`)

To enable Excel output, download the formatting template:

```bash
wget https://www.heise.de/downloads/18/4/8/7/4/3/8/6/crawler_results-vorlage.xlsx
```

Place the file in your project root.

---

## 📊 Output Files

- `symbols_list.pkl` → list of tickers to track
- `pickle/*.pkl` → daily result files with counts
- `crawler_results_aktuell.xlsx` → full overview in Excel, color-coded (green = trending)

---

## 🕒 Automation

You can run the crawler daily using a cronjob:

```bash
0 7 * * * /path/to/project/run_reddit_crawler.sh >> /path/to/project/logs/cron.log 2>&1
```

---

## 🎯 Why Use This?

This script is ideal for:

- Retail traders and investors who want **early signals** on trending stocks
- Content creators and analysts monitoring Reddit-driven market moves
- Anyone who wants to **track WSB hype without reading 1,000+ comments**

---

## 📌 Roadmap Ideas

- 🟡 Sentiment analysis (bullish / bearish comments)
- 🧹 Auto-cleanup for inactive tickers
- 🌐 Web dashboard or API backend
- 📉 Long-term trend visualization

---

## 📄 License

MIT License

---

## 🙌 Credits

- Based on this [Heise Online article](https://www.heise.de/ratgeber/Reddit-Crawler-fuer-Aktien-in-Python-bauen-So-geht-es-Schritt-fuer-Schritt-10442095.html)
- Extended and scripted for automation & ease-of-use
