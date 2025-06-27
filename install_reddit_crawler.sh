#!/bin/bash

echo "🔧 Reddit Crawler Installer – für r/wallstreetbets"
echo "---------------------------------------------"

# 1. Projektpfad abfragen
read -p "📁 Wohin soll der Crawler installiert werden? (Pfad angeben): " INSTALL_DIR
mkdir -p "$INSTALL_DIR"/{pickle,logs}
cd "$INSTALL_DIR" || exit 1

# 2. Python prüfen
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 nicht gefunden. Bitte installiere Python3."
  exit 1
fi

# 3. pip prüfen
if ! command -v pip3 &> /dev/null; then
  echo "❌ pip nicht gefunden. Installiere pip mit 'sudo apt install python3-pip'."
  exit 1
fi

# 4. Abhängigkeiten installieren
echo "📦 Installiere Python-Pakete..."
pip3 install --upgrade praw pandas openpyxl python-dotenv

# 5. Reddit-Zugangsdaten abfragen
echo "🔐 Bitte gib deine Reddit API-Zugangsdaten ein:"
read -p "Client ID: " CLIENT_ID
read -p "Client Secret: " CLIENT_SECRET
read -p "User Agent (z. B. python:mein-bot:v1.0 (by /u/deinname)): " USER_AGENT

# 6. .env Datei erstellen
cat > "$INSTALL_DIR/secret.env" <<EOF
REDDIT_CLIENT_ID=$CLIENT_ID
REDDIT_CLIENT_SECRET=$CLIENT_SECRET
REDDIT_USER_AGENT=$USER_AGENT
EOF

echo "✅ .env-Datei erstellt."

# 7. Beispielskripte speichern (Platzhalter – nur Setup)
cat > "$INSTALL_DIR/Red-Crawler.py" <<EOF
# TODO: Hier kommt das Crawler-Skript rein
print("Red-Crawler.py ist nur ein Platzhalter.")
EOF

cat > "$INSTALL_DIR/Red-Crawl-Table.py" <<EOF
# TODO: Hier kommt das Excel-Auswertungsskript rein
print("Red-Crawl-Table.py ist nur ein Platzhalter.")
EOF

# 8. Startskript erstellen
cat > "$INSTALL_DIR/run_reddit_crawler.sh" <<EOF
#!/bin/bash
echo "📡 Reddit-Crawler wird gestartet..."
python3 "$INSTALL_DIR/Red-Crawler.py"
python3 "$INSTALL_DIR/Red-Crawl-Table.py"
EOF

chmod +x "$INSTALL_DIR/run_reddit_crawler.sh"

echo "✅ Startskript 'run_reddit_crawler.sh' erstellt."

# 9. Abschluss
echo ""
echo "🚀 Einrichtung abgeschlossen!"
echo "👉 Lege jetzt deine eigentlichen Python-Skripte in:"
echo "   $INSTALL_DIR"
echo ""
echo "➡ Starte den Bot später einfach mit:"
echo "   $INSTALL_DIR/run_reddit_crawler.sh"
