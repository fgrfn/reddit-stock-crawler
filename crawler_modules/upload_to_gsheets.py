import os
import pickle
import pandas as pd
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from crawler_modules.config import get_config
import streamlit as st


def upload_latest_results_to_gsheets():
    config = get_config()
    keyfile = config.get("google_sheets_keyfile")
    spreadsheet_name = config.get("google_sheets_spreadsheet")
    pickle_dir = "data/pickle"
    log_path = "data/logs/gsheets_last.json"

    if not keyfile or not spreadsheet_name:
        print("⚠️ Google Sheets integration not configured.")
        return

    if not os.path.isfile(keyfile):
        print(f"❌ Keyfile not found: {keyfile}")
        return

    files = [f for f in os.listdir(pickle_dir) if f.endswith(".pkl")]
    if not files:
        print("🚫 No pickle files found.")
        return

    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(pickle_dir, f)))
    with open(os.path.join(pickle_dir, latest), "rb") as f:
        data = pickle.load(f)

    df = pd.DataFrame(data["results"].items(), columns=["Symbol", "Mentions"])
    df.insert(0, "Run ID", data["run_id"])

    creds = Credentials.from_service_account_file(keyfile, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open(spreadsheet_name).sheet1

    sheet.clear()
    sheet.append_row(df.columns.tolist())
    for row in df.values.tolist():
        sheet.append_row(row)

    print(f"✅ Uploaded {len(df)} rows to Google Sheets: {spreadsheet_name}")

    # Write export info to log
    export_log = {
        "status": "success",
        "spreadsheet": spreadsheet_name,
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "run_id": data["run_id"],
        "rows": len(df),
        "top": df.head(5).to_dict(orient="records")
    }
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as log_file:
        json.dump(export_log, log_file, indent=2)


if __name__ == "__main__":
    upload_latest_results_to_gsheets()

def display_gsheets_status():
    """
    Zeigt im Streamlit-Dashboard an,
    ob die Google-Sheets-Integration konfiguriert ist.
    """
    cfg = get_config()
    enabled = cfg.get('google_sheets_enabled', False) \
              or bool(cfg.get('google_sheets_credentials'))
    
    if enabled:
        st.success("✅ Google Sheets integration enabled")
    else:
        st.warning("⚠️ Google Sheets integration not configured")
