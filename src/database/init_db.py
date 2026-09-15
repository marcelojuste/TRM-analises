import duckdb
from src.global_var import DB_PATH, SCHEMA_PATH, FILE_ENCODING

def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de schema não encontrado: {SCHEMA_PATH} --connection.py")

    schema_sql = SCHEMA_PATH.read_text(encoding=FILE_ENCODING)

    with duckdb.connect(str(DB_PATH)) as conn:
        conn.execute(schema_sql)
