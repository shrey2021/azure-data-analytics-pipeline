"""ETL Pipeline, Analytics Engine & SQL Workbench for Azure Data Analytics."""
import csv
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_sales_data.csv"

def get_db_connection() -> sqlite3.Connection:
    """Initialize an in-memory SQLite database populated with the sales dataset."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE sales (
            transaction_id TEXT PRIMARY KEY,
            timestamp TEXT,
            customer_id TEXT,
            region TEXT,
            product_category TEXT,
            units INTEGER,
            unit_price REAL,
            total_revenue REAL,
            payment_method TEXT,
            is_churn_risk INTEGER
        );
    """)

    if DATA_PATH.exists():
        with open(DATA_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = [
                (
                    row["transaction_id"],
                    row["timestamp"],
                    row["customer_id"],
                    row["region"],
                    row["product_category"],
                    int(row["units"]),
                    float(row["unit_price"]),
                    float(row["total_revenue"]),
                    row["payment_method"],
                    int(row["is_churn_risk"])
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, records)
            conn.commit()
            
    return conn

def load_raw_data() -> List[Dict[str, Any]]:
    """Ingest raw CSV dataset into a list of dict records."""
    records = []
    if not DATA_PATH.exists():
        return records
    with open(DATA_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "transaction_id": row["transaction_id"],
                "timestamp": row["timestamp"],
                "customer_id": row["customer_id"],
                "region": row["region"],
                "product_category": row["product_category"],
                "units": int(row["units"]),
                "unit_price": float(row["unit_price"]),
                "total_revenue": float(row["total_revenue"]),
                "payment_method": row["payment_method"],
                "is_churn_risk": int(row["is_churn_risk"])
            })
    return records

def calculate_analytics_summary() -> Dict[str, Any]:
    """Calculate key financial, regional, payment, and customer churn metrics."""
    data = load_raw_data()
    if not data:
        return {}

    total_revenue = sum(r["total_revenue"] for r in data)
    total_transactions = len(data)
    total_units_sold = sum(r["units"] for r in data)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0.0
    churn_risks = sum(1 for r in data if r["is_churn_risk"] == 1)
    churn_rate_pct = (churn_risks / total_transactions) * 100 if total_transactions else 0.0

    # Regional revenue
    regions: Dict[str, float] = {}
    for r in data:
        reg = r["region"]
        regions[reg] = regions.get(reg, 0.0) + r["total_revenue"]

    # Product category revenue
    categories: Dict[str, float] = {}
    for r in data:
        cat = r["product_category"]
        categories[cat] = categories.get(cat, 0.0) + r["total_revenue"]

    # Payment method breakdown
    payments: Dict[str, int] = {}
    for r in data:
        pm = r["payment_method"]
        payments[pm] = payments.get(pm, 0) + 1

    return {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions,
        "total_units_sold": total_units_sold,
        "avg_order_value": round(avg_order_value, 2),
        "churn_risk_count": churn_risks,
        "churn_rate_percent": round(churn_rate_pct, 1),
        "revenue_by_region": sorted([{"region": k, "revenue": round(v, 2)} for k, v in regions.items()], key=lambda x: x["revenue"], reverse=True),
        "revenue_by_category": sorted([{"category": k, "revenue": round(v, 2)} for k, v in categories.items()], key=lambda x: x["revenue"], reverse=True),
        "transactions_by_payment": [{"method": k, "count": v} for k, v in payments.items()]
    }

def execute_sql_query(query: str) -> Dict[str, Any]:
    """Execute arbitrary SQL query safely on the in-memory SQLite analytics warehouse."""
    sanitized = query.strip()
    # Guard against destructive queries in read-only analytics console
    first_token = sanitized.split()[0].upper() if sanitized else ""
    if first_token not in ("SELECT", "WITH", "EXPLAIN"):
        return {
            "query": query,
            "error": "Security Restriction: Only SELECT, WITH, or EXPLAIN queries are permitted on this analytics cluster.",
            "row_count": 0,
            "columns": [],
            "rows": []
        }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sanitized)
        rows_raw = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(r) for r in rows_raw]
        conn.close()
        return {
            "query": query,
            "error": None,
            "row_count": len(rows),
            "columns": columns,
            "rows": rows
        }
    except Exception as exc:
        return {
            "query": query,
            "error": str(exc),
            "row_count": 0,
            "columns": [],
            "rows": []
        }
