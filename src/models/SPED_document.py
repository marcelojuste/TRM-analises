from dataclasses import dataclass
from src.models.Fiscal_document import FiscalDocument

@dataclass(slots=True)
class SPEDDocument(FiscalDocument):
    sped_type: str

    def to_tuple(self) -> tuple:
        return super().to_tuple() + (
            self.sped_type
        )