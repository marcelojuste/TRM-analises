from pathlib import Path

from parsers.base_parser import FiscalDocumentBaseModelParser


class SintegraParser(FiscalDocumentBaseModelParser):

    def __init__(self, sintegra_path: Path):
        super().__init__(sintegra_path)

    
    