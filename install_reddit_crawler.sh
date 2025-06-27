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

# 📁 Ask for installation directory
read -p "📁 Where should the Reddit Crawler be installed? (e.g., /home/reddit-bot): " INSTALL_DIR
mkdir -p "$INSTALL_DIR"/{pickle,logs}
cd "$INSTALL_DIR" || exit 1

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
pip install pandas openpyxl praw python-dotenv

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

echo "✅ .env file created."

# 🚀 Create launch script
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash
source "\$(dirname "\$0")/venv/bin/activate"
python3 Red-Crawler.py
python3 Red-Crawl-Table.py
EOF

chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

# ✅ Done
echo ""
echo "✅ Installation complete!"
echo "➡ To run the crawler:"
echo "   cd $INSTALL_DIR"
echo "   ./run_reddit_crawler.sh"
