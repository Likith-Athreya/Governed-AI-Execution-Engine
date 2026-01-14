import sqlite3
import time
import os
from agents.tools import classify_columns

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class SandboxManager:
    def __init__(self, schema: dict):
        self.schema = schema
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def simulate_query(self, query: str):
        start = time.time()
        try:
            query_upper = query.strip().upper()
            if query_upper.startswith("UPDATE"):
                query_type = "UPDATE"
            elif query_upper.startswith("SELECT"):
                query_type = "SELECT"
            else:
                return {
                    "valid": False,
                    "error": "Unsupported query type"
                }

            self.cursor.execute(query)

            if query_type == "UPDATE":
                affected_rows = self.cursor.rowcount
                duration = round((time.time() - start) * 1000, 2)

                import re
                set_match = re.search(r'SET\s+([^WHERE]+)', query_upper, re.IGNORECASE)
                columns_accessed = []
                if set_match:
                    set_clause = set_match.group(1)
                    assignments = [part.strip() for part in set_clause.split(',')]
                    for assignment in assignments:
                        if '=' in assignment:
                            col_name = assignment.split('=')[0].strip()
                            columns_accessed.append(col_name)

                classified_columns = classify_columns(columns_accessed)

                return {
                    "valid": True,
                    "query_type": "UPDATE",
                    "columns_accessed": columns_accessed,
                    "column_classification": classified_columns,
                    "rows_affected": affected_rows,
                    "execution_time_ms": duration
                }

            else:  # SELECT query
                rows = self.cursor.fetchall()
                duration = round((time.time() - start) * 1000, 2)

                columns = [desc[0] for desc in self.cursor.description]
                tables_accessed = self._extract_tables_from_query(query)
                classified_columns = classify_columns(columns)

                return {
                    "valid": True,
                    "query_type": "SELECT",
                    "tables_accessed": tables_accessed,
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

    def _extract_tables_from_query(self, query: str) -> list:
        """Extract table names from SQL query"""
        import re
        query_upper = query.strip().upper()

        # Look for FROM clause
        from_match = re.search(r'\bFROM\s+([^\s;]+)', query_upper, re.IGNORECASE)
        if from_match:
            from_clause = from_match.group(1).strip()
            # Handle JOINs
            tables = []
            for part in from_clause.split('JOIN'):
                table = part.strip().split()[0].strip()
                if table and table != ',':
                    tables.append(table)
            return tables if tables else [from_clause.split()[0].strip()]

        # Look for table references in query
        table_pattern = r'\b(?:FROM|JOIN|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, query_upper)
        return matches if matches else []

def execute_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql_upper = sql.strip().upper()
    is_update = sql_upper.startswith("UPDATE")

    cursor.execute(sql)

    if is_update:
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return {
            "operation": "UPDATE",
            "affected_rows": affected_rows
        }
    else:
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return {
            "columns": columns,
            "rows": rows
        }
