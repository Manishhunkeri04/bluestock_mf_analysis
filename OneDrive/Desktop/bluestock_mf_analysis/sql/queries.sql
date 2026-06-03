-- ============================================================
-- queries.sql
-- Bluestock Fintech – Mutual Fund Analysis Project
-- 10 Analytical SQL Queries – Day 2
-- Run against: bluestock_mf.db
-- ============================================================


-- ── Query 1 : Top 5 Funds by AUM ─────────────────────────────
-- Business question: Which are the largest mutual fund schemes
-- by Assets Under Management?
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    p.aum_crore,
    ROUND(p.expense_ratio_pct, 2)   AS expense_ratio_pct,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ── Query 2 : Average NAV per Month (all funds combined) ─────
-- Business question: How has the average NAV across all funds
-- trended month by month?
SELECT
    SUBSTR(date_id, 1, 7)       AS month,
    ROUND(AVG(nav), 2)          AS avg_nav,
    ROUND(MIN(nav), 2)          AS min_nav,
    ROUND(MAX(nav), 2)          AS max_nav,
    COUNT(DISTINCT amfi_code)   AS num_funds
FROM fact_nav
GROUP BY SUBSTR(date_id, 1, 7)
ORDER BY month;


-- ── Query 3 : SIP YoY Growth ─────────────────────────────────
-- Business question: How fast are SIP inflows growing year over year?
-- Uses: monthly_sip_inflows (loaded as a view via pandas if needed)
-- Note: This query reads from fact_nav as a proxy; for direct SIP data
-- load 04_monthly_sip_inflows_clean.csv into a sip_inflows table.
-- Shown here as a template with actual column names:
/*
SELECT
    month,
    sip_inflow_crore,
    ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM sip_inflows
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month;
*/
-- Working version using fact_transactions (SIP type):
SELECT
    SUBSTR(transaction_date, 1, 7)  AS month,
    COUNT(*)                         AS sip_count,
    SUM(amount_inr)                  AS total_sip_amount,
    ROUND(AVG(amount_inr), 0)        AS avg_sip_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY SUBSTR(transaction_date, 1, 7)
ORDER BY month;


-- ── Query 4 : Transactions by State ──────────────────────────
-- Business question: Which states have the most mutual fund investors?
SELECT
    state,
    COUNT(*)                            AS total_transactions,
    SUM(amount_inr)                     AS total_amount,
    ROUND(AVG(amount_inr), 0)           AS avg_amount,
    COUNT(DISTINCT investor_id)         AS unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;


-- ── Query 5 : Funds with Expense Ratio < 1% ──────────────────
-- Business question: Which funds offer low-cost investing (expense < 1%)?
SELECT
    f.scheme_name,
    f.fund_house,
    f.plan,
    f.sub_category,
    p.expense_ratio_pct,
    p.return_3yr_pct,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;


-- ── Query 6 : Best Performing Funds (3-Year Return) ──────────
-- Business question: Which funds have beaten their benchmark
-- over 3 years?
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2)   AS alpha_over_benchmark,
    p.sharpe_ratio,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct > p.benchmark_3yr_pct
ORDER BY alpha_over_benchmark DESC;


-- ── Query 7 : Fund House AUM Ranking (latest quarter) ────────
-- Business question: Which fund houses manage the most assets?
SELECT
    fund_house,
    ROUND(aum_lakh_crore, 2)    AS aum_lakh_crore,
    aum_crore,
    num_schemes,
    ROUND(aum_crore * 1.0 / num_schemes, 0) AS avg_aum_per_scheme
FROM fact_aum
WHERE date_id = (SELECT MAX(date_id) FROM fact_aum)
ORDER BY aum_crore DESC;


-- ── Query 8 : Investor Demographics – Age Group Analysis ─────
-- Business question: Which age groups invest the most in mutual funds?
SELECT
    age_group,
    COUNT(*)                        AS transactions,
    COUNT(DISTINCT investor_id)     AS unique_investors,
    SUM(amount_inr)                 AS total_invested,
    ROUND(AVG(amount_inr), 0)       AS avg_investment,
    ROUND(AVG(annual_income_lakh),1) AS avg_income_lakh
FROM fact_transactions
GROUP BY age_group
ORDER BY total_invested DESC;


-- ── Query 9 : Top Sectors in Portfolio Holdings ───────────────
-- Business question: What sectors are mutual funds most exposed to?
SELECT
    sector,
    COUNT(DISTINCT amfi_code)       AS num_funds_holding,
    ROUND(AVG(weight_pct), 2)       AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 1)  AS total_market_value_cr
FROM fact_portfolio
GROUP BY sector
ORDER BY total_market_value_cr DESC;


-- ── Query 10 : Risk vs Return Analysis ───────────────────────
-- Business question: Which funds offer the best risk-adjusted returns?
-- (High return, low std deviation = efficient fund)
SELECT
    f.scheme_name,
    f.sub_category,
    p.return_5yr_pct,
    p.std_dev_ann_pct,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.max_drawdown_pct,
    p.risk_grade,
    ROUND(p.return_5yr_pct / NULLIF(p.std_dev_ann_pct, 0), 2) AS return_per_unit_risk
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.plan = 'Direct'
ORDER BY return_per_unit_risk DESC;
