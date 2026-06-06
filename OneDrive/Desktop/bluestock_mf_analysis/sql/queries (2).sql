-- ============================================================
-- queries.sql  (v2 — improved)
-- Bluestock Fintech – Mutual Fund Analysis Project
-- 10 Analytical SQL Queries
-- Run against: bluestock_mf.db
-- Improvement: SIP YoY growth now uses actual sip_inflows table
-- ============================================================


-- ── Query 1 : Top 5 Funds by AUM ─────────────────────────────
-- Which are the largest mutual fund schemes by AUM?
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.plan,
    p.aum_crore,
    p.expense_ratio_pct,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ── Query 2 : Average NAV per Month ──────────────────────────
-- How has the average NAV across all funds trended each month?
SELECT
    SUBSTR(date_id, 1, 7)       AS month,
    ROUND(AVG(nav), 2)          AS avg_nav,
    ROUND(MIN(nav), 2)          AS min_nav,
    ROUND(MAX(nav), 2)          AS max_nav,
    COUNT(DISTINCT amfi_code)   AS num_funds
FROM fact_nav
GROUP BY SUBSTR(date_id, 1, 7)
ORDER BY month;


-- ── Query 3 : SIP YoY Growth (from sip_inflows table) ────────
-- How are SIP inflows growing year over year?
-- Uses the actual sip_inflows table loaded from 04_monthly_sip_inflows_clean.csv
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    new_sip_accounts_lakh,
    ROUND(yoy_growth_pct, 2)        AS yoy_growth_pct,
    CASE
        WHEN yoy_growth_pct IS NULL THEN 'No prior year data'
        WHEN yoy_growth_pct > 20    THEN 'Strong growth'
        WHEN yoy_growth_pct > 10    THEN 'Moderate growth'
        WHEN yoy_growth_pct > 0     THEN 'Slow growth'
        ELSE 'Decline'
    END                             AS growth_category
FROM sip_inflows
ORDER BY month;


-- ── Query 4 : Transactions by State ──────────────────────────
-- Which states have the most mutual fund investors?
SELECT
    state,
    COUNT(*)                        AS total_transactions,
    SUM(amount_inr)                 AS total_amount_inr,
    ROUND(AVG(amount_inr), 0)       AS avg_amount_inr,
    COUNT(DISTINCT investor_id)     AS unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;


-- ── Query 5 : Funds with Expense Ratio < 1% ──────────────────
-- Which funds offer low-cost investing?
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


-- ── Query 6 : Funds Beating Their Benchmark (3-Year) ─────────
-- Which fund managers have genuinely outperformed?
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS outperformance_pct,
    p.sharpe_ratio,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct > p.benchmark_3yr_pct
ORDER BY outperformance_pct DESC;


-- ── Query 7 : Fund House AUM Ranking (latest quarter) ────────
-- Which AMCs manage the most assets right now?
SELECT
    fund_house,
    ROUND(aum_lakh_crore, 2)                        AS aum_lakh_crore,
    aum_crore,
    num_schemes,
    ROUND(aum_crore * 1.0 / num_schemes, 0)         AS avg_aum_per_scheme_crore
FROM fact_aum
WHERE date_id = (SELECT MAX(date_id) FROM fact_aum)
ORDER BY aum_crore DESC;


-- ── Query 8 : Investor Age Group Analysis ────────────────────
-- Which age groups invest the most?
SELECT
    age_group,
    COUNT(*)                            AS transactions,
    COUNT(DISTINCT investor_id)         AS unique_investors,
    SUM(amount_inr)                     AS total_invested_inr,
    ROUND(AVG(amount_inr), 0)           AS avg_investment_inr,
    ROUND(AVG(annual_income_lakh), 1)   AS avg_income_lakh
FROM fact_transactions
GROUP BY age_group
ORDER BY total_invested_inr DESC;


-- ── Query 9 : Top Sectors in Portfolio Holdings ───────────────
-- Which sectors are mutual funds most exposed to?
SELECT
    sector,
    COUNT(DISTINCT amfi_code)           AS num_funds_holding,
    ROUND(AVG(weight_pct), 2)           AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 1)      AS total_market_value_cr
FROM fact_portfolio
GROUP BY sector
ORDER BY total_market_value_cr DESC;


-- ── Query 10 : Risk-Adjusted Return (Best Direct Plans) ───────
-- Which direct plan funds give best return per unit of risk?
SELECT
    f.scheme_name,
    f.sub_category,
    p.return_5yr_pct,
    p.std_dev_ann_pct,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.max_drawdown_pct,
    p.risk_grade,
    ROUND(
        p.return_5yr_pct / NULLIF(p.std_dev_ann_pct, 0), 2
    )                                   AS return_per_unit_risk
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.plan = 'Direct'
ORDER BY return_per_unit_risk DESC;
