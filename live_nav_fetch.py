"""
live_nav_fetch.py
=================
Bluestock Fintech – Mutual Fund Analysis Project
Day 1: Fetch live NAV data from mfapi.in for key schemes and save as CSV.

Schemes fetched
---------------
125497  HDFC Top 100 Direct Plan
119551  SBI Bluechip Fund
120503  ICICI Prudential Bluechip Fund
118632  Nippon India Large Cap Fund
119092  Axis Bluechip Fund
120841  Kotak Bluechip Fund

API  :  GET https://api.mfapi.in/mf/{amfi_code}
Docs :  https://www.mfapi.in/

Author : Bluestock Intern
Date   : 2025-06-02
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
BASE_URL = "https://api.mfapi.in/mf"
RAW_DIR  = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

SCHEMES = {
    125497: "HDFC Top 100 Direct Plan",
    119551: "SBI Bluechip Fund",
    120503: "ICICI Prudential Bluechip Fund",
    118632: "Nippon India Large Cap Fund",
    119092: "Axis Bluechip Fund",
    120841: "Kotak Bluechip Fund",
}

SLEEP_BETWEEN_CALLS = 0.5   # seconds — be polite to the free API


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fetch_nav(amfi_code: int) -> dict:
    """
    Call mfapi.in for a single AMFI code.
    Returns parsed JSON dict with keys: 'meta' and 'data'.
    Raises on HTTP error.
    """
    url = f"{BASE_URL}/{amfi_code}"
    print(f"   GET {url} ...", end=" ")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()
    print(f"✅  ({len(payload.get('data', []))} NAV records)")
    return payload


def parse_nav_records(amfi_code: int, payload: dict) -> pd.DataFrame:
    """
    Flatten the JSON response into a tidy DataFrame.

    JSON structure (mfapi.in):
    {
        "meta": { "fund_house": ..., "scheme_type": ...,
                  "scheme_category": ..., "scheme_code": ...,
                  "scheme_name": ... },
        "data": [
            { "date": "02-06-2025", "nav": "342.1234" },
            ...
        ]
    }
    """
    meta = payload.get("meta", {})
    records = payload.get("data", [])

    df = pd.DataFrame(records)                          # date, nav columns
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["amfi_code"]   = amfi_code
    df["scheme_name"] = meta.get("scheme_name", "")
    df["fund_house"]  = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    # Reorder columns
    df = df[["amfi_code", "scheme_name", "fund_house",
             "scheme_type", "scheme_category", "date", "nav"]]
    df = df.sort_values("date").reset_index(drop=True)
    return df


def save_individual_csv(amfi_code: int, df: pd.DataFrame) -> str:
    """Save per-scheme CSV to data/raw/ and return the path."""
    filename = f"live_nav_{amfi_code}.csv"
    path = os.path.join(RAW_DIR, filename)
    df.to_csv(path, index=False)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "★" * 70)
    print("  BLUESTOCK FINTECH – LIVE NAV FETCH  (mfapi.in)")
    print("★" * 70)
    print(f"\n  Fetching {len(SCHEMES)} schemes …\n")

    all_dfs  = []
    failed   = []

    for amfi_code, friendly_name in SCHEMES.items():
        print(f"  [{amfi_code}] {friendly_name}")
        try:
            payload = fetch_nav(amfi_code)
            df      = parse_nav_records(amfi_code, payload)
            path    = save_individual_csv(amfi_code, df)

            # Print latest NAV
            latest = df.iloc[-1]
            print(f"         Latest NAV : ₹{latest['nav']:.4f}  on {latest['date'].date()}")
            print(f"         Records    : {len(df):,}  |  Saved → {path}")

            all_dfs.append(df)

        except requests.exceptions.RequestException as exc:
            print(f"         ❌ Network error: {exc}")
            failed.append(amfi_code)
        except Exception as exc:
            print(f"         ❌ Parse error: {exc}")
            failed.append(amfi_code)

        time.sleep(SLEEP_BETWEEN_CALLS)

    # ── Combine all into one master CSV ─────────────────────────────────────
    if all_dfs:
        combined      = pd.concat(all_dfs, ignore_index=True)
        combined_path = os.path.join(RAW_DIR, "live_nav_all_schemes.csv")
        combined.to_csv(combined_path, index=False)

        print("\n" + "─" * 70)
        print(f"  ✅ Combined CSV saved → {combined_path}")
        print(f"     Total rows : {len(combined):,}")
        print(f"     Schemes    : {combined['amfi_code'].nunique()}")
        print(f"     Date range : {combined['date'].min().date()} → {combined['date'].max().date()}")
    else:
        print("\n  ⚠️  No data was fetched — check network connectivity.")

    if failed:
        print(f"\n  ❌ Failed AMFI codes: {failed}")

    print("\n  Live NAV fetch complete.\n")
    return combined if all_dfs else pd.DataFrame()


if __name__ == "__main__":
    main()
