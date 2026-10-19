from src.models.base_model import FiscalBaseModel


class SintegraModel(FiscalBaseModel):

    CFOP_OPERATION_DIRECTION_DICTIONARY = {
        "T": "Entry",
        "0": "Entry",
        "P": "Exit",
        "1": "Exit",
        "S": "Exit",
    }

    SINTEGRA_STATUS_DICTIONARY = {
        "N": "Autorized",
        "E": "Autorized",
        "S": "Cancelled",
        "X": "Cancelled"
    }

    def __init__(
        self, 
        operation_type_code: str | None = None, 
        model_code: str | None = None, 
        document_status_code: str | None = None, 
        **kwargs
    ):
        self.nfe_model = self.NFE_MODELS.get(model_code, model_code)

        if operation_type_code:
            operation_type = self.CFOP_OPERATION_DIRECTION_DICTIONARY.get(operation_type_code)

        if document_status_code:
            document_status = self.SINTEGRA_STATUS_DICTIONARY.get(document_status_code)

        super().__init__(
            document_status=document_status, 
            operation_type=operation_type, 
            nfe_model=self.nfe_model,
            **kwargs
        )
    
    def to_tuple(self) -> tuple:
        return super().to_tuple()