import sqlite3
import uuid
import time
from catalog.pii_classifier import PIIClassifier

class SandboxManager:
    def __init__(self):
        self.db_name = f":memory:"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def load_schema(self, schema: dict):
        for table, columns in schema.items():
            cols = ", ".join([f"{c} {t}" for c, t in columns.items()])
            self.cursor.execute(f"CREATE TABLE {table} ({cols});")

    def load_synthetic_data(self, table: str, rows: int = 5):
        for i in range(rows):
            self.cursor.execute(f"INSERT INTO {table} VALUES ({i}, 'user{i}', 'user{i}@gmail.com', 'XXX-XX-{i}', {50000 + i * 1000})")

    def simulate_query(self, query: str):
        start = time.time()
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            duration = time.time() - start
            columns = [desc[0] for desc in self.cursor.description]
            classifier = PIIClassifier()
            classified_columns = classifier.classify_columns(columns)

            return{
                "status": "success",
                "columns_accessed": columns,
                "columns_classification": classified_columns,
                "rows_returned": len(rows),
                "execution_time": round(duration * 1000, 2)
            }
        
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    def teardown(self):
        self.conn.close()
                    
        
    

    
