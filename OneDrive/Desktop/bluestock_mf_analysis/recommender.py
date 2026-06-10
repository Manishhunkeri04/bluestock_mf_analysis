"""
recommender.py
==============
Bluestock Fintech – Mutual Fund Analysis Project
Day 6: Simple Fund Recommender based on investor risk appetite

Usage:
    python recommender.py

Author : Bluestock Intern
Date   : 2025-06-06
"""

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(BASE, "data", "processed")

# Load data — perf_df already has scheme_name, fund_house, plan
perf_df = pd.read_csv(os.path.join(PROC, "07_scheme_performance_clean.csv"))
fund_df = pd.read_csv(os.path.join(PROC, "01_fund_master_clean.csv"))

# Add sub_category from fund_df (only column missing in perf_df)
perf_df = perf_df.merge(
    fund_df[["amfi_code","sub_category"]], on="amfi_code", how="left"
)

RISK_MAP = {
    "low"      : ["Low"],
    "moderate" : ["Moderate", "Moderately High"],
    "high"     : ["High", "Very High"],
}

def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    key = risk_appetite.strip().lower()
    if key not in RISK_MAP:
        print(f"\n  Invalid input. Please choose: Low / Moderate / High\n")
        return pd.DataFrame()

    grades   = RISK_MAP[key]
    filtered = perf_df[perf_df["risk_grade"].isin(grades)].copy()

    top = (filtered
           .sort_values("sharpe_ratio", ascending=False)
           .head(top_n)
           [["scheme_name","fund_house","plan","sub_category",
             "sharpe_ratio","return_3yr_pct","return_5yr_pct",
             "expense_ratio_pct","risk_grade","morningstar_rating"]]
           .reset_index(drop=True))
    return top

def print_recommendation(risk_appetite: str) -> None:
    print("\n" + "=" * 70)
    print(f"  FUND RECOMMENDATIONS FOR: {risk_appetite.upper()} RISK INVESTOR")
    print("=" * 70)

    result = recommend(risk_appetite)
    if result.empty:
        return

    for i, row in result.iterrows():
        print(f"\n  #{i+1} — {row['scheme_name']}")
        print(f"       Fund House  : {row['fund_house']}")
        print(f"       Category    : {row['sub_category']} | {row['plan']} Plan")
        print(f"       Sharpe Ratio: {row['sharpe_ratio']:.2f}")
        print(f"       3-Yr Return : {row['return_3yr_pct']:.2f}%")
        print(f"       5-Yr Return : {row['return_5yr_pct']:.2f}%")
        print(f"       Expense     : {row['expense_ratio_pct']:.2f}%")
        print(f"       Risk Grade  : {row['risk_grade']}")
        print(f"       Stars       : {'★' * int(row['morningstar_rating'])}")

    print("\n" + "-" * 70)
    print("  Note: Based on historical data. Past performance is not a guarantee.")
    print("-" * 70 + "\n")

if __name__ == "__main__":
    print("\n" + "★" * 70)
    print("  BLUESTOCK FINTECH — MUTUAL FUND RECOMMENDER")
    print("★" * 70)

    for appetite in ["Low", "Moderate", "High"]:
        print_recommendation(appetite)
