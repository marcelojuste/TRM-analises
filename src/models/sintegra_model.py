from src.models.base_model import FiscalBaseModel

class SintegraModel(FiscalBaseModel):

    CFOP_OPERATION_DIRECTION_DICTIONARY = {
        "T": True,
        "P": False
    }

    SINTEGRA_STATUS_DICTIONARY = {
        "N": True,
        "E": True,
        "S": False,
        "X": False
    }

    def __init__(self, operation_type_code: str | None, model_code: str | None, document_status_code: str | None, **kwargs):
        self.nfe_model = self.NFE_MODELS.get(model_code, None)

        if operation_type_code:
            self.operation_type = self.CFOP_OPERATION_DIRECTION_DICTIONARY.get(operation_type_code, None)

        if document_status_code:
            document_status = self.SINTEGRA_STATUS_DICTIONARY.get(document_status_code, None)

        super().__init__(document_status=document_status, **kwargs)
    
    def to_tuple(self):
        return super().to_tuple()