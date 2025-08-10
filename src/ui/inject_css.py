import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
          .metric-card{
            border:1px solid rgba(255,255,255,0.08);
            border-radius:10px;padding:14px 16px;
            background:rgba(255,255,255,0.03);
          }
          .cap{ text-transform:uppercase; letter-spacing:.08em; font-size:.75rem; opacity:.8; }
          .tight { margin-top:-8px; }
          footer {visibility:hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

def section(title: str):
    st.markdown(f"### {title}")