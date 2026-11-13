import pandas as pd
from src.analytics import calculate_kpis, add_sla_flag
from src.validation import validate_tickets

def sample_frame():
    return pd.DataFrame([
        {"ticket_id":"T1","created_at":"2025-01-01 10:00:00","first_response_hours":1.0,
         "resolution_hours":4.0,"status":"Resolved","priority":"High","category":"Delivery",
         "agent":"Asha","customer_region":"North","csat_score":5,"sla_hours":8},
        {"ticket_id":"T2","created_at":"2025-01-02 10:00:00","first_response_hours":2.0,
         "resolution_hours":None,"status":"Open","priority":"Low","category":"Billing",
         "agent":"Bilal","customer_region":"South","csat_score":None,"sla_hours":24},
    ])

def test_kpi_calculation():
    result = calculate_kpis(sample_frame())
    assert result["total_tickets"] == 2
    assert result["resolved_tickets"] == 1
    assert result["resolution_rate_pct"] == 50.0
    assert result["average_csat"] == 5.0

def test_validation_rejects_duplicate_ticket():
    frame = pd.concat([sample_frame(), sample_frame().iloc[[0]]], ignore_index=True)
    clean, rejected = validate_tickets(frame)
    assert len(clean) == 2
    assert len(rejected) == 1
    assert "duplicate ticket_id" in rejected.iloc[0]["rejection_reason"]

def test_sla_flag_for_resolved_ticket():
    frame = sample_frame().iloc[[0]].copy()
    frame["resolution_hours"] = 12
    flagged = add_sla_flag(frame)
    assert bool(flagged.iloc[0]["sla_breached"]) is True
