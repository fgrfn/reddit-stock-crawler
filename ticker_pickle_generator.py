import pandas as pd
import pickle

# Pfade
EXCEL_PATH = "NAS-NYSE-bereinigt.xlsx"
OUTPUT_PKL = "symbols_list.pkl"

# Excel laden
df = pd.read_excel(EXCEL_PATH)

# Erste Spalte: Aktiensymbole extrahieren
symbols = df.iloc[:, 0].dropna().unique().tolist()

# Pickle-Datei speichern
with open(OUTPUT_PKL, "wb") as f:
    pickle.dump(symbols, f)

print(f"✅ {len(symbols)} Tickersymbole in {OUTPUT_PKL} gespeichert.")
