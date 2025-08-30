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
    season_pot = total_pot * PCT_OVERALL
    per_trimester_pot = total_pot * PCT_TRIMESTER
    special_pot = total_pot * PCT_SPECIAL

    # calculate season prizes
    if num_players <= 40:
        first = 0.6
        second = 0.25
        third = 0.1
        fourth = 0.05
    elif (num_players > 40) & (num_players <= 50):
        first = 0.5
        second = 0.22
        third = 0.13
        fourth = 0.09
        fifth = 0.06

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: _kpi("Number of Players", f"{num_players}")
    with c2: _kpi("Total Prize Pot", f"${total_pot:,.0f}")
    with c3: _kpi("Season Prize", f"${season_pot:,.0f}")
    with c4: _kpi("Trimester Prize", f"${per_trimester_pot:,.0f} x 3")
    with c5: _kpi("Special Prize Pot", f"${special_pot:,.0f}")

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
        season_pot = total_pot * 0.75  # unchanged logic

        # --- helpers for formatting ---
        fmt_pct = lambda x: f"{x:.0%}" if x < 1 else f"{x:.0f}%"
        fmt_usd = lambda x: f"${x:,.0f}"

        # ---------- Season payouts ----------
        season_rows = [
            ("First Place",  first,  season_pot * first),
            ("Second Place", second, season_pot * second),
            ("Third Place",  third,  season_pot * third),
            ("Fourth Place", fourth, season_pot * fourth),
        ]
        season_df = pd.DataFrame(season_rows, columns=["Bucket", "Percent", "Amount ($)"])

        # totals row for the season table
        season_total_pct = sum([first, second, third, fourth])
        season_total_amt = season_df["Amount ($)"].sum()

        season_df.loc[len(season_df)] = ["Total", season_total_pct, season_total_amt]

        # format columns
        season_df["Percent"]   = season_df["Percent"].map(fmt_pct)
        season_df["Amount ($)"] = season_df["Amount ($)"].map(fmt_usd)

        st.markdown("#### Season Payouts")
        st.dataframe(
            season_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Percent":    st.column_config.TextColumn(width=90),
                "Amount ($)": st.column_config.TextColumn(width=110),
            },
        )

        # ---------- Trimester & Special ----------
        extras_rows = [
            ("Trimester 1 (Weeks 1–6)",  5,  per_trimester_pot),
            ("Trimester 2 (Weeks 7–12)", 5,  per_trimester_pot),
            ("Trimester 3 (Weeks 13–18)",5,  per_trimester_pot),
            ("Special/Booby Prize",      10, special_pot),
        ]
        extras_df = pd.DataFrame(extras_rows, columns=["Bucket", "Percent", "Amount ($)"])

        # totals row for extras table
        extras_total_pct = extras_df["Percent"].sum()
        extras_total_amt = extras_df["Amount ($)"].sum()
        extras_df.loc[len(extras_df)] = ["Total (Trimester & Special)", extras_total_pct, extras_total_amt]

        # format columns
        extras_df["Percent"]    = extras_df["Percent"].map(fmt_pct)
        extras_df["Amount ($)"] = extras_df["Amount ($)"].map(fmt_usd)

        st.markdown("#### Trimester & Special")
        st.dataframe(
            extras_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Percent":    st.column_config.TextColumn(width=180),  # wider label for long header
                "Amount ($)": st.column_config.TextColumn(width=120),
            },
        )
    #     breakdown = pd.DataFrame(
    #         {
    #             "Bucket": [
    #                 "First Place (Season)",
    #                 "Second Place (Season)",
    #                 "Third Place (Season)",
    #                 "Fourth Place (Season)",
    #                 "Trimester 1 (Weeks 1–6)",
    #                 "Trimester 2 (Weeks 7–12)",
    #                 "Trimester 3 (Weeks 13–18)",
    #                 "Special/Booby Prize",
    #             ],
    #             "Percent": [first, second, third, fourth, 5, 5, 5, 10],
    #             "Amount ($)": [
    #                            (total_pot * 0.75) * first, 
    #                            (total_pot * 0.75) * second,
    #                            (total_pot * 0.75) * third,
    #                            (total_pot * 0.75) * fourth,
    #                            per_trimester_pot, 
    #                            per_trimester_pot, 
    #                            per_trimester_pot, 
    #                            special_pot
    #                            ],
    #         }
    #     )
    #     breakdown["Amount ($)"] = breakdown["Amount ($)"].map(lambda x: f"${x:,.0f}")
    #     st.markdown("### Breakdown")
    #     st.dataframe(breakdown, use_container_width=True, hide_index=True)

    # st.caption("All values are placeholders. Replace constants with  data source when ready.")

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
