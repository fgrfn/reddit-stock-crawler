# dashboard/dashboard.py
import os
import pickle
import json
from datetime import datetime
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from crawler_modules.config import get_config
from crawler_modules.upload_to_gsheets import display_gsheets_status
import requests

# Initial setup
st.set_page_config(page_title="Reddit Stock Mentions Dashboard", layout="wide")
st.title("📊 Reddit Stock Mentions Dashboard (r/wallstreetbets)")

# Load configuration
cfg = get_config()

# Load pickle data
def load_pickle_data():
    pickle_dir = cfg.pickle_output_path
    files = [f for f in os.listdir(pickle_dir) if f.endswith(".pkl")]
    if not files:
        return pd.DataFrame(), []

    data = []
    for file in files:
        with open(os.path.join(pickle_dir, file), "rb") as f:
            data.append(pickle.load(f))

    all_symbols = set()
    for entry in data:
        all_symbols.update(entry.get('results', {}).keys())

    rows = []
    for entry in data:
        row = {symbol: 0 for symbol in all_symbols}
        row.update(entry.get('results', {}))
        row['run_id'] = entry.get('run_id')
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values("run_id").reset_index(drop=True)
    return df, sorted(all_symbols)

# Load data
df, symbols = load_pickle_data()
if df.empty:
    st.warning("🚫 No crawler results found.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Options")
    selected_symbols = st.multiselect("Filter by symbol:", options=symbols, default=symbols[:5])
    min_mentions = st.slider("Minimum Mentions:", min_value=1, max_value=int(df.drop(columns=["run_id"]).max().max()), value=3)
    top_n = st.slider("Top N symbols in Heatmap:", min_value=3, max_value=len(symbols), value=10)

# Filter data
filtered_df = df[['run_id'] + selected_symbols]
filtered_df = filtered_df.loc[:, (filtered_df != 0).any(axis=0)]
filtered_df = filtered_df[filtered_df[selected_symbols].ge(min_mentions).any(axis=1)]

# Display chart & table
st.subheader("📈 Mentions Over Time")
st.line_chart(filtered_df.set_index("run_id"))

st.subheader("📋 Table View")
st.dataframe(filtered_df)

# Heatmap of top mentioned symbols
total_mentions = df.drop(columns=["run_id"]).sum().sort_values(ascending=False)
top_symbols = total_mentions.head(top_n).index.tolist()
heatmap_data = df[['run_id'] + top_symbols].set_index("run_id")

st.subheader("🔥 Heatmap of Top Stock Mentions")
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data.T, annot=True, fmt="d", cbar=True, ax=ax)
plt.xlabel("Run ID")
plt.ylabel("Symbol")
plt.title("Mentions per Symbol over Time")
st.pyplot(fig)

# Trend Analysis (local, not AI-based)
st.subheader("📈 Mention Trends (Last 3 Runs)")
trend_df = df[['run_id'] + top_symbols].copy()
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

# Show Google Sheets status
with st.expander("📤 Google Sheets Export Status", expanded=True):
    display_gsheets_status()

# AI Recommendation
st.subheader("🤖 AI Recommendation")
ai_provider = cfg.ai_provider.lower()

# Build prompt for AI
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
    ai_text = "⚠️ Unbekannter AI Provider konfiguriert."

st.text_area("AI Einschätzung", ai_text, height=200)
