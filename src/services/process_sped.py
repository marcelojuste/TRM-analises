from pathlib import Path

def process_sped_file(sped_data_batch: list, type_sped: str):
    if not sped_data_batch:
        return Error("Nenhuma NFe encontrada no arquivo SPED --process_sped_file.py")
    
    switch:
        case type_sped == "ICMS":
            query_sql = config.SQL_INSERT_SPED_IPI.read_text(encoding=config.FILE_ENCODING)
        case type_sped == "COFINS":
            query_sql = config.SQL_INSERT_SPED_COFINS.read_text(encoding=config.FILE_ENCODING)
    
    get_connection().executemany(query_sql, sped_data_batch)
    