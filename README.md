# 🗳️ Short Time Voting System

A secure, real-time digital election platform built with **Python + Streamlit** for the **School of SPAS Sub Dean Election**. Staff authenticate with their Staff ID, cast a single vote for their preferred candidate, and watch live results update instantly via an interactive pie chart.

---

## 📸 Overview

| Detail | Value |
|---|---|
| **Election** | School of SPAS — Sub Dean |
| **Candidates** | AWO (Candidate 1) · ADE (Candidate 2) |
| **Authentication** | Alphanumeric Staff ID (max 7 characters) |
| **Post-vote countdown** | 10 seconds before session closes |
| **Anti-cheat** | Dual lock — same device AND same Staff ID |
| **Live results** | Interactive Plotly donut chart, visible on every page |
| **Data export** | `votes.csv` — full timestamped audit log |

---

## ✨ Features

- **Staff ID login** — alphanumeric IDs up to 7 characters, validated for format before access is granted
- **Live pie chart** — Plotly donut chart shows vote counts and percentages in real time, updating on every page
- **Dual anti-cheat protection** — blocks the same device fingerprint AND the same Staff ID, even across different devices
- **10-second auto-close** — after voting, a countdown runs while showing live results, then the session locks permanently
- **Personalised confirmation** — thank-you banner names the staff member and their chosen candidate
- **Blocked page** — clear error message if a duplicate attempt is detected, with live results still visible
- **CSV audit trail** — every vote appended to `votes.csv` with timestamp, Staff ID, candidate, and device fingerprint
- **Single-file app** — entire application in one Python file, no complex setup required

---

## 🔐 Security Model

Two independent fraud barriers are enforced on every login and at the exact moment of casting:

### Barrier 1 — Device fingerprint lock
Each browser session generates a random 64-bit integer as a device ID stored in Streamlit `session_state`. Once a vote is cast from a device, that fingerprint is written permanently to `voted_devices.json`. Any future attempt from the same session is rejected immediately.

### Barrier 2 — Staff ID lock
The set of all Staff IDs that have already voted is extracted from `voted_devices.json` on every login. If the entered Staff ID appears in that set, access is denied — even if the person is using a completely different device or browser.

### Race-condition protection
The anti-cheat check fires **twice** — once on the login page and again at the exact moment the vote button is clicked — preventing any gap between validation and record writing.

---

## 🖥️ App Pages

| Page | Description |
|---|---|
| `login` | Staff ID entry and validation; live results shown below |
| `vote` | Candidate selection with AWO and ADE cards; live results below |
| `thankyou` | Confirmation banner + 10-second countdown + live results |
| `closed` | Permanent session lock screen after countdown ends |
| `blocked` | Shown if device or Staff ID has already voted |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/olumobigjoe/spas-voting-system.git
cd spas-voting-system
```

### 2. Install dependencies

```bash
pip install streamlit pandas plotly
```

### 3. Run the app

```bash
streamlit run voting_app.py
```

The app opens at `http://localhost:8501`.

### 4. Share with staff

Share the **Network URL** shown in your terminal with staff on the same Wi-Fi network:

```
Local URL:   http://localhost:8501
Network URL: http://192.168.x.x:8501
```

For wider access, deploy to **Streamlit Cloud** (free) — see the deployment section below.

---

## 📁 File Structure

```
spas-voting-system/
├── voting_app.py           ← entire application (single file)
├── README.md               ← this file
├── requirements.txt        ← Python dependencies
└── data/                   (auto-created at runtime)
    ├── voted_devices.json  ← device + Staff ID fingerprints
    └── votes.csv           ← full timestamped vote audit log
```

### `votes.csv` columns

| Column | Description |
|---|---|
| `Timestamp` | Date and time the vote was cast (`YYYY-MM-DD HH:MM:SS`) |
| `Staff_ID` | Staff ID in uppercase |
| `Candidate` | Name of the candidate voted for (`Awo` or `Ade`) |
| `Device_ID` | 64-bit device fingerprint for audit purposes |

### `voted_devices.json` structure

```json
{
  "8291048576392847362": "AB12345",
  "7461920384756102938": "CD67890"
}
```

Each key is a device fingerprint; each value is the Staff ID that used it.

---

## ⚙️ Configuration

All settings are constants at the top of `voting_app.py`:

```python
VOTES_CSV     = "votes.csv"          # output path for vote audit log
ATTEMPTS_JSON = "voted_devices.json" # path for device/staff ID lock store
CANDIDATES    = ["Awo", "Ade"]       # candidate names — change to any names
COUNTDOWN_SEC = 10                   # seconds before page closes after voting
```

To adapt this for a different election, simply change `CANDIDATES` to the new names.

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Python 3** | Core language |
| **Streamlit** | Web UI framework |
| **Plotly** | Interactive live pie chart |
| **Pandas** | CSV read/write for vote records |
| **json** | Persistent device + Staff ID lock store |
| **time / random** | Countdown logic and device fingerprinting |

---

## 🌐 Deploying to Streamlit Cloud (Free)

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select this repo → set the main file to `voting_app.py`.
4. Click **Deploy** — you will receive a public URL to share with all staff.

> **Note:** On Streamlit Cloud, `votes.csv` and `voted_devices.json` are stored in the app's ephemeral filesystem. They will reset on app restart. For a persistent election, run the app locally on a dedicated machine, or connect a cloud database.

---

## 🔄 Resetting Between Elections

To clear all votes and device locks before a new election, delete the auto-generated data files:

```bash
rm votes.csv voted_devices.json
```

Then restart the app:

```bash
streamlit run voting_app.py
```

---

## 📊 Viewing Results

During the election, live results are visible on every page of the app as an interactive pie chart.

After the election, open `votes.csv` directly in Excel, Google Sheets, or any CSV viewer for a full audit log. You can also load it in Python for analysis:

```python
import pandas as pd

df = pd.read_csv("votes.csv")
print(df["Candidate"].value_counts())
print(df.groupby("Candidate").size().reset_index(name="Votes"))
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built for the School of SPAS Sub Dean Election · Python + Streamlit + Plotly*
