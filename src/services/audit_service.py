from pathlib import Path

from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser
from src.parsers.sped_parser import SpedParser

def process_audit_pipeline(xml_dir: Path, sped_path: Path):
    with DisposableAuditDatabase(enterprise="homologation") as conn:
        data_repository = FiscalRepository(conn, 1000)

        xml_files_dir = XmlParser.get_xml_files(xml_dir)

        for file_path in xml_files_dir:
            for fiscal_doc in XmlParser.parse(file_path):
                data_repository.add_xml(fiscal_doc.to_tuple())

        sped_file = SpedParser(sped_path)

        data_repository.flush_batchs()
