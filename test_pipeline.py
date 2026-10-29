"""Unit and integration tests for Azure Data Analytics Pipeline."""
import unittest
from pipeline.etl import load_raw_data, calculate_analytics_summary, execute_sql_query

class TestAnalyticsPipeline(unittest.TestCase):
    def test_load_raw_data(self):
        data = load_raw_data()
        self.assertGreaterEqual(len(data), 10)
        self.assertIn("transaction_id", data[0])
        self.assertIn("total_revenue", data[0])
        self.assertIn("region", data[0])

    def test_calculate_analytics_summary(self):
        summary = calculate_analytics_summary()
        self.assertGreater(summary["total_revenue"], 0)
        self.assertGreaterEqual(summary["total_transactions"], 10)
        self.assertGreater(summary["avg_order_value"], 0)
        self.assertIn("revenue_by_region", summary)
        self.assertIn("revenue_by_category", summary)
        self.assertGreater(len(summary["revenue_by_region"]), 0)

    def test_execute_sql_query_valid(self):
        res = execute_sql_query("SELECT region, SUM(total_revenue) AS rev FROM sales GROUP BY region ORDER BY rev DESC;")
        self.assertIsNone(res["error"])
        self.assertGreater(res["row_count"], 0)
        self.assertIn("region", res["columns"])
        self.assertIn("rev", res["columns"])

    def test_execute_sql_query_security_guard(self):
        res = execute_sql_query("DROP TABLE sales;")
        self.assertIsNotNone(res["error"])
        self.assertIn("Security Restriction", res["error"])

if __name__ == "__main__":
    unittest.main()
