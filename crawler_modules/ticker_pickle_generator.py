import pandas as pd
import pickle

# Paths
EXCEL_PATH = "data/NAS-NYSE-cleaned.xlsx"
OUTPUT_PKL = "data/symbols_list.pkl"

# Load Excel file
df = pd.read_excel(EXCEL_PATH)

# Extract the first column: stock ticker symbols
symbols = df.iloc[:, 0].dropna().unique().tolist()

# Save as Pickle file
with open(OUTPUT_PKL, "wb") as f:
    pickle.dump(symbols, f)

print(f"✅ {len(symbols)} ticker symbols saved to {OUTPUT_PKL}.")
