from typing import Union, Optional
from pathlib import Path
import pandas as pd
import threading
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
            nfe_dir_path: Optional[Path] = None, 
            nfce_dir_path: Optional[Path] = None, 
            fiscal_archive_path: Optional[Path] = None, 
            fiscal_archive_path_2: Optional[Path] = None,
            cancel_event: Optional[threading.Event] = None
            ):
        self.nfe_dir_path = nfe_dir_path
        self.nfce_dir_path = nfce_dir_path
        self.fiscal_archive_path = fiscal_archive_path
        self.fiscal_archive_path_2 = fiscal_archive_path_2
        self.cancel_event = cancel_event

    @staticmethod
    def get_xml_files(directory_path: Path) -> list[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {directory_path}")

        xml_files_paths = []

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(".xml"):
                    xml_files_paths.append(os.path.join(root, file))

        return xml_files_paths

    def check_cancellation(self) -> None:
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedError("Operacao cancelada pelo usuario.")

    def run_pipeline(self):
        return
    
