from src.models.fiscal_base_model import FiscalBaseModel

class SintegraBaseModel(FiscalBaseModel):
    def __init__(self, document_status_char: str, **kwargs):
        if (document_status_char == "T"):
            self.document_status = "Entrada"
        elif (document_status_char == "P"):
            self.document_status = "Saída"
        else:
            self.document_status = "Unknown"

        super().__init__(**kwargs)

    def to_tuple(self):
        return super().to_tuple() + (self.document_status,)