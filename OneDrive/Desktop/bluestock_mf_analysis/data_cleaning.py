"""
data_cleaning.py
================
Bluestock Fintech – Mutual Fund Analysis Project
Day 2: Clean all 10 datasets and save to data/processed/

What this script does
---------------------
1. nav_history       – parse dates, sort, forward-fill holidays, remove dupes, validate NAV > 0
2. investor_transactions – standardise types, validate amounts, fix dates, check KYC enum
3. scheme_performance    – validate numerics, flag anomalies, check expense_ratio range
4. All other 7 files     – date parsing, type fixes, basic validation

Author : Bluestock Intern
Date   : 2025-06-03
"""

import os
import pandas as pd
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(__file__)
RAW     = os.path.join(BASE, "data", "raw")
PROC    = os.path.join(BASE, "data", "processed")
os.makedirs(PROC, exist_ok=True)

# ── Helper ─────────────────────────────────────────────────────────────────
def section(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def save(df, filename):
    path = os.path.join(PROC, filename)
    df.to_csv(path, index=False)
    print(f"  ✅ Saved → data/processed/{filename}  ({len(df):,} rows)")
    return df

def load(filename):
    return pd.read_csv(os.path.join(RAW, filename))


# ══════════════════════════════════════════════════════════════════════════
# 1. NAV HISTORY
# ══════════════════════════════════════════════════════════════════════════
def clean_nav_history():
    section("1 · Cleaning nav_history")
    df = load("02_nav_history.csv")
    print(f"  Raw shape : {df.shape}")

    # Parse date
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    print(f"  Duplicates removed : {before - len(df)}")

    # Sort
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Forward-fill missing NAV for weekends / holidays per fund
    # First create a full date range per fund then ffill
    all_funds = df["amfi_code"].unique()
    date_min  = df["date"].min()
    date_max  = df["date"].max()
    full_dates = pd.date_range(date_min, date_max, freq="D")

    filled_frames = []
    for code in all_funds:
        fund_df = df[df["amfi_code"] == code].set_index("date")
        fund_df = fund_df.reindex(full_dates)
        fund_df["amfi_code"] = code
        fund_df["nav"] = fund_df["nav"].ffill()   # carry last known NAV forward
        fund_df = fund_df.dropna(subset=["nav"])  # drop leading NaNs before fund launched
        filled_frames.append(fund_df.reset_index().rename(columns={"index": "date"}))

    df = pd.concat(filled_frames, ignore_index=True)

    # Validate NAV > 0
    invalid = df[df["nav"] <= 0]
    if len(invalid):
        print(f"  ⚠️  Rows with NAV ≤ 0 removed : {len(invalid)}")
        df = df[df["nav"] > 0]
    else:
        print("  ✅ All NAV values > 0")

    # Final dtype tidy
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["nav"]       = df["nav"].round(4)
    df["date"]      = df["date"].dt.strftime("%Y-%m-%d")

    print(f"  Clean shape : {df.shape}")
    return save(df, "02_nav_history_clean.csv")


# ══════════════════════════════════════════════════════════════════════════
# 2. INVESTOR TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════
def clean_investor_transactions():
    section("2 · Cleaning investor_transactions")
    df = load("08_investor_transactions.csv")
    print(f"  Raw shape : {df.shape}")

    # Parse date
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")

    # Standardise transaction_type (strip spaces, title-case)
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    # Map variations to standard values
    type_map = {
        "Sip"        : "SIP",
        "Lumpsum"    : "Lumpsum",
        "Redemption" : "Redemption",
        "Redeem"     : "Redemption",
        "Lump Sum"   : "Lumpsum",
        "Lump-Sum"   : "Lumpsum",
    }
    df["transaction_type"] = df["transaction_type"].replace(type_map)
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    bad_types = df[~df["transaction_type"].isin(valid_types)]
    if len(bad_types):
        print(f"  ⚠️  Unknown transaction types found : {bad_types['transaction_type'].unique()}")
    else:
        print(f"  ✅ transaction_type values OK : {df['transaction_type'].unique().tolist()}")

    # Validate amount > 0
    invalid_amt = df[df["amount_inr"] <= 0]
    if len(invalid_amt):
        print(f"  ⚠️  Rows with amount ≤ 0 removed : {len(invalid_amt)}")
        df = df[df["amount_inr"] > 0]
    else:
        print(f"  ✅ All amounts > 0  (min = ₹{df['amount_inr'].min():,})")

    # Validate KYC status enum
    valid_kyc = {"Verified", "Pending"}
    bad_kyc = df[~df["kyc_status"].isin(valid_kyc)]
    if len(bad_kyc):
        print(f"  ⚠️  Unknown KYC values : {bad_kyc['kyc_status'].unique()}")
    else:
        print(f"  ✅ KYC status values OK : {df['kyc_status'].unique().tolist()}")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"  Duplicates removed : {before - len(df)}")

    # Format date back to string
    df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")

    print(f"  Clean shape : {df.shape}")
    return save(df, "08_investor_transactions_clean.csv")


# ══════════════════════════════════════════════════════════════════════════
# 3. SCHEME PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════
def clean_scheme_performance():
    section("3 · Cleaning scheme_performance")
    df = load("07_scheme_performance.csv")
    print(f"  Raw shape : {df.shape}")

    # Validate all return columns are numeric
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        nulls = df[col].isnull().sum()
        if nulls:
            print(f"  ⚠️  {col} has {nulls} non-numeric values → set to NaN")
        else:
            print(f"  ✅ {col} : all numeric  (range {df[col].min():.2f}% to {df[col].max():.2f}%)")

    # Flag anomalies — returns outside -50% to +100% are suspicious
    for col in return_cols:
        anomalies = df[(df[col] < -50) | (df[col] > 100)]
        if len(anomalies):
            print(f"  ⚠️  Anomaly in {col} : {len(anomalies)} rows outside [-50%, +100%]")
            df[col + "_anomaly_flag"] = ((df[col] < -50) | (df[col] > 100)).astype(int)

    # Validate expense_ratio range 0.1% – 2.5%
    out_of_range = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    if len(out_of_range):
        print(f"  ⚠️  expense_ratio out of range (0.1–2.5%) : {len(out_of_range)} rows")
        print(out_of_range[["scheme_name", "expense_ratio_pct"]])
    else:
        print(f"  ✅ expense_ratio range OK  ({df['expense_ratio_pct'].min()}% – {df['expense_ratio_pct'].max()}%)")

    # Validate other numeric columns
    numeric_cols = ["alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code"])
    print(f"  Duplicates removed : {before - len(df)}")

    print(f"  Clean shape : {df.shape}")
    return save(df, "07_scheme_performance_clean.csv")


# ══════════════════════════════════════════════════════════════════════════
# 4–10. REMAINING DATASETS
# ══════════════════════════════════════════════════════════════════════════
def clean_fund_master():
    section("4 · Cleaning fund_master")
    df = load("01_fund_master.csv")
    df["launch_date"]     = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"]   = pd.to_numeric(df["exit_load_pct"], errors="coerce")
    df = df.drop_duplicates(subset=["amfi_code"])
    print(f"  Clean shape : {df.shape}")
    return save(df, "01_fund_master_clean.csv")


def clean_aum():
    section("5 · Cleaning aum_by_fund_house")
    df = load("03_aum_by_fund_house.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["aum_lakh_crore"] = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    df["aum_crore"]      = pd.to_numeric(df["aum_crore"], errors="coerce")
    df = df.drop_duplicates()
    print(f"  Clean shape : {df.shape}")
    return save(df, "03_aum_by_fund_house_clean.csv")


def clean_sip():
    section("6 · Cleaning monthly_sip_inflows")
    df = load("04_monthly_sip_inflows.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce").dt.strftime("%Y-%m")
    # yoy_growth_pct nulls for first 12 months are expected — keep them
    print(f"  yoy_growth_pct nulls : {df['yoy_growth_pct'].isnull().sum()} (expected — first year)")
    df = df.drop_duplicates()
    print(f"  Clean shape : {df.shape}")
    return save(df, "04_monthly_sip_inflows_clean.csv")


def clean_category_inflows():
    section("7 · Cleaning category_inflows")
    df = load("05_category_inflows.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce").dt.strftime("%Y-%m")
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    df = df.drop_duplicates()
    print(f"  Clean shape : {df.shape}")
    return save(df, "05_category_inflows_clean.csv")


def clean_folio():
    section("8 · Cleaning industry_folio_count")
    df = load("06_industry_folio_count.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce").dt.strftime("%Y-%m")
    df = df.drop_duplicates()
    print(f"  Clean shape : {df.shape}")
    return save(df, "06_industry_folio_count_clean.csv")


def clean_portfolio():
    section("9 · Cleaning portfolio_holdings")
    df = load("09_portfolio_holdings.csv")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["weight_pct"]     = pd.to_numeric(df["weight_pct"], errors="coerce")
    df["market_value_cr"]= pd.to_numeric(df["market_value_cr"], errors="coerce")
    df = df.drop_duplicates()
    print(f"  Clean shape : {df.shape}")
    return save(df, "09_portfolio_holdings_clean.csv")


def clean_benchmark():
    section("10 · Cleaning benchmark_indices")
    df = load("10_benchmark_indices.csv")
    df["date"]        = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df.drop_duplicates(subset=["date", "index_name"])
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    print(f"  Clean shape : {df.shape}")
    return save(df, "10_benchmark_indices_clean.csv")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    print("\n" + "★" * 65)
    print("  BLUESTOCK FINTECH – DATA CLEANING  (Day 2)")
    print("★" * 65)

    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_fund_master()
    clean_aum()
    clean_sip()
    clean_category_inflows()
    clean_folio()
    clean_portfolio()
    clean_benchmark()

    print("\n" + "─" * 65)
    print("  ✅ All 10 datasets cleaned and saved to data/processed/")
    print("─" * 65 + "\n")


if __name__ == "__main__":
    main()
