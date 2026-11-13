"""Operational KPI calculations and report generation."""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def add_sla_flag(frame: pd.DataFrame, as_of: pd.Timestamp | None = None) -> pd.DataFrame:
    data = frame.copy()
    created = pd.to_datetime(data["created_at"])
    resolved = data["resolution_hours"].notna()
    age_hours = ((as_of or pd.Timestamp.now()) - created).dt.total_seconds() / 3600
    elapsed = data["resolution_hours"].where(resolved, age_hours)
    data["sla_breached"] = elapsed > data["sla_hours"]
    return data

def calculate_kpis(frame: pd.DataFrame) -> dict:
    total = int(len(frame))
    resolved = frame[frame["status"].eq("Resolved")]
    scores = frame["csat_score"].dropna()
    return {
        "total_tickets": total,
        "resolved_tickets": int(len(resolved)),
        "open_or_pending_tickets": int(total - len(resolved)),
        "resolution_rate_pct": round(len(resolved) / total * 100, 2) if total else 0.0,
        "average_first_response_hours": round(frame["first_response_hours"].mean(), 2) if total else None,
        "average_resolution_hours": round(resolved["resolution_hours"].mean(), 2) if len(resolved) else None,
        "average_csat": round(scores.mean(), 2) if len(scores) else None,
    }

def build_reports(frame: pd.DataFrame, output_dir: str) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = add_sla_flag(frame)
    kpis = calculate_kpis(data)

    (out / "kpi_summary.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    data.groupby("priority", dropna=False).agg(
        ticket_count=("ticket_id", "count"),
        sla_breaches=("sla_breached", "sum")
    ).reset_index().to_csv(out / "priority_breakdown.csv", index=False)

    category = data.groupby("category", dropna=False).agg(
        ticket_count=("ticket_id", "count"),
        avg_resolution_hours=("resolution_hours", "mean"),
        sla_breaches=("sla_breached", "sum"),
        avg_csat=("csat_score", "mean")
    ).reset_index()
    category.to_csv(out / "category_performance.csv", index=False)

    agent = data.groupby("agent", dropna=False).agg(
        tickets_handled=("ticket_id", "count"),
        resolved_tickets=("status", lambda s: int(s.eq("Resolved").sum())),
        avg_first_response_hours=("first_response_hours", "mean"),
        avg_csat=("csat_score", "mean")
    ).reset_index()
    agent.to_csv(out / "agent_performance.csv", index=False)

    monthly = data.assign(month=pd.to_datetime(data["created_at"]).dt.to_period("M").astype(str))
    monthly.groupby("month").agg(
        ticket_count=("ticket_id", "count"),
        resolved_tickets=("status", lambda s: int(s.eq("Resolved").sum()))
    ).reset_index().to_csv(out / "monthly_trend.csv", index=False)

    data.loc[data["sla_breached"]].to_csv(out / "sla_breaches.csv", index=False)

    if not monthly.empty:
        trend = monthly.groupby("month").size()
        plt.figure(figsize=(9, 4.5))
        trend.plot(kind="line", marker="o")
        plt.title("Monthly Support Ticket Volume")
        plt.xlabel("Month")
        plt.ylabel("Tickets")
        plt.grid(True, alpha=0.25)
        plt.tight_layout()
        plt.savefig(out / "monthly_ticket_volume.png", dpi=160)
        plt.close()

    if not category.empty:
        plot_data = category.sort_values("avg_resolution_hours", ascending=False)
        plt.figure(figsize=(9, 4.5))
        plt.bar(plot_data["category"], plot_data["avg_resolution_hours"])
        plt.title("Average Resolution Time by Category")
        plt.xlabel("Category")
        plt.ylabel("Hours")
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(out / "category_resolution_time.png", dpi=160)
        plt.close()

    return kpis
