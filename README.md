# Customer Support Analytics & Management System
Python-based Customer Support Analytics System using Pandas, SQLite, Matplotlib, and Pytest for data analysis, KPI tracking, and automated reporting.
It validates incoming CSV records, stores clean tickets in SQLite, calculates service KPIs,
identifies SLA breaches, and exports management-ready reports and charts.

## Features

- CSV ingestion with data-quality checks
- SQLite database storage (no external database server required)
- KPI reporting: ticket volume, resolution rate, average response/resolution time, CSAT
- SLA breach analysis and priority/category breakdowns
- Monthly trend and agent performance reports
- CSV exports and PNG charts
- Command-line interface
- Unit tests for core analytics

## Tech stack

Python 3.10+, pandas, matplotlib, SQLite, pytest

## Project structure

```text
customer_support_analytics/
├── data/
│   └── sample_tickets.csv
├── reports/
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── database.py
│   ├── main.py
│   └── validation.py
├── tests/
│   └── test_analytics.py
├── requirements.txt
└── README.md
```

## Quick start

### 1. Create and activate a virtual environment

Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the project

From the project root:

```bash
python -m src.main --input data/sample_tickets.csv
```

The application creates `support_tickets.db` and writes reports to `reports/`.

Useful options:

```bash
python -m src.main --input data/sample_tickets.csv --output reports
python -m src.main --input data/sample_tickets.csv --db support_tickets.db
```

### 4. Run tests

```bash
pytest -q
```

## Data dictionary

| Column | Meaning |
|---|---|
| ticket_id | Unique ticket reference |
| created_at | Ticket creation timestamp |
| first_response_hours | Hours until first human response |
| resolution_hours | Hours until ticket resolution; blank if unresolved |
| status | Open, Pending, or Resolved |
| priority | Low, Medium, High, or Urgent |
| category | Billing, Delivery, Account, Technical, or Returns |
| agent | Support agent assigned |
| customer_region | Customer region |
| csat_score | Customer satisfaction score from 1 to 5 |
| sla_hours | Target resolution time in hours |

## Example outputs

- `reports/kpi_summary.json`
- `reports/priority_breakdown.csv`
- `reports/category_performance.csv`
- `reports/agent_performance.csv`
- `reports/monthly_trend.csv`
- `reports/sla_breaches.csv`
- `reports/monthly_ticket_volume.png`
- `reports/category_resolution_time.png`

## Design notes

The sample data is synthetic and is included only to demonstrate the workflow.
Replace it with anonymized data before using the project in a real organization.
The SLA breach rule is: a resolved ticket breaches SLA when `resolution_hours > sla_hours`;
an unresolved ticket breaches SLA when its age at analysis time exceeds `sla_hours`.

## Future improvements

- Add a REST API using FastAPI
- Add role-based authentication
- Connect a Power BI dashboard to the SQLite/CSV outputs
- Add scheduled ingestion and email alerts
- Add configurable SLA targets by priority


