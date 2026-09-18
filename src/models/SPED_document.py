from dataclasses import dataclass
from src.models.fiscal_document import FiscalDocument

@dataclass(slots=True)
class SpedDocument(FiscalDocument):
    sped_type: str

    def to_tuple(self) -> tuple:
        return super().to_tuple() + (
            self.sped_type,
            )