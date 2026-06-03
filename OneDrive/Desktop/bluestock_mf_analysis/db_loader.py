"""
db_loader.py
============
Bluestock Fintech – Mutual Fund Analysis Project
Day 2: Load cleaned CSVs into SQLite star schema

Uses Python's built-in sqlite3 + pandas (no extra install needed)
SQLAlchemy is used if available, falls back to sqlite3 automatically.

Author : Bluestock Intern
Date   : 2025-06-03
"""

import os
import sqlite3
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(BASE, "data", "processed")
DB   = os.path.join(BASE, "bluestock_mf.db")
SQL  = os.path.join(BASE, "sql", "schema.sql")

def section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def load_csv(filename):
    return pd.read_csv(os.path.join(PROC, filename))

def get_connection():
    return sqlite3.connect(DB)

def verify(conn, table, expected):
    actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    status = "✅" if actual == expected else "⚠️ "
    print(f"  {status} {table:30s}  expected={expected:>7,}  actual={actual:>7,}")

# ══════════════════════════════════════════════════════════════
# 1. SCHEMA
# ══════════════════════════════════════════════════════════════
def create_schema(conn):
    section("Creating SQLite Schema")
    with open(SQL) as f:
        schema = f.read()
    for stmt in schema.split(";"):
        s = stmt.strip()
        if s:
            try:
                conn.execute(s)
            except Exception as e:
                print(f"  ⚠️  {e}")
    conn.commit()
    print("  ✅ Schema created")

# ══════════════════════════════════════════════════════════════
# 2. DIM DATE
# ══════════════════════════════════════════════════════════════
def load_dim_date(conn):
    section("Building & Loading dim_date")
    nav   = load_csv("02_nav_history_clean.csv")
    dates = pd.to_datetime(nav["date"].unique())
    dim   = pd.DataFrame({"date_id": dates})
    dim["year"]       = dim["date_id"].dt.year
    dim["quarter"]    = dim["date_id"].dt.quarter
    dim["month"]      = dim["date_id"].dt.month
    dim["month_name"] = dim["date_id"].dt.strftime("%B")
    dim["week"]       = dim["date_id"].dt.isocalendar().week.astype(int)
    dim["day"]        = dim["date_id"].dt.day
    dim["day_name"]   = dim["date_id"].dt.strftime("%A")
    dim["is_weekend"] = dim["date_id"].dt.dayofweek.isin([5, 6]).astype(int)
    dim["date_id"]    = dim["date_id"].dt.strftime("%Y-%m-%d")
    dim = dim.drop_duplicates("date_id").sort_values("date_id").reset_index(drop=True)
    dim.to_sql("dim_date", conn, if_exists="replace", index=False)
    print(f"  ✅ dim_date  ({len(dim):,} rows)")

# ══════════════════════════════════════════════════════════════
# 3. ALL FACT + DIM TABLES
# ══════════════════════════════════════════════════════════════
def load_all(conn):
    section("Loading dim_fund")
    df = load_csv("01_fund_master_clean.csv")
    df.to_sql("dim_fund", conn, if_exists="replace", index=False)
    print(f"  ✅ dim_fund  ({len(df):,} rows)")

    section("Loading fact_nav")
    df = load_csv("02_nav_history_clean.csv").rename(columns={"date": "date_id"})
    df.to_sql("fact_nav", conn, if_exists="replace", index=False)
    print(f"  ✅ fact_nav  ({len(df):,} rows)")

    section("Loading fact_transactions")
    df = load_csv("08_investor_transactions_clean.csv")
    df.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    print(f"  ✅ fact_transactions  ({len(df):,} rows)")

    section("Loading fact_performance")
    df = load_csv("07_scheme_performance_clean.csv")
    cols = ["amfi_code","return_1yr_pct","return_3yr_pct","return_5yr_pct",
            "benchmark_3yr_pct","alpha","beta","sharpe_ratio","sortino_ratio",
            "std_dev_ann_pct","max_drawdown_pct","aum_crore","expense_ratio_pct",
            "morningstar_rating","risk_grade"]
    df[cols].to_sql("fact_performance", conn, if_exists="replace", index=False)
    print(f"  ✅ fact_performance  ({len(df):,} rows)")

    section("Loading fact_aum")
    df = load_csv("03_aum_by_fund_house_clean.csv").rename(columns={"date": "date_id"})
    df.to_sql("fact_aum", conn, if_exists="replace", index=False)
    print(f"  ✅ fact_aum  ({len(df):,} rows)")

    section("Loading fact_portfolio")
    df = load_csv("09_portfolio_holdings_clean.csv")
    df.to_sql("fact_portfolio", conn, if_exists="replace", index=False)
    print(f"  ✅ fact_portfolio  ({len(df):,} rows)")

# ══════════════════════════════════════════════════════════════
# 4. VERIFY
# ══════════════════════════════════════════════════════════════
def verify_all(conn):
    section("Row Count Verification")
    verify(conn, "dim_fund",          40)
    verify(conn, "dim_date",          1608)
    verify(conn, "fact_nav",          64320)
    verify(conn, "fact_transactions", 32778)
    verify(conn, "fact_performance",  40)
    verify(conn, "fact_aum",          90)
    verify(conn, "fact_portfolio",    322)

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    print("\n" + "★" * 60)
    print("  BLUESTOCK FINTECH – SQLite DB LOADER  (Day 2)")
    print("★" * 60)

    conn = get_connection()
    create_schema(conn)
    load_dim_date(conn)
    load_all(conn)
    verify_all(conn)
    conn.close()

    print("\n" + "─" * 60)
    print(f"  ✅ Database ready → bluestock_mf.db")
    print("─" * 60 + "\n")

if __name__ == "__main__":
    main()
