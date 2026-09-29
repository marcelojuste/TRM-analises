import os
import sys
import ctypes
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from concurrent.futures import ProcessPoolExecutor
import threading

from src.app_paths import PATHS
from src.database.database import DisposableAuditDatabase
from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.xml_parser import XmlParser
from src.parsers.sped_parser import SpedParser
from src.services.excel_exporter import ExportService


class InterruptedException(Exception):
    pass


class NoXmlsFoundException(Exception):
    pass


class NoSpedRecordsFoundException(Exception):
    pass


class AuditService:
    nfe_dir: Optional[Path]
    nfce_dir: Optional[Path]
    sped_fiscal_path: Optional[Path]
    sped_cofins_path: Optional[Path]

    def __init__(
        self, 
        nfe_dir: Optional[Path] = None, 
        nfce_dir: Optional[Path] = None, 
        sped_fiscal_path: Optional[Path] = None, 
        sped_cofins_path: Optional[Path] = None,
        cancel_event: Optional[threading.Event] = None
    ):
        self.nfe_dir = nfe_dir
        self.nfce_dir = nfce_dir
        self.sped_fiscal_path = sped_fiscal_path
        self.sped_cofins_path = sped_cofins_path
        self.cancel_event = cancel_event

    def check_cancellation(self):
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedException("Operação cancelada pelo usuário.")

    def run_pipeline(self) -> Dict[str, Any]:
        self.set_low_process_priority()
        self.check_cancellation()

        enterprise_name = "EMPRESA_DESCONHECIDA"
        
        if self.sped_fiscal_path and self.sped_fiscal_path.exists():
            with SpedParser(self.sped_fiscal_path) as parser:
                parser.parse_metadata_only()
                found_name = parser.get_enterprise()
                if found_name and found_name != "EMPRESA_DESCONHECIDA":
                    enterprise_name = found_name

        self.check_cancellation()

        if enterprise_name == "EMPRESA_DESCONHECIDA" and self.sped_cofins_path and self.sped_cofins_path.exists():
            with SpedParser(self.sped_cofins_path) as parser:
                parser.parse_metadata_only()
                found_name = parser.get_enterprise()
                if found_name and found_name != "EMPRESA_DESCONHECIDA":
                    enterprise_name = found_name

        self.check_cancellation()
        xml_notes = self._extract_xmls()

        if not xml_notes:
            raise NoXmlsFoundException("Não foi possível encontrar os arquivos XML nos diretórios selecionados.")

        sql_query_path = PATHS.queries_dir / "audit.sql"
        output_xlsx_path = PATHS.outputs_dir / f"relatorio_auditoria_{enterprise_name}.xlsx"

        metrics = {
            "xml": {"qty": 0, "val": 0.0},
            "sped": {"qty": 0, "val": 0.0}
        }

        sped_records_count = 0

        with DisposableAuditDatabase(enterprise=enterprise_name) as conn:
            with FiscalRepository(conn, batch_size=250) as repo:
                for xml_tuple in xml_notes:
                    self.check_cancellation()
                    repo.add_xml(xml_tuple)
        
                if self.sped_fiscal_path and self.sped_fiscal_path.exists():
                    with SpedParser(self.sped_fiscal_path) as sped_fiscal_parser:
                        for sped_tuple in sped_fiscal_parser.parse_sped():
                            self.check_cancellation()
                            repo.add_sped([sped_tuple])
                            sped_records_count += 1

                if self.sped_cofins_path and self.sped_cofins_path.exists():
                    with SpedParser(self.sped_cofins_path) as sped_cofins_parser:
                        for sped_tuple in sped_cofins_parser.parse_sped():
                            self.check_cancellation()
                            repo.add_sped([sped_tuple])
                            sped_records_count += 1

            if sped_records_count == 0:
                raise NoSpedRecordsFoundException("Não foi possível encontrar os registros SPED nos arquivos selecionados.")

            self.check_cancellation()

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
            "enterprise_name": enterprise_name,
            "metrics": metrics
        }

    def _extract_xmls(self) -> List[Tuple]:
        xml_paths = []

        if self.nfe_dir and self.nfe_dir.exists():
            xml_paths.extend(XmlParser.get_xml_files(self.nfe_dir))

        if self.nfce_dir and self.nfce_dir.exists():
            xml_paths.extend(XmlParser.get_xml_files(self.nfce_dir))

        if not xml_paths:
            return []

        xml_tuples = []
        
        with ProcessPoolExecutor(max_workers=2) as executor:
            results = executor.map(XmlParser.parse_xml_to_tuple, xml_paths, chunksize=50)
            for res in results:
                self.check_cancellation()
                if res:
                    xml_tuples.append(res)

        return xml_tuples

    def set_low_process_priority(self) -> None:
        try:
            if sys.platform == "win32":
                BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                ctypes.windll.kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
            else:
                os.nice(10)
        except Exception as e:
            print(f"Não foi possível ajustar a prioridade: {e}")