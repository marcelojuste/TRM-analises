from pathlib import Path

def process_xml_files(xml_files: list):
    data_batch = []

    for xml_file in xml_files:
        path_xml = Path(xml_file)

        if not path_xml.exists() or not path_xml.is_file():
            return Error(f"Arquivo XML inválido: {xml_file} --process_xml_files.py")
        
        nfe = parse_nfe_xml(xml_file: tuple)
        data_batch.append(nfe)

    if not data_batch:
        return Error("Nenhum arquivo XML válido encontrado --process_xml_files.py")
    
    if not SQL_INSERT_XML.exists():
        return Error(f"Arquivo SQL de inserção não encontrado: {SQL_INSERT_XML} --process_xml_files.py")

    query_sql = config.SQL_INSERT_XML.read_text(encoding=config.FILE_ENCODING)

    get_connection().executemany(query_sql, data_batch)

