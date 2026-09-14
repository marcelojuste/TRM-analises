import duckdb
from pathlib import Path

def get_connection():
    if not DB_PATH.exists():
        init_db()

    return duckdb.connect(str(DB_PATH))