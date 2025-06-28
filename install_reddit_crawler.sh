\#!/bin/bash

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

INSTALL\_DIR="\$(pwd)"
echo "📁 Installing to: \$INSTALL\_DIR"

mkdir -p "\$INSTALL\_DIR/data/pickle"
mkdir -p "\$INSTALL\_DIR/data/logs"
mkdir -p "\$INSTALL\_DIR/dashboard"
mkdir -p "\$INSTALL\_DIR/crawler-modules"

# 🔐 Create virtual environment

if \[ ! -d "\$INSTALL\_DIR/venv" ]; then
echo "📦 Creating virtual environment..."
python3 -m venv "\$INSTALL\_DIR/venv"
fi

# 🧠 Activate virtual environment

source "\$INSTALL\_DIR/venv/bin/activate"

# 🛠️ Install Python dependencies inside venv

echo "📦 Installing Python dependencies in virtual environment..."
pip install --upgrade pip
pip install pandas openpyxl praw python-dotenv streamlit plotly gspread google-auth google-auth-oauthlib seaborn openai PyYAML croniter

# 🔑 Ask for Reddit & API credentials

echo ""
echo "🔐 Please enter your API credentials:"

read -p "Reddit Client ID: " CLIENT\_ID
read -p "Reddit Client Secret: " CLIENT\_SECRET
read -p "Reddit User Agent (e.g., reddit-bot\:v1.0 by /u/yourname): " USER\_AGENT

read -p "OpenAI API Key (optional): " OPENAI\_API\_KEY
read -p "Gemini API Key (optional): " GEMINI\_API\_KEY

read -p "Discord Webhook URL (optional): " WEBHOOK\_URL
read -p "Google Sheets JSON key file path (optional): " GDRIVE\_KEY
read -p "Google Sheet spreadsheet name (optional): " GDRIVE\_SHEET
read -p "Auto-cleanup days for pickle files (default 7): " CLEANUP\_DAYS
CLEANUP\_DAYS=\${CLEANUP\_DAYS:-7}
read -p "Cron schedule for crawler (e.g., '0 \* \* \* \*'): " CRON\_SCHEDULE

# 📄 Create config.yaml file

cat > "\$INSTALL\_DIR/config.yaml" <\<EOF

# Reddit Stock Crawler Configuration

# Reddit API credentials

reddit\_client\_id: "\${CLIENT\_ID}"
reddit\_client\_secret: "\${CLIENT\_SECRET}"
reddit\_user\_agent: "\${USER\_AGENT}"

# AI provider and keys

ai\_provider: "\${OPENAI\_API\_KEY:+openai}\${OPENAI\_API\_KEY:+}"\${OPENAI\_API\_KEY:+}""
openai\_api\_key: "\${OPENAI\_API\_KEY}"
\${GEMINI\_API\_KEY:+gemini\_api\_key: "\${GEMINI\_API\_KEY}"}

# Webhook and Google Sheets

webhook\_url: "\${WEBHOOK\_URL}"
google\_sheets\_keyfile: "\${GDRIVE\_KEY}"
google\_sheets\_spreadsheet: "\${GDRIVE\_SHEET}"

# Crawler settings

pickle\_output\_path: "data/pickle"
cleanup\_days: \${CLEANUP\_DAYS}
cron\_schedule: "\${CRON\_SCHEDULE:-0 \* \* \* \*}"
EOF

echo "✅ config.yaml created."

# 📥 Download stock symbol list

echo "🗕️ Downloading NASDAQ & NYSE symbol list..."
wget -O data/NAS-NYSE-cleaned.xlsx [https://www.heise.de/downloads/18/4/8/7/4/3/8/6/NAS-NYSE-bereinigt.xlsx](https://www.heise.de/downloads/18/4/8/7/4/3/8/6/NAS-NYSE-bereinigt.xlsx)

# 🖐 Generate symbols\_list.pkl from Excel

echo "🖐 Generating ticker symbol list..."
python3 crawler\_modules/ticker\_pickle\_generator.py

# 🚀 Create launch script

cat > "\$INSTALL\_DIR/run\_reddit\_crawler.sh" <\<EOF
\#!/bin/bash

# Change to the directory where this script is located

cd "\$(dirname "\$0")"

# Activate the virtual environment

source venv/bin/activate

# Ensure the main project directory is in Python's module search path

export PYTHONPATH=\$(pwd)

# Execute the crawler modules

python3 crawler\_modules/Red-Crawler.py
python3 crawler\_modules/cleanup\_pickle\_files.py
python3 crawler\_modules/upload\_to\_gsheets.py

# Launch dashboard UI

streamlit run dashboard/dashboard.py
EOF

chmod +x "\$INSTALL\_DIR/run\_reddit\_crawler.sh"

# ⏰ Setup cronjob for automatic crawler runs

if \[ -n "\$CRON\_SCHEDULE" ]; then
CRON\_CMD="\$CRON\_SCHEDULE cd \$INSTALL\_DIR && ./run\_reddit\_crawler.sh >> \$INSTALL\_DIR/data/logs/cron.log 2>&1"
(crontab -l 2>/dev/null; echo "\$CRON\_CMD") | crontab -
echo "✅ Cronjob added: \$CRON\_SCHEDULE"
fi

# 📈 Ask to auto-start dashboard on boot

echo ""
read -p "❓ Do you want to automatically launch the dashboard on boot? (y/n): " DASH\_START
if \[\[ "\$DASH\_START" =\~ ^\[Yy]\$ ]]; then
DASH\_CMD="@reboot cd \$INSTALL\_DIR && ./run\_reddit\_crawler.sh >> \$INSTALL\_DIR/data/logs/dashboard.log 2>&1"
(crontab -l 2>/dev/null; echo "\$DASH\_CMD") | crontab -
echo "✅ Dashboard autostart added."
fi

# ✅ Done

echo ""
echo "✅ Installation complete!"
echo "Run the crawler manually with: ./run\_reddit\_crawler.sh"
echo "Start the dashboard manually with: streamlit run dashboard/dashboard.py"
