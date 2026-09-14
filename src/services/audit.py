import duckdb
from pathlib import Path

def audit_query():
    df = get_connection().execute(config.QUERY_AUDIT_PATH.read_text(encoding=config.FILE_ENCODING)).df()

    return df
