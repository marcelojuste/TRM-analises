from src.global_var import FILE_ENCODING, INSERT_SPED_IPI_PATH, INSERT_SPED_COFINS_PATH
from src.database.connection import get_connection

def process_sped_file(sped_data_batch: list, type_sped: str):
    if not sped_data_batch:
        erro = (f"Nenhuma NFe encontrada no arquivo SPED --process_sped_file.py")
        return erro

    match type_sped:
        case "ICMS":
            query_sql = INSERT_SPED_IPI_PATH.read_text(encoding=FILE_ENCODING)
        case "COFINS":
            query_sql = INSERT_SPED_COFINS_PATH.read_text(encoding=FILE_ENCODING)
    
    get_connection().executemany(query_sql, sped_data_batch)
    