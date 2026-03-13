import streamlit as st
import pandas as pd
import json
import os
import time
import random
from datetime import datetime
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPAS Sub Dean Election",
    page_icon="🗳️",
    layout="centered",
)

VOTES_CSV     = "votes.csv"
ATTEMPTS_JSON = "voted_devices.json"
CANDIDATES    = ["Awo", "Ade"]
COUNTDOWN_SEC = 10   # countdown after voting before page closes

# ─────────────────────────────────────────────────────────────────────────────
#  FILE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def load_voted():
    """Returns dict  {device_id: staff_id, ...}  and set of voted staff IDs."""
    if os.path.exists(ATTEMPTS_JSON):
        with open(ATTEMPTS_JSON) as f:
            return json.load(f)
    return {}

def save_voted(data: dict):
    with open(ATTEMPTS_JSON, "w") as f:
        json.dump(data, f)

def record_vote(staff_id: str, candidate: str, device_id: str):
    row = pd.DataFrame([{
        "Timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Staff_ID":   staff_id.upper(),
        "Candidate":  candidate,
        "Device_ID":  device_id,
    }])
    if os.path.exists(VOTES_CSV):
        row.to_csv(VOTES_CSV, mode="a", header=False, index=False)
    else:
        row.to_csv(VOTES_CSV, index=False)

def load_votes():
    if os.path.exists(VOTES_CSV):
        return pd.read_csv(VOTES_CSV)
    return pd.DataFrame(columns=["Timestamp", "Staff_ID", "Candidate", "Device_ID"])

def get_counts():
    df = load_votes()
    counts = {c: 0 for c in CANDIDATES}
    if not df.empty:
        vc = df["Candidate"].value_counts().to_dict()
        for c in CANDIDATES:
            counts[c] = vc.get(c, 0)
    return counts

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "page":       "login",   # login | vote | thankyou | closed | blocked
    "staff_id":   "",
    "device_id":  str(random.getrandbits(64)),
    "voted_for":  "",
    "vote_time":  None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
#  PIE CHART HELPER
# ─────────────────────────────────────────────────────────────────────────────
def make_pie(counts: dict):
    labels = list(counts.keys())
    values = list(counts.values())
    total  = sum(values)

    colors = ["#1a6bbf", "#e05b2e"]

    if total == 0:
        fig = go.Figure(go.Pie(
            labels=labels,
            values=[1, 1],
            hole=0.45,
            marker_colors=colors,
            textinfo="label",
            hoverinfo="skip",
        ))
        fig.add_annotation(text="No votes yet", x=0.5, y=0.5,
                           font_size=14, showarrow=False)
    else:
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker_colors=colors,
            textinfo="label+percent+value",
            hovertemplate="%{label}: %{value} votes (%{percent})<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>{total}</b><br>votes",
            x=0.5, y=0.5, font_size=16, showarrow=False,
        )

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", y=-0.1),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.top-bar {
    background: linear-gradient(90deg, #0a3d62, #1a6bbf);
    color: white; padding: 18px 24px; border-radius: 12px; margin-bottom: 20px;
}
.top-bar h1 { margin: 0; font-size: 1.45rem; letter-spacing:.3px; }
.top-bar p  { margin: 5px 0 0; font-size: .85rem; opacity: .88; }

.cand-card {
    border: 2px solid #dee2e6; border-radius: 14px;
    padding: 24px 18px; text-align: center; cursor: pointer;
    transition: all .2s;
}
.cand-card:hover { border-color: #1a6bbf; background: #f0f6ff; }
.cand-name  { font-size: 1.5rem; font-weight: 700; margin-bottom: 6px; }
.cand-label { font-size: .82rem; color: #6c757d; }

.vote-banner { background:#d1e7dd; border:2px solid #0f5132; color:#0f5132;
               border-radius:12px; padding:22px; text-align:center;
               font-size:1.1rem; font-weight:600; margin-bottom:16px; }
.blocked-box { background:#f8d7da; border:2px solid #842029; color:#842029;
               border-radius:12px; padding:22px; text-align:center;
               font-size:1.05rem; }
.timer-box  { background:#fff3cd; border:1.5px solid #ffc107; color:#856404;
              border-radius:8px; padding:10px; font-size:1.2rem;
              font-weight:700; text-align:center; margin:12px 0; }
.closed-box { background:#0a3d62; color:white; border-radius:14px;
              padding:30px; text-align:center; }
.stat-row   { display:flex; gap:12px; margin-bottom:8px; }
.stat-card  { flex:1; background:#f8f9fa; border:1px solid #dee2e6;
              border-radius:10px; padding:14px; text-align:center; }
.stat-num   { font-size:2rem; font-weight:700; }
.stat-lbl   { font-size:.8rem; color:#6c757d; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SHARED HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_header(subtitle=""):
    st.markdown(f"""
    <div class="top-bar">
        <h1>🗳️ SPAS — SUB DEAN ELECTION</h1>
        <p>Candidates: &nbsp;<strong>AWO</strong> &nbsp;vs&nbsp; <strong>ADE</strong>
           {"&nbsp;&nbsp;|&nbsp;&nbsp;" + subtitle if subtitle else ""}</p>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  LIVE STATS (used on vote + thankyou pages)
# ─────────────────────────────────────────────────────────────────────────────
def render_live_stats():
    counts = get_counts()
    total  = sum(counts.values())
    st.markdown("#### 📊 Live Voting Results")

    # Stat cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num" style="color:#1a6bbf">{counts['Awo']}</div>
            <div class="stat-lbl">AWO votes</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num" style="color:#e05b2e">{counts['Ade']}</div>
            <div class="stat-lbl">ADE votes</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num">{total}</div>
            <div class="stat-lbl">Total votes</div>
        </div>""", unsafe_allow_html=True)

    st.plotly_chart(make_pie(counts), use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: LOGIN
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    render_header("Staff Login")

    st.markdown("### 🔐 Enter your Staff ID to vote")
    sid = st.text_input(
        "Staff ID (alphanumeric, max 7 characters):",
        max_chars=7,
        placeholder="e.g. AB12345",
    )

    if st.button("Proceed to Vote", type="primary", use_container_width=True):
        sid = sid.strip().upper()
        if not sid:
            st.error("Please enter your Staff ID.")
        elif not sid.isalnum():
            st.error("Staff ID must be alphanumeric (letters and numbers only).")
        elif len(sid) < 2:
            st.error("Staff ID must be at least 2 characters.")
        else:
            voted_data = load_voted()
            dev_id     = st.session_state.device_id
            voted_ids  = set(voted_data.values())

            # Block if same device OR same staff ID already used
            if dev_id in voted_data or sid in voted_ids:
                st.session_state.staff_id = sid
                st.session_state.page     = "blocked"
                st.rerun()
            else:
                st.session_state.staff_id = sid
                st.session_state.page     = "vote"
                st.rerun()

    st.divider()
    render_live_stats()

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: VOTE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "vote":
    render_header(f"Voting — Staff: {st.session_state.staff_id}")

    st.markdown("### 🗳️ Cast Your Vote")
    st.markdown("Select your preferred candidate for **Sub Dean, School of SPAS:**")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="cand-card">
            <div style="font-size:2.5rem">👤</div>
            <div class="cand-name" style="color:#1a6bbf">AWO</div>
            <div class="cand-label">Candidate 1</div>
        </div>""", unsafe_allow_html=True)
        st.write("")
        if st.button("✅  Vote for AWO", type="primary", use_container_width=True):
            dev_id    = st.session_state.device_id
            staff_id  = st.session_state.staff_id
            voted_data = load_voted()
            voted_ids  = set(voted_data.values())

            if dev_id in voted_data or staff_id in voted_ids:
                st.session_state.page = "blocked"
                st.rerun()
            else:
                record_vote(staff_id, "Awo", dev_id)
                voted_data[dev_id] = staff_id
                save_voted(voted_data)
                st.session_state.voted_for = "Awo"
                st.session_state.vote_time = time.time()
                st.session_state.page      = "thankyou"
                st.rerun()

    with col2:
        st.markdown("""
        <div class="cand-card">
            <div style="font-size:2.5rem">👤</div>
            <div class="cand-name" style="color:#e05b2e">ADE</div>
            <div class="cand-label">Candidate 2</div>
        </div>""", unsafe_allow_html=True)
        st.write("")
        if st.button("✅  Vote for ADE", type="primary", use_container_width=True):
            dev_id    = st.session_state.device_id
            staff_id  = st.session_state.staff_id
            voted_data = load_voted()
            voted_ids  = set(voted_data.values())

            if dev_id in voted_data or staff_id in voted_ids:
                st.session_state.page = "blocked"
                st.rerun()
            else:
                record_vote(staff_id, "Ade", dev_id)
                voted_data[dev_id] = staff_id
                save_voted(voted_data)
                st.session_state.voted_for = "Ade"
                st.session_state.vote_time = time.time()
                st.session_state.page      = "thankyou"
                st.rerun()

    st.divider()
    render_live_stats()

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: THANK YOU  (10-second countdown then closes)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "thankyou":
    render_header("Vote Recorded!")

    voted_for = st.session_state.voted_for
    color     = "#1a6bbf" if voted_for == "Awo" else "#e05b2e"

    st.markdown(f"""
    <div class="vote-banner">
        🎉 Thank you, <strong>{st.session_state.staff_id}</strong>!<br>
        Your vote for <span style="color:{color}; font-size:1.3rem;">
        <strong>{voted_for.upper()}</strong></span> has been recorded.
    </div>""", unsafe_allow_html=True)

    # Countdown
    elapsed   = time.time() - st.session_state.vote_time
    remaining = max(0, COUNTDOWN_SEC - int(elapsed))

    if remaining > 0:
        st.markdown(
            f'<div class="timer-box">🔒 This page will close in <strong>{remaining}</strong> second{"s" if remaining != 1 else ""}...</div>',
            unsafe_allow_html=True,
        )
        render_live_stats()
        # Re-run every second using a short sleep + rerun (safe — no meta refresh)
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.page = "closed"
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: CLOSED
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "closed":
    render_header()
    st.markdown("""
    <div class="closed-box">
        <div style="font-size:3rem">🔒</div>
        <div style="font-size:1.4rem; font-weight:700; margin:10px 0;">
            Your session has closed.
        </div>
        <div style="opacity:.85; font-size:.95rem;">
            Your vote has been recorded. Thank you for participating in the<br>
            <strong>School of SPAS Sub Dean Election.</strong>
        </div>
    </div>""", unsafe_allow_html=True)

    st.write("")
    render_live_stats()

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: BLOCKED
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "blocked":
    render_header()
    st.markdown(f"""
    <div class="blocked-box">
        <div style="font-size:2.5rem">⛔</div>
        <div style="font-size:1.2rem; font-weight:700; margin:10px 0;">
            Vote Not Allowed
        </div>
        <div style="font-size:.95rem;">
            Staff ID <strong>{st.session_state.staff_id}</strong> has already voted,
            or this device has already been used to cast a vote.<br><br>
            Each staff member may only vote <strong>once</strong>.
        </div>
    </div>""", unsafe_allow_html=True)

    st.write("")

    render_live_stats()
