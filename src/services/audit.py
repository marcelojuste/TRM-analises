from src.global_var import QUERY_AUDIT_PATH, FILE_ENCODING
from src.database.connection import get_connection

def audit_query():
    # 1. Lê o arquivo SQL PRIMEIRO
    query_sql = QUERY_AUDIT_PATH.read_text(encoding=FILE_ENCODING)

    # 2. Abre a conexão APENAS SE o SQL for lido com sucesso
    with get_connection() as conn:
        df = conn.execute(query_sql).df()

    return df
