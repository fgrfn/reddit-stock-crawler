#!/bin/bash

echo "🚀 Starte initiales Setup für Reddit Crawler"
sleep 1

# Prüfe auf Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden. Bitte zuerst installieren."
    exit 1
fi

# 1️⃣ Virtuelle Umgebung erstellen (falls nicht vorhanden)
if [ ! -d "venv" ]; then
    echo "📦 Erstelle virtuelle Umgebung..."
    python3 -m venv venv
fi

# 2️⃣ Aktivieren (nur Bash/Linux)
source ./venv/bin/activate

# 3️⃣ Pip aktualisieren
echo "⚙️  Aktualisiere pip..."
pip install --upgrade pip

# 4️⃣ Installiere Setup-Abhängigkeiten (für CLI & .env)
echo "📚 Installiere Setup-Abhängigkeiten..."
pip install colorama pyfiglet halo python-dotenv

# 5️⃣ requirements.txt prüfen
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt nicht gefunden. Bitte anlegen!"
    exit 1
fi

# 6️⃣ Starte interaktives Setup-Skript
echo ""
echo "🎛️  Starte install.py ..."
python install.py
