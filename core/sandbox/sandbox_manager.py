import sqlite3
import time
from catalog.pii_classifier import PIIClassifier

class SandboxManager:
    def __init__(self, schema: dict):
        self.schema = schema
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.classifier = PIIClassifier()

        self._load_schema()
        self._load_synthetic_data()

    def _load_schema(self):
        for table, columns in self.schema.items():
            cols = ", ".join([f"{c} {t}" for c, t in columns.items()])
            self.cursor.execute(f"CREATE TABLE {table} ({cols});")

    def _load_synthetic_data(self, rows: int = 20):
        for table in self.schema.keys():
            for i in range(rows):
                self.cursor.execute(
                    f"""
                    INSERT INTO {table}
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        i,
                        f"user{i}",
                        f"user{i}@example.com",
                        f"XXX-XX-{1000+i}",
                        50000 + i * 1000
                    )
                )

    def simulate_query(self, query: str):
        start = time.time()
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            duration = round((time.time() - start) * 1000, 2)

            columns = [desc[0] for desc in self.cursor.description]
            classified_columns = self.classifier.classify_columns(columns)

            return {
                "valid": True,
                "query_type": "SELECT",
                "columns_accessed": columns,
                "column_classification": classified_columns,
                "rows_returned": len(rows),
                "execution_time_ms": duration
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def teardown(self):
        self.conn.close()
