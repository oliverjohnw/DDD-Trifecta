import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# GLOBAL VARIABLES - DETERMINED VIA RULES
BUY_IN = 100
PCT_OVERALL = 0.75
PCT_TRIMESTER = 0.05
PCT_SPECIAL = 0.10 

def prizes_page(app_config: dict):
    _inject_css()
    st.title("Prizes")

    # load player pool
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"player_pool"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    player_pool = pd.read_csv(url)
    players = player_pool["Players"]

    # calculate numbers
    num_players = len(players)
    total_pot = num_players * 100
    per_trimester_pot = total_pot * 0.05
    special_pot = total_pot * 0.10

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1: _kpi("Number of Players", f"{num_players}")
    with c2: _kpi("Total Prize Pot", f"${total_pot:,.0f}")
    with c3: _kpi("Trimester Prize (each)", f"${per_trimester_pot:,.0f}")
    with c4: _kpi("Special Prize Pot", f"${special_pot:,.0f}")

    st.divider()

    # Donut + Breakdown
    left, right = st.columns([1, 1])
    with left:
        labels = [
            f"Season Overall ({int(PCT_OVERALL*100)}%)",
            f"Trimester 1 ({int(PCT_TRIMESTER*100)}%)",
            f"Trimester 2 ({int(PCT_TRIMESTER*100)}%)",
            f"Trimester 3 ({int(PCT_TRIMESTER*100)}%)",
            f"Special ({int(PCT_SPECIAL*100)}%)",
        ]
        values = [
            total_pot * PCT_OVERALL,
            per_trimester_pot,
            per_trimester_pot,
            per_trimester_pot,
            special_pot,
        ]
        _donut_chart(labels, values, title="Prize Distribution")

    with right:
        breakdown = pd.DataFrame(
            {
                "Bucket": [
                    "Season Overall (Top 3)",
                    "Trimester 1 (Weeks 1–6)",
                    "Trimester 2 (Weeks 7–12)",
                    "Trimester 3 (Weeks 13–18)",
                    "Temporary (TBA)",
                ],
                "Percent": [75, 5, 5, 5, 10],
                "Amount ($)": [total_pot * 0.75, per_trimester_pot, per_trimester_pot, per_trimester_pot, special_pot],
            }
        )
        breakdown["Amount ($)"] = breakdown["Amount ($)"].map(lambda x: f"${x:,.0f}")
        st.markdown("### Breakdown")
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

    st.caption("All values are placeholders. Replace constants with  data source when ready.")

def _inject_css():
    st.markdown(
        """
        <style>
          .metric-card{
            border:1px solid rgba(255,255,255,0.08);
            border-radius:12px;
            padding:14px 16px;
            background:rgba(255,255,255,0.03);
          }
          .cap {text-transform:uppercase; letter-spacing:.08em; font-size:.75rem; opacity:.8;}
          .kpi {font-size:1.6rem; font-weight:700; margin:4px 0 0 0;}
        </style>
        """,
        unsafe_allow_html=True
    )

def _kpi(label, value):
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="cap">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi">{value}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def _donut_chart(labels, values, title="Prize Distribution"):
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    wedges, _ = ax.pie(values, wedgeprops=dict(width=0.42), startangle=90)
    # draw center circle for donut effect
    centre_circle = plt.Circle((0,0), 0.58, fc='white' if st.get_option("theme.base") == "light" else '#0E1117')
    fig.gca().add_artist(centre_circle)
    ax.set(aspect="equal", title=title)
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(fig, use_container_width=False)
