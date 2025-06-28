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

# 🔑 Ask for Reddit & API credentials
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

read -p "Cron schedule for crawler (default '0 * * * *'): " CRON_INPUT
CRON_SCHEDULE=${CRON_INPUT:-"0 * * * *"}

# 📄 Create config.yaml file
cat > "$INSTALL_DIR/config.yaml" <<EOF
# Reddit Stock Crawler Configuration

# Reddit API credentials
reddit_client_id: "${CLIENT_ID}"
reddit_client_secret: "${CLIENT_SECRET}"
reddit_user_agent: "${USER_AGENT}"

# AI provider and keys
ai_provider: "${AI_PROVIDER}"
openai_api_key: "${OPENAI_API_KEY}"
${GEMINI_API_KEY:+gemini_api_key: "${GEMINI_API_KEY}"}

# Webhook and Google Sheets
webhook_url: "${WEBHOOK_URL}"
google_sheets_keyfile: "${GDRIVE_KEY}"
google_sheets_spreadsheet: "${GDRIVE_SHEET}"

# Crawler settings
pickle_output_path: "data/pickle"
cleanup_days: ${CLEANUP_DAYS}
cron_schedule: "${CRON_SCHEDULE}"
EOF

echo "✅ config.yaml created."

# 📥 Download stock symbol list
echo "🗕️ Downloading NASDAQ & NYSE symbol list..."
wget -O data/NAS-NYSE-cleaned.xlsx https://www.heise.de/downloads/18/4/8/7/4/3/8/6/NAS-NYSE-bereinigt.xlsx

# 🖐 Generate symbols_list.pkl from Excel
echo "🖐 Generating ticker symbol list..."
python3 crawler_modules/ticker_pickle_generator.py

# 🚀 Create launch script
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash

# Change to the directory where this script is located
cd "$(dirname "\$0")"

# Activate the virtual environment
source venv/bin/activate

# Ensure the main project directory is in Python's module search path
export PYTHONPATH=$(pwd)

# Execute the crawler modules
python3 crawler_modules/Red-Crawler.py
python3 crawler_modules/cleanup_pickle_files.py
python3 crawler_modules/upload_to_gsheets.py

# Launch dashboard UI
streamlit run dashboard/dashboard.py
EOF

chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

# ⏰ Setup cronjob for automatic crawler runs
if [ -n "$CRON_SCHEDULE" ]; then
  CRON_CMD="$CRON_SCHEDULE cd $INSTALL_DIR && ./run_reddit_crawler.sh >> $INSTALL_DIR/data/logs/cron.log 2>&1"
  (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
  echo "✅ Cronjob added: $CRON_SCHEDULE"
fi

# 📈 Ask to auto-start dashboard on boot
echo ""
read -p "❓ Do you want to automatically launch the dashboard on boot? (y/n): " DASH_START
if [[ "\$DASH_START" =~ ^[Yy]$ ]]; then
  DASH_CMD="@reboot cd $INSTALL_DIR && ./run_reddit_crawler.sh >> $INSTALL_DIR/data/logs/dashboard.log 2>&1"
  (crontab -l 2>/dev/null; echo "$DASH_CMD") | crontab -
  echo "✅ Dashboard autostart added."
fi

# ✅ Done
echo ""
echo "✅ Installation complete!"
echo "Run the crawler manually with: ./run_reddit_crawler.sh"
echo "Start the dashboard manually with: streamlit run dashboard/dashboard.py"
