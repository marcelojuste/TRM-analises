from dataclasses import dataclass
from src.models.Fiscal_document import FiscalDocument

@dataclass(slots=True)
class SPEDDocument(FiscalDocument):
    sped_type: str
    situation_code: str

    def __init__(
        self,
        access_key: str,
        total_value: int,
        emission_date: str,
        exit_date: str,
        recipient_cnpj: str,
        sped_type: str,
        situation_code: str,
    ):
        super().__init__(
            access_key, total_value, emission_date, exit_date, recipient_cnpj
        )
        self.sped_type = sped_type
        self.situation_code = situation_code

    def to_tuple(self) -> tuple:
        return super().to_tuple() + (
            self.sped_type,
            self.situation_code,
        )