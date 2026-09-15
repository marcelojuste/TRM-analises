import duckdb
from src.database.init_db import init_db
from global_var import DB_PATH

def get_connection():
    if not DB_PATH.exists():
        init_db()

    return duckdb.connect(str(DB_PATH))
