from src.models.xml_model import XmlModel
from src.models.sped_model import SpedModel
from src.models.sintegra_model import SintegraModel


class FiscalRepository:
    def __init__(self, is_sped: bool):
        self.fiscal_archive_type = "SPED" if is_sped else "SINTEGRA"

        self.xml_data_hub: list[tuple] = []
        self.fiscal_archive_data_hub: list[tuple] = []

    def add_xml(self, xml: tuple) -> None:
        self.xml_data_hub.append(xml)

    def add_fiscal_archive(self, fiscal_archive: tuple) -> None:
        self.fiscal_archive_data_hub.append(fiscal_archive)

    def _clean_hubs(self) -> None:
        self.xml_data_hub.clear()
        self.fiscal_archive_data_hub.clear()

    @property
    def xml_data_hub_length(self) -> int:
        return len(self.xml_data_hub)

    @property
    def fiscal_archive_data_hub_length(self) -> int:
        return len(self.fiscal_archive_data_hub)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clean_hubs()