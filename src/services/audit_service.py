from concurrent.futures import ThreadPoolExecutor
from typing import Union, Optional, Any
from pathlib import Path
import pandas as pd
import threading
import ctypes
import sys
import os

from src.models.sintegra_model import SintegraModel
from src.models.sped_model import SpedModel
from src.models.xml_model import XmlModel

from src.parsers.sintegra_parser import SintegraParser
from src.parsers.sped_parser import SpedParser
from src.parsers.xml_parser import XmlParser

from src.repositories.fiscal_repository import FiscalRepository

FiscalArchives = Union[SintegraModel, SpedModel]

class AuditService:

    def __init__(
            self, 
            fiscal_archive_path: Path,
            nfe_dir_path: Optional[Path] = None, 
            nfce_dir_path: Optional[Path] = None, 
            fiscal_archive_path_2: Optional[Path] = None,
            cancel_event: Optional[threading.Event] = None,
            is_sped: bool = True
            ):
        self.nfe_dir_path = nfe_dir_path
        self.nfce_dir_path = nfce_dir_path
        self.fiscal_archive_path = fiscal_archive_path
        self.fiscal_archive_path_2 = fiscal_archive_path_2
        self.cancel_event = cancel_event
        self.is_sped = is_sped
        self.repository = FiscalRepository(self.is_sped)

    @staticmethod
    def _get_xml_files(directory_path: Path) -> list[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {directory_path}")

        xml_files_paths = []

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(".xml"):
                    xml_files_paths.append(os.path.join(root, file))

        return xml_files_paths

    def _check_cancellation(self) -> None:
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedError("Operacao cancelada pelo usuario.")

    def _process_sped_files(self) -> None:
        for sped_path in (self.fiscal_archive_path, self.fiscal_archive_path_2):
            if sped_path and sped_path.exists():
                with SpedParser(sped_path) as parser:
                    sped_records = list(parser.parse_sped())
                    if sped_records:
                        self._check_cancellation()
                        self.repository.add_fiscal_archive(sped_records)

    def _process_sintegra_files(self) -> None:
        sintegra_path = self.fiscal_archive_path
        if sintegra_path and sintegra_path.exists():
            with SintegraParser(sintegra_path) as parser:
                sintegra_records = list(parser.parse_sintegra())
                if sintegra_records:
                    self._check_cancellation()
                    self.repository.add_fiscal_archive(sintegra_records)

    def _extract_xmls(self) -> None:
        xml_paths = []

        if self.nfe_dir_path and self.nfe_dir_path():
            xml_paths.extend(self._get_xml_files(self.nfe_dir_path))
        if self.nfce_dir_path and self.nfce_dir_path():
            xml_paths.extend(self._get_xml_files(self.nfce_dir_path))

        if not xml_paths:
            return

        xml_tuples = []

        with ThreadPoolExecutor(max_workers=2) as executor:
            for xmls in executor.map(XmlParser.parse_xml_to_tuple, xml_paths, chunksize=100):
                if self.cancel_event and self.cancel_event.is_set():
                    raise
                if xmls:
                    xml_paths.append(xmls)

        xml_paths.clear() 

        return xml_tuples

    def _set_low_process_priority(self) -> None:
        try:
            if sys.platform == "win32":
                BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                ctypes.windll.kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
            else:
                os.nice(10)
        except Exception as e:
            print(f"Não foi possível ajustar a prioridade do processo: {e}")

    def run_pipeline(self) -> dict[str, Any]:
        self._set_low_process_priority()
        self.check_cancellation()

        