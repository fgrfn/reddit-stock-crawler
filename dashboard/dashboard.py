# dashboard.py
import streamlit as st
import pandas as pd
import os
import pickle

st.set_page_config(page_title="Reddit Stock Crawler Dashboard", layout="wide")
st.title("📊 Reddit Stock Mentions (r/wallstreetbets)")

# Load data
pickle_files = sorted([f for f in os.listdir("pickle") if f.endswith(".pkl")])
if not pickle_files:
    st.warning("No crawler results found.")
else:
    latest_file = os.path.join("pickle", pickle_files[-1])
    with open(latest_file, "rb") as f:
        data = pickle.load(f)

    st.markdown(f"**Run ID:** `{data['run_id']}` — Total Posts: `{data['total_posts']}`")
    df = pd.DataFrame(data["results"].items(), columns=["Ticker", "Mentions"])
    df = df.sort_values(by="Mentions", ascending=False)

    st.bar_chart(df.set_index("Ticker"))

    st.dataframe(df.reset_index(drop=True))

