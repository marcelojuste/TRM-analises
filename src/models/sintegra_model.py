from src.models.base_model import FiscalBaseModel

class SintegraBaseModel(FiscalBaseModel):

    CFOP_OPERATION_DIRECTION_DICTIONARY = {
        "5": "Saida",
        "6": "Saida",
        "7": "Saida",
        "1": "Entrada",
        "2": "Entrada",
        "3": "Entrada",
    }

    SINTEGRA_STATUS_DICTIONARY = {
        "N": "Autorizada",
        "E": "Autorizada",
        "S": "Nao autorizada",
        "X": "Nao autorizada"
    }

    def __init__(self, CFOP: str | None, model_code: str | None, **kwargs):
        if CFOP:
            self.document_status = self.CFOP_OPERATION_DIRECTION_DICTIONARY.get(CFOP[0], None)

        self.nfe_model = self.NFE_MODELS.get(model_code, None)

        super().__init__(**kwargs)
    
    def to_tuple(self):
        return super().to_tuple()