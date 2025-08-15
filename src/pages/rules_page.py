# src/pages/rules.py
import streamlit as st

# ----------------------------
# Tiny CSS polish (local only)
# ----------------------------
def _inject_css():
    st.markdown(
        """
        <style>
          .card {
            border:1px solid rgba(255,255,255,0.08);
            border-radius:12px;
            padding:16px;
            background:rgba(255,255,255,0.03);
          }
          .cap {text-transform:uppercase; letter-spacing:.08em; font-size:.75rem; opacity:.8;}
          .big {font-size:1.05rem;}
          .badge {
            display:inline-block; padding:4px 8px; border-radius:999px;
            border:1px solid rgba(255,255,255,0.15); font-size:.8rem; opacity:.95;
            margin-right:6px; margin-bottom:6px;
          }
          .good {background:rgba(76,175,80,.15);}
          .warn {background:rgba(255,193,7,.15);}
          .note {background:rgba(33,150,243,.15);}
          .hr {height:1px; background:rgba(255,255,255,0.1); margin:10px 0 16px 0;}
          .list-tight li{ margin-bottom:6px; }
          footer {visibility:hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------
# Page
# ----------------------------
def rules_page():
    _inject_css()
    st.title("Rules")

    # Quick badges
    st.markdown(
        """
        <span class="badge note">Season: Weeks 1–18</span>
        <span class="badge good">Buy‑in: $100</span>
        <span class="badge warn">Submission cutoff: 1 hour before kickoff</span>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Weekly Submissions
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("#### Weekly Submissions")
        st.markdown(
            """
            <div class="card big">
              <ul class="list-tight">
                <li>🏁 <b>1 Survivor pick</b> per week — <i>cannot reuse a team all season</i>.</li>
                <li>📈 <b>5 Spread picks</b> per week:
                  <ul>
                    <li>4 picks worth <b>1 point</b> each</li>
                    <li>1 “confident” pick worth <b>2 points</b></li>
                  </ul>
                </li>
                <li>🏁 <b>1 Email picks to <i>dddtrifecta@gmail.com</i>.</li>
              </ul>
              <div class="hr"></div>
              <span class="cap">Deadline</span><br/>
              Picks must be submitted at least <b>1 hour</b> before kickoff of the first game the player has selected.
              Already‑started games are ineligible.

              For example, if the player is planning to use a Thursday Night Football game in their picks,
              they must supply <b>ALL</b> picks 1 hour prior to kickoff on Thursday night.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("#### Scoring")
        st.markdown(
            """
            <div class="card big">
              <ul class="list-tight">
                <li>🛡️ <b>Survivor is a gatekeeper</b>:
                  <ul>
                    <li>Survivor <b>win</b> → you earn the sum of your spread points.</li>
                    <li>Survivor <b>loss or tie</b> → <b>0 points</b> for the week.</li>
                  </ul>
                </li>
                <li>⏳ Missed week → <b>0 points</b>.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Buy‑in & Prizes
    st.markdown("#### Buy‑In & Prizes")
    st.markdown(
        """
        <div class="card big">
          <ul class="list-tight">
            <li>💵 <b>Buy‑in:</b> $100 per player</li>
            <li>🧮 <b>Total pot:</b> $100 × number of players</li>
            <li>🏆 <b>Distribution:</b>
              <ul>
                <li>75% → Season overall (1st, 2nd, 3rd)</li>
                <li>5% → Trimester 1 (Weeks 1–6)</li>
                <li>5% → Trimester 2 (Weeks 7–12)</li>
                <li>5% → Trimester 3 (Weeks 13–18)</li>
                <li>10% → Special / Temporary (TBA)</li>
              </ul>
            </li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tie rules & eligibility
    st.markdown("#### Ties & Eligibility")
    st.markdown(
        """
        <div class="card big">
          <ul class="list-tight">
            <li>🤝 Season-end ties → tied players <b>split the prize</b>.</li>
            <li>🗓️ Trimester winners determined solely by points within each 6‑week window.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Helpful notes (expanders)
    with st.expander("Helpful Notes"):
        st.markdown(
            """
            - Email picks to dddtrifecta@gmail.com. 
            - For any additional question please reach out to @Edub1321 or @MrTuxedo on the Discord.  
            """
        )