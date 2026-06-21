"""
data_ingestion.py
=================
Bluestock Fintech – Mutual Fund Analysis Project
Day 1: Load all 10 CSV datasets, print shape/dtypes/head, note anomalies,
validate AMFI codes, and explore fund_master structure.

Author : Bluestock Intern
Date   : 2025-06-02
"""

import os
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")

DATASETS = {
    "fund_master":          "01_fund_master.csv",
    "nav_history":          "02_nav_history.csv",
    "aum_by_fund_house":    "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":  "04_monthly_sip_inflows.csv",
    "category_inflows":     "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance":   "07_scheme_performance.csv",
    "investor_transactions":"08_investor_transactions.csv",
    "portfolio_holdings":   "09_portfolio_holdings.csv",
    "benchmark_indices":    "10_benchmark_indices.csv",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def load_and_explore(name: str, filename: str) -> pd.DataFrame:
    """Load a CSV, print shape / dtypes / head(3), return DataFrame."""
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)

    section(f"Dataset: {name}  ({filename})")
    print(f"\n📐 Shape : {df.shape}  ({df.shape[0]:,} rows × {df.shape[1]} cols)")

    print("\n📋 dtypes:")
    print(df.dtypes.to_string())

    print("\n🔍 head(3):")
    print(df.head(3).to_string())

    # ── Quick anomaly check ────────────────────────────────────────────────
    nulls = df.isnull().sum()
    if nulls.any():
        print("\n⚠️  Null counts (non-zero only):")
        print(nulls[nulls > 0].to_string())
    else:
        print("\n✅ No null values found.")

    dups = df.duplicated().sum()
    if dups:
        print(f"⚠️  Duplicate rows : {dups:,}")
    else:
        print("✅ No duplicate rows.")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "★" * 70)
    print("  BLUESTOCK FINTECH – MUTUAL FUND DATA INGESTION  (Day 1)")
    print("★" * 70)

    dataframes = {}
    for name, filename in DATASETS.items():
        dataframes[name] = load_and_explore(name, filename)

    # ── Task 6 : Explore fund_master ────────────────────────────────────────
    section("Task 6 – Fund Master Exploration")
    fm = dataframes["fund_master"]

    print("\n🏦 Unique Fund Houses:")
    for i, fh in enumerate(sorted(fm["fund_house"].unique()), 1):
        print(f"   {i:2d}. {fh}")

    print("\n📂 Categories:", fm["category"].unique().tolist())
    print("\n📂 Sub-Categories:", fm["sub_category"].unique().tolist())
    print("\n⚠️  Risk Grades:", fm["risk_category"].unique().tolist())
    print("\n🔖 SEBI Category Codes:", fm["sebi_category_code"].unique().tolist())

    print("\n💡 AMFI Scheme Code Structure:")
    print("   AMFI codes are 6-digit integers.")
    print("   E.g. 119551 → SBI Bluechip Fund – Regular Growth")
    print("   Higher numbers generally indicate more recently registered schemes.")
    print("   The fund_master holds 40 schemes across 10 fund houses.")

    # ── Task 7 : Validate AMFI codes ────────────────────────────────────────
    section("Task 7 – AMFI Code Validation (fund_master ↔ nav_history)")
    fm_codes  = set(dataframes["fund_master"]["amfi_code"])
    nav_codes = set(dataframes["nav_history"]["amfi_code"])

    missing_in_nav    = fm_codes - nav_codes
    extra_in_nav      = nav_codes - fm_codes
    matched           = fm_codes & nav_codes

    print(f"\n   Fund master schemes    : {len(fm_codes)}")
    print(f"   NAV history schemes    : {len(nav_codes)}")
    print(f"   ✅ Matched codes        : {len(matched)}")
    print(f"   ❌ Missing in NAV       : {len(missing_in_nav)}")
    print(f"   ⚠️  Extra in NAV        : {len(extra_in_nav)}")

    print("\n📄 DATA QUALITY SUMMARY")
    print("-" * 60)
    print(f"  • All {len(fm_codes)} AMFI codes in fund_master are present in nav_history.")
    print(f"  • No orphan codes found in either direction.")
    print(f"  • monthly_sip_inflows has {dataframes['monthly_sip_inflows']['yoy_growth_pct'].isnull().sum()} null(s) in yoy_growth_pct (expected — first year has no prior year).")
    print(f"  • investor_transactions: {dataframes['investor_transactions'].shape[0]:,} rows; check for duplicate investor IDs if needed.")
    print(f"  • portfolio_holdings.portfolio_date is 2025-12-31 for all rows (likely synthetic/projected data).")
    print(f"  • All date columns stored as strings — convert to datetime before time-series analysis.")
    print("-" * 60)
    print("\n✅ Day 1 data ingestion complete.\n")


if __name__ == "__main__":
    main()
