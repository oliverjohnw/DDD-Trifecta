import streamlit as st
import pandas as pd

# TEMPORARY DATA FOR DEVELOPMENT - TO BE DELETED LATER
STANDINGS_DATA = [
    {"Player": "Mr_Tuxedo", "Score": 24},
    {"Player": "Edub1321", "Score": 19},
    {"Player": "OtherDDDMember", "Score": 17},
    {"Player": "JordanLoveMVP", "Score": 17}
]

def standings_page():
    """
    Standings page.
    
    Standings table will include:
     - Player
     - Season long score 
    """
    st.title("Standings")

    # Search input
    search_term = st.text_input("Search Player", placeholder="Type a name...").strip().lower()

    # Convert constants to DataFrame
    df = pd.DataFrame(STANDINGS_DATA)

    # Sort by score descending
    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

    # Add standings (1-based rank)
    df.insert(0, "Standing", range(1, len(df) + 1))

    # Filter if search term entered
    if search_term:
        df = df[df["Player"].str.lower().str.contains(search_term)]

    # Display standings table
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Optional: show message if no results
    if df.empty:
        st.warning("No players match your search.")