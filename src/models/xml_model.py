from models.base_model import FiscalBaseModel

class XmlBaseModel(FiscalBaseModel):
    access_key: str

    NFE_KEY_OPERATION_DICTIONARY = {
        "00": "Entrada",
        "01": "Saida"
    }

    NFE_KEY_STATUS_DICTIONARY = {
        "00" | "01": "Autorizada",
        "02" | "03": "Nao autorizada"
    }

    def __init__(self, access_key: str, operation_direction: str, document_status: str | None = None, **kwargs):
        self.access_key = access_key

        operation_type = self.NFE_KEY_OPERATION_DICTIONARY.get(operation_direction, None)
        self.document_status = self.NFE_KEY_STATUS_DICTIONARY.get(document_status, None)

        if len(access_key) >= 22:
            model_code = access_key[20:22]
            self.nfe_model = self.NFE_MODELS.get(model_code, None)
        
        super().__init__(operation_type=operation_type, document_status=document_status, **kwargs)

    def to_tuple(self):
        return super().to_tuple() + (self.access_key,)