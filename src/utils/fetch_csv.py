import streamlit as st
import pandas as pd

# --- Cached fetcher with TTL ---
@st.cache_data(ttl=3600)  # refreshes automatically every 1 hour
def fetch_csv(sheet_id: str, gid: str | int) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return pd.read_csv(url)