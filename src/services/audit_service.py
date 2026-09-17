from pathlib import Path
from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser

def process_audit_pipeline(xml_dir: Path):
    with DisposableAuditDatabase(enterprise="homologation") as conn:
        data_repository = FiscalRepository(conn, 1000)

        xml_files = XmlParser.get_xml_files(xml_dir)

        for file_path in xml_files:
            for fiscal_doc in XmlParser.parse(file_path):
                data_repository.add_xml(fiscal_doc.to_tuple())

        data_repository.flush_batchs()
