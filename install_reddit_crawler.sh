#!/bin/bash

echo "🔧 Reddit Stock Crawler Installer"
echo "----------------------------------"

# 📦 Install system dependencies
echo "📦 Installing required system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip wget git 

# 🔍 Check for Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 not found. Please install Python3."
  exit 1
fi

# 📁 Set install directory
INSTALL_DIR="$(pwd)"
echo "📁 Installing to: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR/data/pickle"
mkdir -p "$INSTALL_DIR/data/logs"
mkdir -p "$INSTALL_DIR/dashboard"
mkdir -p "$INSTALL_DIR/crawler-modules"

# 🔐 Create virtual environment
if [ ! -d "$INSTALL_DIR/venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv "$INSTALL_DIR/venv"
fi

# 🧠 Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# 🛠️ Install Python dependencies inside venv
echo "📦 Installing Python dependencies in virtual environment..."
pip install --upgrade pip
pip install pandas openpyxl praw python-dotenv streamlit plotly gspread google-auth google-auth-oauthlib seaborn openai PyYAML croniter

# 🔑 Ask for credentials
echo ""
echo "🔐 Please enter your API credentials:"
read -p "Reddit Client ID: " CLIENT_ID
read -p "Reddit Client Secret: " CLIENT_SECRET
read -p "Reddit User Agent (e.g., reddit-bot:v1.0 by /u/yourname): " USER_AGENT

read -p "AI Provider [openai/gemini] (default: openai): " AI_PROVIDER_INPUT
AI_PROVIDER=${AI_PROVIDER_INPUT:-openai}

read -p "OpenAI API Key (optional): " OPENAI_API_KEY
read -p "Gemini API Key (optional): " GEMINI_API_KEY

read -p "Discord Webhook URL (optional): " WEBHOOK_URL
read -p "Google Sheets JSON key file path (optional): " GDRIVE_KEY
read -p "Google Sheet spreadsheet name (optional): " GDRIVE_SHEET

read -p "Auto-cleanup days for pickle files (default 7): " CLEANUP_INPUT
CLEANUP_DAYS=${CLEANUP_INPUT:-7}

# 📄 Generate config.yaml
cat > "$INSTALL_DIR/config.yaml" <<EOF
# Reddit Stock Crawler Configuration
reddit_client_id: "${CLIENT_ID}"
reddit_client_secret: "${CLIENT_SECRET}"
reddit_user_agent: "${USER_AGENT}"
ai_provider: "${AI_PROVIDER}"
openai_api_key: "${OPENAI_API_KEY}"
${GEMINI_API_KEY:+gemini_api_key: "${GEMINI_API_KEY}"}
webhook_url: "${WEBHOOK_URL}"
google_sheets_keyfile: "${GDRIVE_KEY}"
google_sheets_spreadsheet: "${GDRIVE_SHEET}"
pickle_output_path: "data/pickle"
cleanup_days: ${CLEANUP_DAYS}
EOF

echo "✅ config.yaml created."

# 📥 Download ticker list
echo "🗕️ Downloading NASDAQ & NYSE symbol list..."
wget -O data/NAS-NYSE-cleaned.xlsx https://www.heise.de/downloads/18/4/8/7/4/3/8/6/NAS-NYSE-bereinigt.xlsx

# 📦 Generate ticker pickle
echo "🖐 Generating ticker symbol list..."
python3 crawler_modules/ticker_pickle_generator.py

# 🚀 Create run script
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash
cd "\$(dirname "\$0")"
source venv/bin/activate
export PYTHONPATH=\$(pwd)
python3 crawler_modules/Red-Crawler.py
python3 crawler_modules/cleanup_pickle_files.py
python3 crawler_modules/upload_to_gsheets.py
EOF
chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

# ⏰ Cronjob setup
echo ""
echo "⏰ How often should the crawler run automatically?"
echo "   1) Every 1 hour"
echo "   2) Every 6 hours"
echo "   3) Once per day (8:00 AM)"
echo "   4) Custom schedule (cron format)"
echo "   5) Skip (no cronjob)"
read -p "➡ Choose an option [1-5]: " INTERVAL

case $INTERVAL in
  1) CRON_EXPR="0 * * * *" ;;
  2) CRON_EXPR="0 */6 * * *" ;;
  3) CRON_EXPR="0 8 * * *" ;;
  4) read -p "🛠️ Enter your custom cron expression: " CUSTOM_EXPR
     CRON_EXPR="$CUSTOM_EXPR" ;;
  *) echo "⏩ Skipping cronjob setup."; CRON_EXPR="" ;;
esac

if [ -n "$CRON_EXPR" ]; then
  CRON_CMD="$CRON_EXPR $INSTALL_DIR/run_reddit_crawler.sh >> $INSTALL_DIR/data/logs/cron.log 2>&1"
  (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
  echo "" >> "$INSTALL_DIR/config.yaml"
  echo "# Cron schedule for automated runs" >> "$INSTALL_DIR/config.yaml"
  echo "cron_schedule: \"$CRON_EXPR\"" >> "$INSTALL_DIR/config.yaml"
  echo "✅ Cronjob added."
fi

# 🖥️ Create systemd service for dashboard
echo "🛠️ Creating systemd service for dashboard..."
SERVICE_NAME="reddit_dashboard"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Reddit Dashboard Service
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=${INSTALL_DIR}/venv/bin/streamlit run dashboard/dashboard.py
Restart=always
User=$(whoami)
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
echo "✅ Dashboard service started and enabled."

# 🧩 Create helper scripts
cat > "$INSTALL_DIR/status-dashboard.sh" <<EOF
#!/bin/bash
systemctl status $SERVICE_NAME
EOF
chmod +x "$INSTALL_DIR/status-dashboard.sh"

cat > "$INSTALL_DIR/stop-dashboard.sh" <<EOF
#!/bin/bash
systemctl stop $SERVICE_NAME
systemctl disable $SERVICE_NAME
echo "⛔ Dashboard service stopped and disabled."
EOF
chmod +x "$INSTALL_DIR/stop-dashboard.sh"

# ✅ Done
echo ""
echo "✅ Installation complete!"
echo "Run crawler manually with: ./run_reddit_crawler.sh"
echo "Start dashboard manually with: streamlit run dashboard/dashboard.py"
echo "Check dashboard status: ./status-dashboard.sh"
