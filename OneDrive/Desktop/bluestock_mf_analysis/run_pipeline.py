"""
run_pipeline.py
===============
Bluestock Fintech – Mutual Fund Analysis Project
Master execution script — runs the full ETL pipeline in order.

Steps:
    1. Data ingestion  — loads all 10 CSVs, prints shape/dtypes/head
    2. Live NAV fetch  — fetches current NAV from mfapi.in for 6 schemes
    3. Data cleaning   — cleans all 10 datasets, saves to data/processed/
    4. Database load   — loads all cleaned data into SQLite via SQLAlchemy

Usage:
    python run_pipeline.py

Author : Bluestock Intern
Date   : 2025-06-07
"""

import os
import sys
import time
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))


def section(title: str) -> None:
    """Print a clearly visible section header."""
    print("\n" + "=" * 62)
    print(f"  {title}")
    print("=" * 62)


def run_script(script_name: str) -> bool:
    """
    Dynamically import and execute a Python script's main() function.

    Parameters
    ----------
    script_name : str
        Filename of the script to run (e.g. 'data_cleaning.py')

    Returns
    -------
    bool
        True if the script ran without errors, False otherwise.
    """
    path = os.path.join(BASE, script_name)

    if not os.path.exists(path):
        print(f"  WARNING: {script_name} not found — skipping")
        return False

    try:
        spec   = importlib.util.spec_from_file_location("module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            module.main()
        return True
    except Exception as exc:
        print(f"  ERROR running {script_name}: {exc}")
        return False


def check_prerequisites() -> bool:
    """
    Verify that the required raw CSV files exist before running the pipeline.

    Returns
    -------
    bool
        True if all required files are present, False otherwise.
    """
    raw_dir  = os.path.join(BASE, "data", "raw")
    required = [
        "01_fund_master.csv",
        "02_nav_history.csv",
        "08_investor_transactions.csv",
    ]
    missing = [f for f in required if not os.path.exists(os.path.join(raw_dir, f))]

    if missing:
        print("\n  ERROR: The following raw data files are missing from data/raw/:")
        for f in missing:
            print(f"    - {f}")
        print("\n  Please place all 10 CSV files in data/raw/ before running.")
        return False

    return True


def main() -> None:
    """Run the full Bluestock MF analytics ETL pipeline."""
    start = time.time()

    print("\n" + "★" * 62)
    print("  BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS PIPELINE")
    print("  Master Execution Script  |  run_pipeline.py")
    print("★" * 62)
    print(f"\n  Project root : {BASE}")

    if not check_prerequisites():
        sys.exit(1)

    results = {}

    # ── Step 1 ─────────────────────────────────────────────────
    section("Step 1 of 4 — Data Ingestion")
    results["data_ingestion"] = run_script("data_ingestion.py")

    # ── Step 2 ─────────────────────────────────────────────────
    section("Step 2 of 4 — Live NAV Fetch (mfapi.in)")
    print("  Note: This step requires an active internet connection.")
    results["live_nav_fetch"] = run_script("live_nav_fetch.py")

    # ── Step 3 ─────────────────────────────────────────────────
    section("Step 3 of 4 — Data Cleaning")
    results["data_cleaning"] = run_script("data_cleaning.py")

    # ── Step 4 ─────────────────────────────────────────────────
    section("Step 4 of 4 — SQLite Database Load")
    results["db_loader"] = run_script("db_loader.py")

    # ── Summary ────────────────────────────────────────────────
    elapsed = time.time() - start
    section("Pipeline Summary")

    all_ok = all(results.values())
    for step, ok in results.items():
        icon = "OK  " if ok else "FAIL"
        print(f"  [{icon}] {step}")

    print(f"\n  Total time : {elapsed:.1f} seconds")
    if all_ok:
        print("  Status     : All steps completed successfully")
    else:
        print("  Status     : Some steps failed — check errors above")

    print()
    print("  What to do next:")
    print("    Open notebooks : jupyter notebook")
    print("    Fund recommender: python recommender.py")
    print("    Dashboard       : Open dashboard/bluestock_mf_dashboard.pbix in Power BI")
    print()


if __name__ == "__main__":
    main()
