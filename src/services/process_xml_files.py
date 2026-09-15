from pathlib import Path
from src.global_var import FILE_ENCODING, INSERT_NFE_PATH
from src.database.connection import get_connection
from src.parsers.nfe_parser import parse_nfe_xml

def process_xml_files(xml_files: list):
    xml_data_batch = []

    for xml_file in xml_files:
        path_xml = Path(xml_file)

        if not path_xml.exists() or not path_xml.is_file():
            return print(f"Arquivo XML inválido: {xml_file} --process_xml_files.py")
        
        nfe = parse_nfe_xml(str(path_xml))
        xml_data_batch.append(nfe)

    if not xml_data_batch:
        return print(f"Nenhum arquivo XML válido encontrado --process_xml_files.py")
    
    if not INSERT_NFE_PATH.exists():
        return print(f"Arquivo SQL de inserção não encontrado: {INSERT_NFE_PATH} --process_xml_files.py")

    query_sql = INSERT_NFE_PATH.read_text(encoding=FILE_ENCODING)

    get_connection().executemany(query_sql, xml_data_batch)

