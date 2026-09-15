from src.database.connection import get_connection
from src.global_var import QUERY_AUDIT_PATH, FILE_ENCODING

def audit_query():
    get_connection().execute(QUERY_AUDIT_PATH.read_text(encoding=FILE_ENCODING)) 
