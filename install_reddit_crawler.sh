#!/bin/bash

echo "🔧 Reddit Stock Crawler Installer"
echo "----------------------------------"

# 📦 Install required system dependencies
echo "📦 Installing required system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip wget git

# 🔍 Check for Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 not found. Please install Python3."
  exit 1
fi

# 📁 Use current directory as install target
INSTALL_DIR="$(pwd)"
echo "📁 Installing to: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"/data/pickle
mkdir -p "$INSTALL_DIR"/data/logs

# 🔐 Create virtual environment
if [ ! -d "$INSTALL_DIR/venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv "$INSTALL_DIR/venv"
fi

# 🧠 Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# 🧰 Install Python dependencies inside venv
echo "📦 Installing Python dependencies in virtual environment..."
pip install --upgrade pip
pip install pandas openpyxl praw python-dotenv streamlit plotly

# 🔑 Ask for Reddit API credentials
echo ""
echo "🔐 Please enter your Reddit API credentials:"
read -p "Client ID: " CLIENT_ID
read -p "Client Secret: " CLIENT_SECRET
read -p "User Agent (e.g., python:reddit-bot:v1.0 (by /u/yourname)): " USER_AGENT

# 📄 Create .env file
cat > "$INSTALL_DIR/secret.env" <<EOF
REDDIT_CLIENT_ID=$CLIENT_ID
REDDIT_CLIENT_SECRET=$CLIENT_SECRET
REDDIT_USER_AGENT=$USER_AGENT
EOF

# ➕ Optional: Add integration configuration
echo "" >> "$INSTALL_DIR/secret.env"
echo "# Optional integrations:" >> "$INSTALL_DIR/secret.env"
echo "WEBHOOK_URL=" >> "$INSTALL_DIR/secret.env"
echo "GOOGLE_SHEETS_KEYFILE=" >> "$INSTALL_DIR/secret.env"
echo "GOOGLE_SHEETS_SPREADSHEET=" >> "$INSTALL_DIR/secret.env"
echo "CLEANUP_DAYS=7" >> "$INSTALL_DIR/secret.env"

echo "✅ .env file created."

# 📥 Download stock symbol list
echo "📥 Downloading NASDAQ & NYSE symbol list..."
wget -O data/NAS-NYSE-cleaned.xlsx https://www.heise.de/downloads/18/4/8/7/4/3/8/6/NAS-NYSE-bereinigt.xlsx

# 🧪 Generate symbols_list.pkl from Excel
echo "🔧 Generating ticker symbol list..."
python3 crawler/ticker_pickle_generator.py

# 🚀 Create launch script
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash
source "\$(dirname "\$0")/venv/bin/activate"
python3 crawler/Red-Crawler.py
python3 crawler/Red-Crawl-Table.py
python3 crawler/cleanup_pickle_files.py
EOF

chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

# ⏰ Ask how often the crawler should run
echo ""
echo "⏰ How often should the crawler run automatically?"
echo "   1) Every 1 hour"
echo "   2) Every 6 hours"
echo "   3) Once per day (8:00 AM)"
echo "   4) Custom schedule (cron format)"
echo "   5) Skip (no cronjob)"
read -p "➡ Choose an option [1-5]: " INTERVAL

case $INTERVAL in
  1)
    CRON_EXPR="0 * * * *"
    ;;
  2)
    CRON_EXPR="0 */6 * * *"
    ;;
  3)
    CRON_EXPR="0 8 * * *"
    ;;
  4)
    read -p "🛠️  Enter your custom cron expression (e.g., */30 * * * *): " CUSTOM_EXPR
    CRON_EXPR="$CUSTOM_EXPR"
    ;;
  *)
    echo "⏩ Skipping cronjob setup."
    CRON_EXPR=""
    ;;
esac

if [ -n "$CRON_EXPR" ]; then
  CRON_CMD="$CRON_EXPR $INSTALL_DIR/run_reddit_crawler.sh >> $INSTALL_DIR/data/logs/cron.log 2>&1"
  (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
  echo "✅ Cronjob added: Crawler will run as scheduled."
fi

# 📊 Ask to auto-start dashboard on boot
echo ""
read -p "❓ Do you want to automatically launch the dashboard on boot? (y/n): " DASHBOARD_START
if [[ "$DASHBOARD_START" =~ ^[Yy]$ ]]; then
  DASHBOARD_CMD="@reboot $INSTALL_DIR/venv/bin/streamlit run $INSTALL_DIR/dashboard/dashboard.py >> $INSTALL_DIR/data/logs/dashboard.log 2>&1"
  (crontab -l 2>/dev/null; echo "$DASHBOARD_CMD") | crontab -
  echo "✅ Dashboard autostart added (via cron @reboot)."
fi

# ✅ Done
echo ""
echo "✅ Installation complete!"
echo "➡ To run the crawler manually:"
echo "   ./run_reddit_crawler.sh"
echo ""
echo "📊 To launch the dashboard manually:"
echo "   streamlit run dashboard/dashboard.py"
