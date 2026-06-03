# Data Dictionary
## Bluestock Fintech – Mutual Fund Analysis Project

**Last updated:** 2025-06-03  
**Author:** Bluestock Intern  
**Database:** bluestock_mf.db (SQLite)  
**Source:** AMFI India, mfapi.in

---

## Table of Contents
1. [dim_fund](#1-dim_fund)
2. [dim_date](#2-dim_date)
3. [fact_nav](#3-fact_nav)
4. [fact_transactions](#4-fact_transactions)
5. [fact_performance](#5-fact_performance)
6. [fact_aum](#6-fact_aum)
7. [fact_portfolio](#7-fact_portfolio)

---

## 1. dim_fund

**Source file:** `01_fund_master_clean.csv`  
**Description:** Master reference table for all mutual fund schemes. One row per scheme.

| Column | Type | Business Definition |
|--------|------|---------------------|
| amfi_code | INTEGER (PK) | Unique scheme identifier issued by AMFI India. 6-digit integer. Used as the primary key to join all datasets. |
| fund_house | TEXT | Name of the Asset Management Company (AMC) that manages the fund. E.g. "SBI Mutual Fund". |
| scheme_name | TEXT | Full official name of the scheme including plan and option. E.g. "SBI Bluechip Fund - Direct Plan - Growth". |
| category | TEXT | Broad SEBI category. Either "Equity" or "Debt". |
| sub_category | TEXT | SEBI sub-category. E.g. Large Cap, Mid Cap, Small Cap, Gilt, Liquid, ELSS. |
| plan | TEXT | Either "Regular" (sold via distributor, higher expense) or "Direct" (bought directly, lower expense). |
| launch_date | TEXT | Date the scheme was first open for investment. Format: YYYY-MM-DD. |
| benchmark | TEXT | Index the fund's performance is measured against. E.g. "NIFTY 100 TRI". |
| expense_ratio_pct | REAL | Annual fee charged by the fund house as % of AUM. Lower is better for investor. Typical range: 0.1% – 2.5%. |
| exit_load_pct | REAL | Fee charged when investor redeems units before a specified period. Usually 1% if redeemed within 1 year. |
| min_sip_amount | INTEGER | Minimum monthly amount (₹) required to start a SIP in this scheme. |
| min_lumpsum_amount | INTEGER | Minimum one-time investment amount (₹) in this scheme. |
| fund_manager | TEXT | Name of the fund manager responsible for investment decisions. |
| risk_category | TEXT | SEBI mandated risk label: Low / Moderate / Moderately High / High / Very High. |
| sebi_category_code | TEXT | Internal SEBI code for the scheme category. E.g. EC01 = Equity Large Cap. |

---

## 2. dim_date

**Source:** Generated from nav_history date range  
**Description:** Date dimension table for time-based analysis. One row per calendar date.

| Column | Type | Business Definition |
|--------|------|---------------------|
| date_id | TEXT (PK) | Calendar date in YYYY-MM-DD format. Primary key. |
| year | INTEGER | Calendar year. E.g. 2024. |
| quarter | INTEGER | Quarter of the year (1–4). Q1 = Jan-Mar. |
| month | INTEGER | Month number (1–12). |
| month_name | TEXT | Full month name. E.g. "January". |
| week | INTEGER | ISO week number of the year (1–53). |
| day | INTEGER | Day of the month (1–31). |
| day_name | TEXT | Day of the week name. E.g. "Monday". |
| is_weekend | INTEGER | 1 if Saturday or Sunday, 0 otherwise. |

---

## 3. fact_nav

**Source file:** `02_nav_history_clean.csv`  
**Description:** Daily NAV (price per unit) for each scheme. Forward-filled for weekends and holidays.

| Column | Type | Business Definition |
|--------|------|---------------------|
| amfi_code | INTEGER (FK) | References dim_fund. Identifies which scheme this NAV belongs to. |
| date_id | TEXT (FK) | References dim_date. The date for this NAV value. Format: YYYY-MM-DD. |
| nav | REAL | Net Asset Value — the price of 1 unit of the fund on that date. In Indian Rupees (₹). Updated daily after market close. |

**Notes:**
- Raw data had 46,000 rows. After forward-filling weekends/holidays, expanded to 64,320 rows.
- NAV values validated to be > 0.
- Sorted by amfi_code + date_id.

---

## 4. fact_transactions

**Source file:** `08_investor_transactions_clean.csv`  
**Description:** Individual investor buy/sell transactions. One row per transaction.

| Column | Type | Business Definition |
|--------|------|---------------------|
| investor_id | TEXT | Anonymised unique identifier for each investor. Format: INVxxxxxx. |
| transaction_date | TEXT | Date the transaction was processed. Format: YYYY-MM-DD. |
| amfi_code | INTEGER (FK) | References dim_fund. The scheme invested in / redeemed from. |
| transaction_type | TEXT | Type of transaction. One of: SIP (monthly auto-debit), Lumpsum (one-time purchase), Redemption (withdrawal). |
| amount_inr | INTEGER | Transaction amount in Indian Rupees (₹). Validated > 0. |
| state | TEXT | Indian state where the investor is located. |
| city | TEXT | City where the investor is located. |
| city_tier | TEXT | City classification: T30 (top 30 cities), B30 (beyond top 30). |
| age_group | TEXT | Investor age bracket. E.g. "18-25", "26-35", "36-45", "46-55", "56+". |
| gender | TEXT | Investor gender: Male / Female. |
| annual_income_lakh | REAL | Investor's annual income in Indian Lakhs (1 Lakh = ₹100,000). |
| payment_mode | TEXT | How the transaction was paid. E.g. UPI, Mandate, Cheque, Net Banking. |
| kyc_status | TEXT | KYC (Know Your Customer) verification status. Either "Verified" or "Pending". Verified required for most investments. |

---

## 5. fact_performance

**Source file:** `07_scheme_performance_clean.csv`  
**Description:** Risk and return metrics for each scheme. One row per scheme.

| Column | Type | Business Definition |
|--------|------|---------------------|
| amfi_code | INTEGER (FK) | References dim_fund. |
| return_1yr_pct | REAL | Absolute return of the fund over the last 1 year (%). Higher is better. |
| return_3yr_pct | REAL | Annualised return over the last 3 years (%). Key metric for medium-term evaluation. |
| return_5yr_pct | REAL | Annualised return over the last 5 years (%). Key metric for long-term evaluation. |
| benchmark_3yr_pct | REAL | 3-year annualised return of the fund's benchmark index. Used to measure outperformance. |
| alpha | REAL | Excess return over benchmark after adjusting for market risk. Positive alpha = fund manager added value. |
| beta | REAL | Sensitivity of the fund to market movements. Beta > 1 means more volatile than market. |
| sharpe_ratio | REAL | Return earned per unit of total risk (std deviation). Higher is better. Above 1 is considered good. |
| sortino_ratio | REAL | Like Sharpe but only penalises downside risk. Higher is better. |
| std_dev_ann_pct | REAL | Annualised standard deviation of returns (%). Measures volatility. Lower means more stable. |
| max_drawdown_pct | REAL | Largest peak-to-trough decline in fund value (%). Negative number — closer to 0 is better. |
| aum_crore | INTEGER | Assets Under Management in Indian Crores (1 Crore = ₹10 million). Larger AUM = larger fund. |
| expense_ratio_pct | REAL | Annual management fee as % of AUM. Lower is better for investor returns. |
| morningstar_rating | INTEGER | Morningstar star rating (1–5). 5 stars = top performing in category. |
| risk_grade | TEXT | Qualitative risk label: Low / Moderate / Moderately High / High / Very High. |

---

## 6. fact_aum

**Source file:** `03_aum_by_fund_house_clean.csv`  
**Description:** AUM data per fund house per quarter. Tracks industry size over time.

| Column | Type | Business Definition |
|--------|------|---------------------|
| date_id | TEXT (FK) | Quarter-end date. References dim_date. Format: YYYY-MM-DD. |
| fund_house | TEXT | Name of the Asset Management Company. |
| aum_lakh_crore | REAL | AUM in Lakh Crores (1 Lakh Crore = ₹1 Trillion). Used for industry-level reporting. |
| aum_crore | INTEGER | AUM in Crores. Used for fund-house level comparison. |
| num_schemes | INTEGER | Total number of schemes managed by this fund house at that date. |

---

## 7. fact_portfolio

**Source file:** `09_portfolio_holdings_clean.csv`  
**Description:** Stock-level holdings of each mutual fund scheme.

| Column | Type | Business Definition |
|--------|------|---------------------|
| amfi_code | INTEGER (FK) | References dim_fund. The scheme holding this stock. |
| stock_symbol | TEXT | NSE/BSE ticker symbol of the stock. E.g. "HDFCBANK". |
| stock_name | TEXT | Full company name. E.g. "HDFC Bank Ltd". |
| sector | TEXT | Industry sector of the stock. E.g. Banking, IT, Utilities, FMCG. |
| weight_pct | REAL | Percentage of the fund's total portfolio allocated to this stock. All holdings for a fund sum to ~100%. |
| market_value_cr | REAL | Current market value of the fund's holding in this stock, in Crores (₹). |
| current_price_inr | REAL | Current market price per share of the stock in Indian Rupees. |
| portfolio_date | TEXT | Date as of which the portfolio snapshot was taken. Format: YYYY-MM-DD. |

---

## Key Business Definitions

| Term | Definition |
|------|------------|
| NAV | Net Asset Value. Price of 1 unit of a mutual fund. Calculated daily as (Total Assets - Liabilities) / Number of Units. |
| SIP | Systematic Investment Plan. Fixed amount invested monthly automatically. |
| AUM | Assets Under Management. Total market value of all investments managed by a fund house. |
| AMFI | Association of Mutual Funds in India. Regulatory body that assigns scheme codes. |
| SEBI | Securities and Exchange Board of India. Regulates all mutual funds. |
| Direct Plan | Fund bought directly from AMC without distributor. Lower expense ratio. |
| Regular Plan | Fund bought through a distributor/agent. Higher expense ratio due to commission. |
| Expense Ratio | Annual fee charged by fund house, expressed as % of AUM. Deducted daily from NAV. |
| Exit Load | Penalty fee if investor redeems within a specified period (usually 1 year). |
| Alpha | Fund manager's value-add above benchmark. Positive = outperformance. |
| Beta | Market sensitivity. Beta of 1.2 means fund moves 1.2x the market. |
| Sharpe Ratio | Risk-adjusted return. (Return - Risk-free rate) / Standard Deviation. |
| KYC | Know Your Customer. Mandatory identity verification for all investors in India. |
| T30/B30 | Top 30 cities (T30) vs Beyond top 30 cities (B30). SEBI classification for investor geography. |
