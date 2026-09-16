from src.global_var import FILE_ENCODING, INSERT_SPED_IPI_PATH, INSERT_SPED_COFINS_PATH
from src.database.connection import get_connection

def process_sped_file(sped_data_batch: list, type_sped: str):
    if not sped_data_batch:
        raise ValueError("Nenhuma NFe encontrada no arquivo SPED. Verifique se o arquivo possui registros C100 com COD_SIT = '00' e Chaves de NF-e válidas.")

    match type_sped:
        case "ICMS" | "IPI":
            query_sql = INSERT_SPED_IPI_PATH.read_text(encoding=FILE_ENCODING)
        case "COFINS" | "PIS_COFINS":
            query_sql = INSERT_SPED_COFINS_PATH.read_text(encoding=FILE_ENCODING)
        case _:
            raise ValueError(f"Tipo de SPED desconhecido: {type_sped}")

    with get_connection() as conn:
        conn.executemany(query_sql, sped_data_batch)
        