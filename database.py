"""SQLite persistence layer."""
from __future__ import annotations
import sqlite3
import pandas as pd

def save_tickets(frame: pd.DataFrame, db_path: str) -> None:
    """Create the ticket table and insert validated rows."""
    with sqlite3.connect(db_path) as connection:
        frame.to_sql("tickets", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_tickets_agent ON tickets(agent)")

def load_tickets(db_path: str) -> pd.DataFrame:
    with sqlite3.connect(db_path) as connection:
        return pd.read_sql_query("SELECT * FROM tickets ORDER BY created_at", connection)
