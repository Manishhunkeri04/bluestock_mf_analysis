# Bluestock Fintech — Mutual Fund Analytics Project

A full-stack mutual fund analytics pipeline built during a 7-day internship at [Bluestock Fintech](https://bluestock.in/). The project covers data ingestion, cleaning, SQL database design, exploratory data analysis, quantitative performance analytics, and an interactive Power BI dashboard — all built from scratch.

---

## Project Overview

| Item | Detail |
|------|--------|
| Schemes analysed | 40 mutual fund schemes across 10 AMCs |
| Data period | January 2022 – May 2026 |
| NAV records | 64,320 (after forward-filling weekends) |
| Investor transactions | 32,778 across 5,000 unique investors |
| Database tables | 11 (2 dimension + 5 fact + 4 supplementary) |
| Dashboard pages | 4 (Industry, Performance, Investors, SIP Trends) |

---

## Project Structure

```
bluestock_mf_analysis/
├── data/
│   ├── raw/                         ← original CSVs + live NAV downloads
│   └── processed/                   ← cleaned datasets + derived CSVs
├── notebooks/
│   ├── EDA_Analysis.ipynb           ← 15 EDA charts
│   ├── Performance_Analytics.ipynb  ← CAGR, Sharpe, drawdown, scorecard
│   └── Advanced_Analytics.ipynb     ← VaR, cohort, HHI, recommender
├── dashboard/
│   └── bluestock_mf_dashboard.pbix  ← Power BI dashboard
├── reports/
│   ├── data_dictionary.md
│   ├── data_quality_report.md
│   └── Final_Report.pdf
├── sql/
│   ├── schema.sql                   ← SQLite star schema DDL
│   └── queries.sql                  ← 10 analytical SQL queries
├── data_ingestion.py                ← load and explore all datasets
├── live_nav_fetch.py                ← fetch live NAV from mfapi.in
├── data_cleaning.py                 ← clean all 10 datasets
├── db_loader.py                     ← load into SQLite via SQLAlchemy
├── recommender.py                   ← fund recommender by risk appetite
├── run_pipeline.py                  ← master script — runs everything
├── bluestock_mf.db                  ← SQLite database (11 tables)
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.11 or newer — https://python.org
- Git — https://git-scm.com
- Power BI Desktop (for dashboard) — https://powerbi.microsoft.com/desktop

### 2. Clone the repo
```bash
git clone https://github.com/Manishhunkeri04/bluestock_mf_analysis.git
cd bluestock_mf_analysis
```

### 3. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run the ETL Pipeline

### Option A — Run everything at once
```bash
python run_pipeline.py
```

### Option B — Run each step individually
```bash
python data_ingestion.py    # Step 1: explore raw data
python live_nav_fetch.py    # Step 2: fetch live NAV from mfapi.in
python data_cleaning.py     # Step 3: clean all 10 datasets
python db_loader.py         # Step 4: load into SQLite
```

### Run the fund recommender
```bash
python recommender.py
```

### Open Jupyter notebooks
```bash
jupyter notebook
```
Then open any notebook from the `notebooks/` folder and click **Kernel → Restart & Run All**.

---

## How to Open the Dashboard

1. Open **Power BI Desktop**
2. Click **File → Open**
3. Navigate to `dashboard/bluestock_mf_dashboard.pbix`
4. Click **Refresh** to reload the latest data

### Dashboard Pages
| Page | Contents |
|------|----------|
| Industry Overview | AUM trends, KPI cards, fund house ranking |
| Fund Performance | Scatter plot, scorecard table, slicers |
| Investor Analytics | Demographics, state map, transaction split |
| SIP & Market Trends | SIP growth, category heatmap, benchmarks |

---

## Dataset Descriptions

| File | Rows | Description |
|------|------|-------------|
| 01_fund_master.csv | 40 | Scheme metadata — AMFI code, fund house, category, risk grade |
| 02_nav_history.csv | 46,000 | Daily NAV for all 40 schemes (2022–2026) |
| 03_aum_by_fund_house.csv | 90 | Quarterly AUM per fund house |
| 04_monthly_sip_inflows.csv | 48 | Industry SIP statistics per month |
| 05_category_inflows.csv | 144 | Net inflows by fund category |
| 06_industry_folio_count.csv | 21 | Total investor folios by type |
| 07_scheme_performance.csv | 40 | Returns, alpha, beta, Sharpe, Sortino |
| 08_investor_transactions.csv | 32,778 | Individual investor buy/sell records |
| 09_portfolio_holdings.csv | 322 | Stock-level fund holdings |
| 10_benchmark_indices.csv | 8,050 | NIFTY50, NIFTY100, Midcap daily close |

---

## Key Deliverables by Day

| Day | Deliverable |
|-----|-------------|
| 1 | data_ingestion.py, live_nav_fetch.py, requirements.txt |
| 2 | data_cleaning.py, db_loader.py, schema.sql, queries.sql, data_dictionary.md |
| 3 | EDA_Analysis.ipynb (15 charts, 10 key findings) |
| 4 | Performance_Analytics.ipynb (CAGR, Sharpe, Alpha, Beta, Drawdown, Scorecard) |
| 5 | Power BI Dashboard (4 pages, dark theme) |
| 6 | Advanced_Analytics.ipynb, var_cvar_report.csv, recommender.py |
| 7 | Final_Report.pdf, Bluestock_MF_Presentation.pptx, README.md, v1.0 tag |

---

## Technologies Used

- **Python** — Pandas, NumPy, Matplotlib, Seaborn, Plotly, SQLAlchemy, SciPy
- **SQL** — SQLite with star schema (dim_fund, dim_date, fact_nav, fact_transactions, etc.)
- **Power BI** — Interactive dashboard with 4 pages and cross-filtering
- **Jupyter** — Notebooks for EDA, performance, and advanced analytics
- **Git / GitHub** — Version control with v1.0 release tag

---

## Author

**Manish**
Intern at Bluestock Fintech | June 2026
GitHub: https://github.com/Manishhunkeri04

---

## Disclaimer

This project uses synthetic and publicly available data for educational purposes. All analysis is for learning and demonstration only — not financial advice.
