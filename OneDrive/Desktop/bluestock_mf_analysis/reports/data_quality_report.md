# Data Quality Report
**Project:** Bluestock Fintech Mutual Fund Analysis  
**Day:** 2  

## Dataset Summary

| Dataset | Rows | Total Nulls | Duplicates | Notes |
|---------|------|-------------|------------|-------|
| fund_master | 40 | 0 | 0 | Clean |
| nav_history | 64,320 | 0 | 0 | Clean |
| aum_by_fund_house | 90 | 0 | 0 | Clean |
| monthly_sip_inflows | 48 | 12 | 0 | 12 nulls in yoy_growth_pct are expected (no prior year data) |
| category_inflows | 144 | 0 | 0 | Clean |
| industry_folio_count | 21 | 0 | 0 | Clean |
| scheme_performance | 40 | 0 | 0 | Clean |
| investor_transactions | 32,778 | 0 | 0 | Clean |
| portfolio_holdings | 322 | 0 | 0 | Clean |
| benchmark_indices | 8,050 | 0 | 0 | Clean |

## Key Validation Results

- All 40 AMFI codes in fund_master exist in nav_history — 0 orphan codes
- NAV history expanded from 46,000 to 64,320 rows after forward-filling weekends/holidays
- investor_transactions: all amounts > 0, KYC values are Verified/Pending only
- scheme_performance: expense_ratio range 0.55% to 1.64% (within SEBI 0.1%-2.5% limit)
- All date columns converted to YYYY-MM-DD format for SQLite compatibility

## SQLite Tables Loaded

| Table | Rows | Category |
|-------|------|----------|
| dim_fund | 40 | Dimension |
| dim_date | 1,608 | Dimension |
| fact_nav | 64,320 | Fact |
| fact_transactions | 32,778 | Fact |
| fact_performance | 40 | Fact |
| fact_aum | 90 | Fact |
| fact_portfolio | 322 | Fact |
| sip_inflows | 48 | Supplementary |
| category_inflows | 144 | Supplementary |
| folio_count | 21 | Supplementary |
| benchmark_indices | 8,050 | Supplementary |