-- ============================================================
-- schema.sql
-- Bluestock Fintech – Mutual Fund Analysis Project
-- SQLite Star Schema – Day 2
-- ============================================================

-- ── DIMENSION : Fund ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT    NOT NULL,
    scheme_name         TEXT    NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- ── DIMENSION : Date ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    week        INTEGER,
    day         INTEGER,
    day_name    TEXT,
    is_weekend  INTEGER             -- 0 or 1
);

-- ── FACT : NAV History ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER NOT NULL,
    date_id     TEXT    NOT NULL,
    nav         REAL    NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date (date_id)
);

-- ── FACT : Investor Transactions ─────────────────────────────
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    transaction_date    TEXT    NOT NULL,
    amfi_code           INTEGER NOT NULL,
    transaction_type    TEXT,
    amount_inr          INTEGER,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

-- ── FACT : Scheme Performance ────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

-- ── FACT : AUM by Fund House ─────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id         TEXT    NOT NULL,
    fund_house      TEXT    NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    FOREIGN KEY (date_id) REFERENCES dim_date (date_id)
);

-- ── FACT : Portfolio Holdings ────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_portfolio (
    holding_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    stock_symbol        TEXT,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

-- ── INDEXES for query performance ────────────────────────────
CREATE INDEX IF NOT EXISTS idx_nav_amfi    ON fact_nav (amfi_code);
CREATE INDEX IF NOT EXISTS idx_nav_date    ON fact_nav (date_id);
CREATE INDEX IF NOT EXISTS idx_txn_amfi    ON fact_transactions (amfi_code);
CREATE INDEX IF NOT EXISTS idx_txn_date    ON fact_transactions (transaction_date);
CREATE INDEX IF NOT EXISTS idx_txn_state   ON fact_transactions (state);
CREATE INDEX IF NOT EXISTS idx_perf_amfi   ON fact_performance (amfi_code);
CREATE INDEX IF NOT EXISTS idx_aum_date    ON fact_aum (date_id);
