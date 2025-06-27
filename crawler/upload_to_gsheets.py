import os
import pickle
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from crawler.config import get_config


def upload_latest_results_to_gsheets():
    config = get_config()
    keyfile = config.get("google_sheets_keyfile")
    spreadsheet_name = config.get("google_sheets_spreadsheet")
    pickle_dir = "data/pickle"

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


if __name__ == "__main__":
    upload_latest_results_to_gsheets()
