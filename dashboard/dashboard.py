# dashboard/dashboard.py

import streamlit as st
import pandas as pd
import os
import json
import pickle
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from crawler_modules.config import get_config
from crawler_modules.upload_to_gsheets import display_gsheets_status
import requests

st.set_page_config(page_title="📈 Reddit Stock Crawler", layout="wide")
st.title("📈 Reddit Stock Mentions Dashboard (r/wallstreetbets)")

cfg = get_config()

# Anzeige des nächsten geplanten Cron-Laufs
st.subheader("⏱️ Nächste Ausführung")
next_run_file = "data/next_run.txt"
if os.path.exists(next_run_file):
    with open(next_run_file) as f:
        try:
            next_run = datetime.fromisoformat(f.read().strip())
            st.info(f"**{next_run.strftime('%Y-%m-%d %H:%M:%S')}**")
        except Exception:
            st.warning("⚠️ Ungültiger Zeitstempel in next_run.txt")
else:
    st.warning("ℹ️ Noch kein nächster Ausführungstermin vorhanden.")

# Lade das aktuelle Excel-Dokument (wenn vorhanden)
excel_path = "data/crawler_results_current.xlsx"
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    st.subheader("📊 Aktuelle Ergebnisse")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("❌ Keine aktuellen Ergebnisse gefunden.")
    df = pd.DataFrame()

# Lade JSON-Daten aller bisherigen Pickles
pickles_dir = cfg.pickle_output_path
all_data = []
if os.path.exists(pickles_dir):
    for file in sorted(os.listdir(pickles_dir), reverse=True):
        if file.endswith(".pkl"):
            try:
                with open(os.path.join(pickles_dir, file), "rb") as f:
                    data = pickle.load(f)
                    all_data.append((file, data))
            except Exception as e:
                st.error(f"Fehler beim Laden von {file}: {e}")

# ---- Pickle-Daten in DataFrame umwandeln ----
def parse_pickles(data_list):
    rows = []
    all_symbols = set()
    for file, entry in data_list:
        results = entry.get("results", {})
        run_id = entry.get("run_id", file.replace("results_", "").replace(".pkl", ""))
        all_symbols.update(results.keys())
        row = {"run_id": run_id}
        row.update(results)
        rows.append(row)
    df = pd.DataFrame(rows)
    df = df.sort_values("run_id").reset_index(drop=True)
    return df, sorted(all_symbols)

# Verarbeitung & Anzeige
if all_data:
    st.subheader("📈 Analyse der letzten Crawls")

    df_hist, symbols = parse_pickles(all_data)

    # Seitenleiste für Filter
    with st.sidebar:
        st.header("🔍 Filter")
        selected_symbols = st.multiselect("Filter by symbol:", options=symbols, default=symbols[:5])
        try:
            max_mentions = int(df_hist.drop(columns=["run_id"]).max().max())
            if pd.isna(max_mentions) or max_mentions < 1:
                raise ValueError
        except Exception:
            max_mentions = 10
        min_mentions = st.slider("Minimum Mentions:", min_value=1, max_value=max_mentions, value=3)
        top_n = st.slider("Top N Symbols (Heatmap):", min_value=3, max_value=len(symbols), value=10)

    # Gefilterter Datensatz
    filtered_df = df_hist[['run_id'] + selected_symbols].copy()
    filtered_df = filtered_df.loc[:, (filtered_df != 0).any(axis=0)]
    filtered_df = filtered_df[filtered_df[selected_symbols].ge(min_mentions).any(axis=1)]

    st.line_chart(filtered_df.set_index("run_id"))

    st.subheader("📋 Gefilterte Tabelle")
    st.dataframe(filtered_df)

    # Heatmap
    st.subheader("🔥 Heatmap of Top Stock Mentions")
    total_mentions = df_hist.drop(columns=["run_id"]).sum().sort_values(ascending=False)
    top_symbols = total_mentions.head(top_n).index.tolist()
    heatmap_data = df_hist[['run_id'] + top_symbols].set_index("run_id")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data.T, annot=True, fmt="d", cbar=True, ax=ax)
    st.pyplot(fig)

    # Trends
    st.subheader("📈 Mention Trends (Last 3 Runs)")
    trend_df = df_hist[['run_id'] + top_symbols].copy()
    trend_result = []
    for symbol in top_symbols:
        values = trend_df[symbol].values[-3:]
        if len(values) < 3:
            trend = "🟡 Not enough data"
        elif values[-1] > values[-2] > values[-3]:
            trend = "🟢 Increasing"
        elif values[-1] < values[-2] < values[-3]:
            trend = "🔴 Decreasing"
        else:
            trend = "🟡 Stable"
        trend_result.append((symbol, values.tolist(), trend))

    trend_table = pd.DataFrame(trend_result, columns=["Symbol", "Last 3", "Trend"])
    st.dataframe(trend_table)

    # AI-Auswertung
    st.subheader("🤖 AI Recommendation")
    ai_provider = cfg.ai_provider.lower()
    prompt = "Given the following stock trends:\n" + "\n".join(
        [f"{row['Symbol']}: {row['Trend']} ({row['Last 3']})" for _, row in trend_table.iterrows()]
    ) + "\n\nWhich tickers show strong momentum and should be watched closely?"

    if ai_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=cfg.openai_api_key)
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        ai_text = resp.choices[0].message.content

    elif ai_provider == "gemini":
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-pro:generateContent"
            f"?key={cfg.gemini_api_key}"
        )
        body = {"prompt": prompt, "temperature": 0.3, "maxOutputTokens": 150}
        r = requests.post(url, json=body, timeout=10)
        r.raise_for_status()
        ai_text = r.json()["candidates"][0]["content"]

    else:
        ai_text = "⚠️ Unknown AI provider configured."

    st.text_area("AI Einschätzung", ai_text, height=200)

# Google Sheets Status
with st.expander("📤 Google Sheets Export Status", expanded=True):
    display_gsheets_status()

st.caption("🔁 Das Dashboard aktualisiert sich nach jedem Crawl automatisch.")
