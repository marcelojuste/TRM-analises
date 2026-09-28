from pathlib import Path
from typing import List, Tuple

from src.app_paths import PATHS
from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser
from src.parsers.sped_parser import SpedParser
from src.services.excel_exporter import ExportService


class AuditService:
    nfe_dir: None | Path
    nfce_dir: None | Path
    sped_fiscal_path: None | Path
    sped_cofins_path: None | Path

    def __init__(self, nfe_dir: None | Path, nfce_dir: None | Path, sped_fiscal_path: None | Path, sped_cofins_path: None | Path):
        self.nfe_dir=nfe_dir
        self.nfce_dir=nfce_dir
        self.sped_fiscal_path=sped_fiscal_path
        self.sped_cofins_path=sped_cofins_path

    def run_pipeline(self) -> None:
        with SpedParser(self.sped_fiscal_path) as sped_fiscal_parser:
            sped_fiscal_notes = sped_fiscal_parser.fiscal_notes or []
            enterprise_name = sped_fiscal_parser.get_enterprise() or "EMPRESA_DESCONHECIDA"

        with SpedParser(self.sped_cofins_path) as sped_cofins_parser:
            sped_cofins_notes = sped_cofins_parser.fiscal_notes or []

        xml_notes = self._extract_xmls()

        sql_query_path = PATHS.queries_dir / "audit.sql"
        output_xlsx_path = PATHS.outputs_dir / f"relatorio_auditoria_{enterprise_name}.xlsx"

        with DisposableAuditDatabase(enterprise=enterprise_name) as conn:
            with FiscalRepository(conn, batch_size=1000) as repo:
                for xml_tuple in xml_notes:
                    repo.add_xml(xml_tuple)
                
                if sped_fiscal_notes:
                    repo.add_sped(sped_fiscal_notes)

                if sped_cofins_notes:
                    repo.add_sped(sped_cofins_notes)

            print("Total de XMLs no banco:", conn.execute("SELECT COUNT(*) FROM xml_documents;").fetchone()[0])
            print("Total de SPEDs no banco:", conn.execute("SELECT COUNT(*) FROM sped_documents;").fetchone()[0])

            ExportService.export_query_to_excel( 
                conn=conn,
                sql_file_path=sql_query_path,
                output_xlsx_path=output_xlsx_path
            )

    def _extract_xmls(self) -> List[Tuple]:
        xml_tuples = []

        if self.nfe_dir:
            for file_path in XmlParser.get_xml_files(self.nfe_dir):
                fiscal_doc = XmlParser.parse_xml(file_path)
                if fiscal_doc:
                    xml_tuples.append(fiscal_doc.to_tuple())

        if self.nfce_dir:
            for file_path in XmlParser.get_xml_files(self.nfce_dir):
                fiscal_doc = XmlParser.parse_xml(file_path)
                if fiscal_doc:
                    xml_tuples.append(fiscal_doc.to_tuple())

        return xml_tuples