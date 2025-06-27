import os
import pickle
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from crawler.upload_to_gsheets import display_gsheets_status

st.set_page_config(page_title="Reddit Stock Crawler Dashboard", layout="wide")
st.title("📊 Reddit Stock Mentions Dashboard (r/wallstreetbets)")

# Load pickle data
def load_pickle_data():
    pickle_dir = "data/pickle"
    files = [f for f in os.listdir(pickle_dir) if f.endswith(".pkl")]
    if not files:
        return pd.DataFrame(), []

    data = []
    for file in files:
        with open(os.path.join(pickle_dir, file), "rb") as f:
            data.append(pickle.load(f))

    all_symbols = set()
    for entry in data:
        all_symbols.update(entry['results'].keys())

    rows = []
    for entry in data:
        row = {symbol: 0 for symbol in all_symbols}
        row.update(entry['results'])
        row['run_id'] = entry['run_id']
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
    min_mentions = st.slider("Minimum Mentions:", min_value=1, max_value=50, value=3)
    top_n = st.slider("Top N symbols in Heatmap:", min_value=3, max_value=25, value=10)

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
sns.heatmap(heatmap_data.T, cmap="YlGnBu", annot=True, fmt="d", cbar=True, ax=ax)
plt.xlabel("Run ID")
plt.ylabel("Symbol")
plt.title("Mentions per Symbol over Time")
st.pyplot(fig)

# Show Google Sheets status
with st.expander("📤 Google Sheets Export Status", expanded=True):
    display_gsheets_status()
