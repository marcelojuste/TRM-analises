from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor

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
        self.nfe_dir = nfe_dir
        self.nfce_dir = nfce_dir
        self.sped_fiscal_path = sped_fiscal_path
        self.sped_cofins_path = sped_cofins_path

    def run_pipeline(self) -> dict:
        enterprise_name = "EMPRESA_DESCONHECIDA"
        
        sped_fiscal_notes = []
        if self.sped_fiscal_path and self.sped_fiscal_path.exists():
            with SpedParser(self.sped_fiscal_path) as sped_fiscal_parser:
                sped_fiscal_notes = sped_fiscal_parser.fiscal_notes or []
                found_name = sped_fiscal_parser.get_enterprise()
                if found_name and found_name != "EMPRESA_DESCONHECIDA":
                    enterprise_name = found_name

        sped_cofins_notes = []
        if self.sped_cofins_path and self.sped_cofins_path.exists():
            with SpedParser(self.sped_cofins_path) as sped_cofins_parser:
                sped_cofins_notes = sped_cofins_parser.fiscal_notes or []
                # Se ainda não identificou a empresa pelo Fiscal, pega do Contribuições
                if enterprise_name == "EMPRESA_DESCONHECIDA":
                    found_name = sped_cofins_parser.get_enterprise()
                    if found_name and found_name != "EMPRESA_DESCONHECIDA":
                        enterprise_name = found_name

        xml_notes = self._extract_xmls()

        sql_query_path = PATHS.queries_dir / "audit.sql"
        output_xlsx_path = PATHS.outputs_dir / f"relatorio_auditoria_{enterprise_name}.xlsx"

        metrics = {
            "xml": {"qty": 0, "val": 0.0},
            "sped": {"qty": 0, "val": 0.0}
        }

        with DisposableAuditDatabase(enterprise=enterprise_name) as conn:
            with FiscalRepository(conn, batch_size=1000) as repo:
                for xml_tuple in xml_notes:
                    repo.add_xml(xml_tuple)
                
                if sped_fiscal_notes:
                    repo.add_sped(sped_fiscal_notes)

                if sped_cofins_notes:
                    repo.add_sped(sped_cofins_notes)

            with FiscalRepository(conn) as repo:
                metrics["xml"] = repo.get_xml_metrics()
                metrics["sped"] = repo.get_sped_metrics()

            exporter = ExportService(
                conn=conn,
                sql_file_path=sql_query_path,
                output_xlsx_path=output_xlsx_path,
                enterprise_name=enterprise_name
            )

            exporter.export_query_to_excel()

        return {
            "excel_path": output_xlsx_path,
            "metrics": metrics
        }

    def _extract_xmls(self) -> List[Tuple]:
        xml_paths = []

        if self.nfe_dir:
            xml_paths.extend(XmlParser.get_xml_files(self.nfe_dir))

        if self.nfce_dir:
            xml_paths.extend(XmlParser.get_xml_files(self.nfce_dir))

        if not xml_paths:
            return []

        xml_tuples = []
        with ProcessPoolExecutor() as executor:
            results = executor.map(XmlParser.parse_xml_to_tuple, xml_paths, chunksize=500)
            for res in results:
                if res:
                    xml_tuples.append(res)

        return xml_tuples