#!/bin/bash

echo "🔧 Reddit Crawler Installer – für r/wallstreetbets"
echo "--------------------------------------------------"

# 1. Projektverzeichnis abfragen
read -p "📁 Wohin soll der Reddit-Crawler installiert werden? (z. B. /home/reddit-bot): " INSTALL_DIR
mkdir -p "$INSTALL_DIR"/{pickle,logs}
cd "$INSTALL_DIR" || exit 1

# 2. Python & pip prüfen
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 nicht gefunden. Bitte installiere Python."
  exit 1
fi

# 3. Virtuelle Umgebung erstellen
if [ ! -d "$INSTALL_DIR/venv" ]; then
  echo "📦 Erstelle virtuelle Umgebung..."
  python3 -m venv "$INSTALL_DIR/venv"
fi

# 4. Aktivieren der venv
source "$INSTALL_DIR/venv/bin/activate"

# 5. Pakete installieren
echo "📦 Installiere Python-Abhängigkeiten..."
pip install --upgrade pip
pip install pandas openpyxl praw python-dotenv

# 6. Reddit-API-Zugangsdaten abfragen
echo ""
echo "🔐 Bitte gib deine Reddit API-Zugangsdaten ein:"
read -p "Client ID: " CLIENT_ID
read -p "Client Secret: " CLIENT_SECRET
read -p "User Agent (z. B. python:mein-bot:v1.0 (by /u/deinname)): " USER_AGENT

# 7. .env Datei schreiben
cat > "$INSTALL_DIR/secret.env" <<EOF
REDDIT_CLIENT_ID=$CLIENT_ID
REDDIT_CLIENT_SECRET=$CLIENT_SECRET
REDDIT_USER_AGENT=$USER_AGENT
EOF

echo "✅ .env-Datei wurde erstellt."

# 8. Platzhalter-Skripte erstellen (nur zur Orientierung)
cat > "$INSTALL_DIR/Red-Crawler.py" <<EOF
# TODO: Red-Crawler.py mit echtem Crawler-Skript befüllen
print("Platzhalter: Red-Crawler.py")
EOF

cat > "$INSTALL_DIR/Red-Crawl-Table.py" <<EOF
# TODO: Red-Crawl-Table.py mit Excel-Auswertungsskript befüllen
print("Platzhalter: Red-Crawl-Table.py")
EOF

# 9. Startskript erstellen mit venv-Aktivierung
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash
source "\$(dirname "\$0")/venv/bin/activate"
python3 Red-Crawler.py
python3 Red-Crawl-Table.py
EOF

chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

# 10. Abschluss
echo ""
echo "✅ Setup abgeschlossen!"
echo "👉 Wechsle in dein Projektverzeichnis:"
echo "   cd $INSTALL_DIR"
echo ""
echo "➡ Starte den Crawler mit:"
echo "   ./run_reddit_crawler.sh"
echo ""
echo "📌 Denke daran, die echten Skripte (Red-Crawler.py etc.) einzufügen."
