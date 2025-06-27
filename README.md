# Reddit Stock Crawler (r/wallstreetbets)

This project automatically analyzes the most mentioned stock tickers in the `r/wallstreetbets` subreddit.

It helps identify trending or hyped stocks quickly by crawling Reddit, counting ticker mentions, and exporting the results into an Excel file.

---

## 🚀 Features

- Crawls latest posts and comments from `r/wallstreetbets`
- Counts ticker symbol mentions based on a filtered NASDAQ/NYSE list
- Excludes common words via blacklist
- Saves results as `.pkl` and `.xlsx`
- Optional: Streamlit dashboard for interactive viewing

---

## 📁 Project Structure

```
reddit-stock-crawler/
├── crawler/                  # Core logic scripts
│   ├── Red-Crawler.py        # Reddit scraping logic
│   ├── Red-Crawl-Table.py    # XLSX export logic
│   └── ticker_pickle_generator.py  # Generates symbols_list.pkl
│
├── data/                     # Input/output files
│   ├── NAS-NYSE-cleaned.xlsx      # Ticker source file
│   ├── crawler_results_template.xlsx  # XLSX template
│   ├── symbols_list.pkl           # Pickled ticker list
│   ├── pickle/                    # Crawler results (Pickle)
│   └── logs/                      # Optional logs
│
├── dashboard/                # Optional Streamlit dashboard
│   └── dashboard.py
│
├── venv/                     # Python virtual environment
├── install.sh                # Installer script
├── run_reddit_crawler.sh     # Main runner
├── secret.env                # Reddit API credentials
└── README.md
```

---

## 🛠️ Installation

```bash
git clone https://github.com/fgrfn/reddit-stock-crawler.git
cd reddit-stock-crawler
chmod +x install.sh
./install.sh
```

The installer will:
- Install required dependencies
- Ask for Reddit API credentials
- Download the stock list Excel file
- Generate the ticker list
- Setup a virtual environment

---

## 🧪 Run the crawler

```bash
./run_reddit_crawler.sh
```

Output will be saved to:

- `data/pickle/*.pkl` (raw results)
- `data/crawler_results_current.xlsx` (latest summary)

---

## 📊 Optional: Streamlit Dashboard

To launch the dashboard:

```bash
pip install streamlit
streamlit run dashboard/dashboard.py
```

---

## 🔐 Reddit API Setup

Create a Reddit app at: https://www.reddit.com/prefs/apps  
Use the credentials in the `install.sh` prompt or set them manually in `secret.env`.

---

## 📄 License

MIT License
