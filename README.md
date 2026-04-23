# ✈ Aviator Oracle — Kivy Mobile App

A statistical companion app for the Aviator game. Tracks crash points,
analyzes patterns, and suggests data-driven cashout targets.

> ⚠ For entertainment only. Aviator uses provably fair RNG — no system
> can guarantee future outcomes.

---

## Project Structure

```
aviator_oracle/
├── main.py                  # App entry point
├── requirements.txt
├── buildozer.spec           # Android packaging config
├── screens/
│   ├── main_screen.py       # Root screen + tab switching
│   ├── predict_tab.py       # Prediction engine UI
│   ├── history_tab.py       # Log crash points
│   ├── stats_tab.py         # Statistics & charts
│   └── bankroll_tab.py      # Bet sizing calculator
└── utils/
    ├── data_store.py        # JSON persistence layer
    ├── theme.py             # Colors & style constants
    └── widgets.py           # Reusable custom widgets
```

---

## Run on Desktop (Windows / Mac / Linux)

### 1. Install Python 3.10+

### 2. Install dependencies
```bash
pip install kivy==2.3.0
```

### 3. Run
```bash
cd aviator_oracle
python main.py
```
A 400×750px mobile-preview window will open.

---

## Build Android APK

### 1. Install Buildozer (Linux only, or use WSL on Windows)
```bash
pip install buildozer
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
```

### 2. Build debug APK
```bash
cd aviator_oracle
buildozer android debug
```
APK will be at: `bin/aviator_oracle-1.0.0-debug.apk`

### 3. Deploy directly to connected phone
```bash
buildozer android debug deploy run
```

---

## Features

| Tab        | What it does                                              |
|------------|-----------------------------------------------------------|
| Predict    | Animated prediction with strategy modes (Safe → Moon)    |
| History    | Log crash points, delete entries, persists between sessions |
| Stats      | Avg, median, distribution bars, sparkline trend chart    |
| Bankroll   | Bet sizing by risk %, P&L session tracker                 |

---

## Data Persistence
All data is saved to `aviator_data.json` in the app's user data directory.
On Android this is in the app's internal storage. No internet required.
