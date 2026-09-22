from pathlib import Path

from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser
from src.parsers.sped_parser import SpedParser
from src.services.csv_exporter import ExportService

class AuditService:
    def __init__(
        self, 
        enterprise: str, 
        xml_dir: Path, 
        sped_path: Path, 
        sql_query_path: Path, 
        output_csv_path: Path
    ):
        self.enterprise = enterprise
        self.xml_dir = xml_dir
        self.sped_path = sped_path
        self.sql_query_path = sql_query_path
        self.output_csv_path = output_csv_path

    def run_pipeline(self) -> None:
        with DisposableAuditDatabase(enterprise=self.enterprise) as conn:

            with FiscalRepository(conn, batch_size=1000) as data_repository:
                self._process_xmls(data_repository)
                self._process_sped(data_repository)

            self._export_results(conn)

    def _process_xmls(self, data_repository: FiscalRepository) -> None:
        xml_files_dir = XmlParser.get_xml_files(self.xml_dir)
        
        for file_path in xml_files_dir:
            fiscal_doc = XmlParser.parse_xml(str(file_path))
            if fiscal_doc:
                data_repository.add_xml(fiscal_doc.to_tuple())

    def _process_sped(self, data_repository: FiscalRepository) -> None:
        sped_file = SpedParser(self.sped_path)
        sped_file._parse_sped()
        
        if sped_file.fiscal_notes:
            data_repository.add_sped(sped_file.fiscal_notes)

    def _export_results(self, conn) -> None:
        ExportService.export_query_to_csv(
            conn=conn,
            sql_file_path=self.sql_query_path,
            output_csv_path=self.output_csv_path
        )
