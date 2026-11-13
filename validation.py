"""Input validation and cleaning for support-ticket records."""
from __future__ import annotations
import pandas as pd

REQUIRED_COLUMNS = {
    "ticket_id", "created_at", "first_response_hours", "resolution_hours",
    "status", "priority", "category", "agent", "customer_region",
    "csat_score", "sla_hours",
}
VALID_STATUSES = {"Open", "Pending", "Resolved"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}

def validate_tickets(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean_rows, rejected_rows_with_reason)."""
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    data = frame.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    numeric = ["first_response_hours", "resolution_hours", "csat_score", "sla_hours"]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    reasons = pd.Series("", index=data.index, dtype="object")
    checks = [
        (data["ticket_id"].isna() | data["ticket_id"].astype(str).str.strip().eq(""), "missing ticket_id"),
        (data["created_at"].isna(), "invalid created_at"),
        (~data["status"].isin(VALID_STATUSES), "invalid status"),
        (~data["priority"].isin(VALID_PRIORITIES), "invalid priority"),
        (data["first_response_hours"].isna() | (data["first_response_hours"] < 0), "invalid first_response_hours"),
        (data["sla_hours"].isna() | (data["sla_hours"] <= 0), "invalid sla_hours"),
        (data["csat_score"].notna() & ~data["csat_score"].between(1, 5), "csat_score must be 1-5"),
        (data["resolution_hours"].notna() & (data["resolution_hours"] < 0), "negative resolution_hours"),
    ]
    for condition, message in checks:
        reasons.loc[condition] = reasons.loc[condition].where(reasons.loc[condition].eq(""), reasons.loc[condition] + "; ")
        reasons.loc[condition] += message

    # A resolved ticket must have a resolution duration.
    bad_resolved = data["status"].eq("Resolved") & data["resolution_hours"].isna()
    reasons.loc[bad_resolved] = reasons.loc[bad_resolved].where(reasons.loc[bad_resolved].eq(""), reasons.loc[bad_resolved] + "; ")
    reasons.loc[bad_resolved] += "resolved ticket missing resolution_hours"

    # Keep the first occurrence of each ticket ID.
    duplicate = data["ticket_id"].duplicated(keep="first")
    reasons.loc[duplicate] = reasons.loc[duplicate].where(reasons.loc[duplicate].eq(""), reasons.loc[duplicate] + "; ")
    reasons.loc[duplicate] += "duplicate ticket_id"

    rejected = data.loc[reasons.ne("")].copy()
    rejected["rejection_reason"] = reasons.loc[reasons.ne("")]
    clean = data.loc[reasons.eq("")].copy()
    return clean, rejected
