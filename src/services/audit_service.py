from pathlib import Path
from typing import List, Tuple

from src.app_paths import PATHS
from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser
from src.parsers.sped_parser import SpedParser
from src.services.excel_exporter import ExportService


class AuditService:
    def __init__(self, xml_dir: Path, sped_path: Path):
        self.xml_dir = xml_dir
        self.sped_path = sped_path

    def run_pipeline(self) -> None:
        with SpedParser(self.sped_path) as sped_parser:
            sped_notes = sped_parser.fiscal_notes or []
            enterprise_name = sped_parser.get_enterprise() or "EMPRESA_DESCONHECIDA"

        xml_notes = self._extract_xmls()

        sql_query_path = PATHS.queries_dir / "audit.sql"
        output_xlsx_path = PATHS.outputs_dir / f"relatorio_auditoria_{enterprise_name}.xlsx"

        with DisposableAuditDatabase(enterprise=enterprise_name) as conn:
            with FiscalRepository(conn, batch_size=1000) as repo:
                for xml_tuple in xml_notes:
                    repo.add_xml(xml_tuple)
                
                if sped_notes:
                    repo.add_sped(sped_notes)

            print("Total de XMLs no banco:", conn.execute("SELECT COUNT(*) FROM xml_documents;").fetchone()[0])
            print("Total de SPEDs no banco:", conn.execute("SELECT COUNT(*) FROM sped_documents;").fetchone()[0])

            ExportService.export_query_to_excel( 
                conn=conn,
                sql_file_path=sql_query_path,
                output_xlsx_path=output_xlsx_path
            )

    def _extract_xmls(self) -> List[Tuple]:
        xml_tuples = []

        for file_path in XmlParser.get_xml_files(self.xml_dir):
            fiscal_doc = XmlParser.parse_xml(file_path)
            if fiscal_doc:
                xml_tuples.append(fiscal_doc.to_tuple())

        return xml_tuples