# Bluestock Fintech – Mutual Fund Analysis Project

An end-to-end mutual fund analytics pipeline built during my internship at [Bluestock Fintech](https://bluestock.in/).

## Project Structure

```
bluestock_mf_analysis/
├── data/
│   ├── raw/            ← original CSVs + live NAV downloads
│   └── processed/      ← cleaned & feature-engineered datasets
├── notebooks/          ← exploratory Jupyter notebooks
├── sql/                ← schema DDL + analytical queries
├── dashboard/          ← Plotly Dash / Streamlit app files
├── reports/            ← PDF / HTML reports
├── data_ingestion.py   ← Task 1–3, 6–7: load & validate all datasets
├── live_nav_fetch.py   ← Task 4–5: fetch live NAV from mfapi.in
├── requirements.txt    ← Python dependencies
└── README.md
```

## Datasets (10 CSVs)

| # | File | Description | Rows |
|---|------|-------------|------|
| 1 | 01_fund_master.csv | Scheme metadata (AMFI code, fund house, category, risk) | 40 |
| 2 | 02_nav_history.csv | Daily NAV for all schemes | ~46,000 |
| 3 | 03_aum_by_fund_house.csv | AUM per fund house per quarter | 90 |
| 4 | 04_monthly_sip_inflows.csv | Industry SIP statistics monthly | 48 |
| 5 | 05_category_inflows.csv | Net inflows by equity category | 144 |
| 6 | 06_industry_folio_count.csv | Folio counts by type | 21 |
| 7 | 07_scheme_performance.csv | Returns, alpha, beta, Sharpe, Sortino | 40 |
| 8 | 08_investor_transactions.csv | Investor buy/sell transactions | ~32,778 |
| 9 | 09_portfolio_holdings.csv | Stock-level holdings per scheme | 322 |
| 10 | 10_benchmark_indices.csv | NIFTY50 / NIFTY Midcap etc. daily close | ~8,050 |

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/bluestock_mf_analysis.git
cd bluestock_mf_analysis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run data ingestion
python data_ingestion.py

# 5. Fetch live NAV
python live_nav_fetch.py
```

## Day-by-Day Progress

| Day | Deliverable | Status |
|-----|-------------|--------|
| 1   | Data ingestion, live NAV fetch | ✅ Complete |
| 2   | Data cleaning & EDA | 🔜 |
| 3   | SQL schema & queries | 🔜 |
| 4   | Dashboard | 🔜 |
| 5   | Final report | 🔜 |

## Live NAV API

Source: [mfapi.in](https://www.mfapi.in/)  
Endpoint: `GET https://api.mfapi.in/mf/{amfi_code}`

Schemes tracked: HDFC Top 100 (125497), SBI Bluechip (119551), ICICI Bluechip (120503), Nippon Large Cap (118632), Axis Bluechip (119092), Kotak Bluechip (120841).
