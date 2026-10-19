from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional
from pathlib import Path
import pandas as pd
import threading
import duckdb
import ctypes
import sys
import os


from src.repositories.fiscal_repository import FiscalRepository
from src.parsers.sintegra_parser import SintegraParser
from src.parsers.sped_parser import SpedParser
from src.parsers.xml_parser import XmlParser
from src.path_manager import PATHS


class AuditService:

    def __init__(
        self,
        fiscal_archive_path: Path,
        nfe_dir_path: Optional[Path] = None,
        nfce_dir_path: Optional[Path] = None,
        fiscal_archive_path_2: Optional[Path] = None,
        cancel_event: Optional[threading.Event] = None,
        is_sped: bool = True,
    ):
        self.nfe_dir_path = nfe_dir_path
        self.nfce_dir_path = nfce_dir_path
        self.fiscal_archive_path = fiscal_archive_path
        self.fiscal_archive_path_2 = fiscal_archive_path_2
        self.cancel_event = cancel_event
        self.is_sped = is_sped
        self.repository = FiscalRepository(self.is_sped)
        self.enterprise: Optional[str] = None
        self.metrics: Optional[dict] = None

    @staticmethod
    def _get_xml_files(directory_path: Path) -> list[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Caminho do diretório inválido: {directory_path}")

        xml_files_paths = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(".xml"):
                    xml_files_paths.append(Path(root) / file)

        return xml_files_paths

    @staticmethod
    def _set_low_process_priority() -> None:
        try:
            if sys.platform == "win32":
                BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                ctypes.windll.kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
            else:
                os.nice(10)
        except Exception as e:
            print(f"Falha ao ajustar a prioridade do processo: {e}")

    def _check_cancellation(self) -> None:
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedError("Operação cancelada pelo utilizador.")

    def _process_sped_files(self) -> None:
        for sped_path in (self.fiscal_archive_path, self.fiscal_archive_path_2):
            if sped_path and sped_path.exists():
                with SpedParser(sped_path) as parser:
                    sped_records = list(parser.parse_sped())
                    if parser.enterprise:
                        self.enterprise = parser.enterprise
                    if sped_records:
                        self._check_cancellation()
                        self.repository.add_fiscal_archive(sped_records)

    def _process_sintegra_files(self) -> None:
        sintegra_path = self.fiscal_archive_path
        if sintegra_path and sintegra_path.exists():
            parser = SintegraParser(sintegra_path)
            sintegra_records = list(parser.parse_sintegra())
            if parser.enterprise:
                self.enterprise = parser.enterprise
            if sintegra_records:
                self._check_cancellation()
                self.repository.add_fiscal_archive(sintegra_records)

    @staticmethod
    def _parse_single_xml(xml_path: Path) -> list[tuple]:
        parser = XmlParser(xml_path)
        return list(parser.parse_xml() or [])

    def _process_xmls(self) -> None:
        xml_paths: list[Path] = []

        if self.nfe_dir_path and self.nfe_dir_path.exists():
            xml_paths.extend(self._get_xml_files(self.nfe_dir_path))
        if self.nfce_dir_path and self.nfce_dir_path.exists():
            xml_paths.extend(self._get_xml_files(self.nfce_dir_path))

        if not xml_paths:
            return

        xml_tuples: list[tuple] = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            for xml_results in executor.map(self._parse_single_xml, xml_paths):
                self._check_cancellation()
                if xml_results:
                    xml_tuples.extend(xml_results)

        self.repository.add_xml(xml_tuples)

    def _execute_audit_query(self, df_xml: pd.DataFrame, df_fiscal: pd.DataFrame) -> pd.DataFrame:
        query_file = PATHS.sped_query_path if self.is_sped else PATHS.sintegra_query_path

        if not query_file.exists():
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {query_file}")

        query_sql = query_file.read_text(encoding="utf-8")

        con = duckdb.connect(database=":memory:")
        con.register("df_xml", df_xml)
        con.register("df_fiscal", df_fiscal)

        return con.execute(query_sql).df()

    def run_pipeline(self) -> dict[str, Any]:
        self._set_low_process_priority()
        self._check_cancellation()

        has_nfe = self.nfe_dir_path and self.nfe_dir_path.exists()
        has_nfce = self.nfce_dir_path and self.nfce_dir_path.exists()

        if has_nfe or has_nfce:
            self._process_xmls()
        else:
            raise FileNotFoundError("Diretórios de XMLs não foram informados ou são inválidos.")

        if self.is_sped and (self.fiscal_archive_path or self.fiscal_archive_path_2):
            self._process_sped_files()
        elif not self.is_sped and self.fiscal_archive_path:
            self._process_sintegra_files()
        else:
            raise FileNotFoundError("Arquivos fiscais não foram informados ou não existem.")

        df_xml, df_fiscal = self.repository.prepare_data_frames()
        
        self.metrics = self.repository.calculate_metrics(df_xml, df_fiscal)
        audit_results_df = self._execute_audit_query(df_xml, df_fiscal)

        return {
            "enterprise": self.enterprise or "EMPRESA_DESCONHECIDA",
            "metrics": self.metrics,
            "audit_results": audit_results_df,
        }