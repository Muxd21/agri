# Agri-Input Narrative Tracker

This project is an automated tracker for key agricultural and fertilizer companies, designed to monitor their performance and market rotation signals.

## Features

- **Automated Updates**: Runs daily at midnight UTC via GitHub Actions.
- **Company Tracking**: Monitors Nutrien (NTR), SABIC Agri-Nutrients (2020), Ma'aden (1211), and Almarai (2280).
- **52-Week Low Alerts**: Highlights stocks trading near their historical lows (within 10%).
- **Rotation Signals**: Tracks the ratio of Agri-stocks vs Tech (QQQ) and the local Saudi market (TASI) to identify potential market re-ratings.
- **Static Dashboard**: A clean, responsive dashboard hosted on GitHub Pages.

## Tech Stack

- **Backend**: Python with `yfinance` for data retrieval.
- **Frontend**: HTML5 with Tailwind CSS.
- **Automation**: GitHub Actions.
- **Hosting**: GitHub Pages.

## Local Setup

If you want to run the tracker locally:

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the tracker:
   ```bash
   python tracker.py
   ```
4. Open `index.html` in your browser.

## Project Structure

- `tracker.py`: The main script that fetches data and generates the dashboard.
- `index.html`: The generated dashboard (do not edit directly, it is overwritten by the script).
- `.github/workflows/update.yml`: GitHub Actions configuration for automation.
- `requirements.txt`: Python dependencies.
