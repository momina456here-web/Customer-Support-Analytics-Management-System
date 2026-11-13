"""Command-line entry point."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .validation import validate_tickets
from .database import save_tickets
from .analytics import build_reports

def run(input_path: str, db_path: str, output_dir: str) -> int:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")
    raw = pd.read_csv(source)
    clean, rejected = validate_tickets(raw)
    if clean.empty:
        print("No valid ticket rows found. Check the input CSV.")
        return 1

    save_tickets(clean, db_path)
    kpis = build_reports(clean, output_dir)
    rejected_path = Path(output_dir) / "rejected_rows.csv"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    if not rejected.empty:
        rejected.to_csv(rejected_path, index=False)

    print("\nCUSTOMER SUPPORT ANALYTICS")
    print("=" * 32)
    for key, value in kpis.items():
        print(f"{key.replace('_', ' ').title():32} {value}")
    print(f"\nValid rows stored: {len(clean)}")
    print(f"Rejected rows: {len(rejected)}")
    print(f"Database: {db_path}")
    print(f"Reports: {output_dir}")
    return 0

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze customer-support ticket operations.")
    parser.add_argument("--input", default="data/sample_tickets.csv", help="Path to source CSV")
    parser.add_argument("--db", default="support_tickets.db", help="SQLite database path")
    parser.add_argument("--output", default="reports", help="Report output directory")
    args = parser.parse_args()
    raise SystemExit(run(args.input, args.db, args.output))

if __name__ == "__main__":
    main()
