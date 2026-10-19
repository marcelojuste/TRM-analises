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

    def __init__(
        self, 
        operation_type_code: str | None = None, 
        model_code: str | None = None, 
        document_status_code: str | None = None, 
        **kwargs
    ):
        self.nfe_model = self.NFE_MODELS.get(model_code, model_code)

        operation_type = None
        if operation_type_code:
            operation_type = "Exit" if self.CFOP_OPERATION_DIRECTION_DICTIONARY.get(operation_type_code, True) else "Entry"

        document_status = None
        if document_status_code:
            document_status = "Authorized" if self.SINTEGRA_STATUS_DICTIONARY.get(document_status_code, True) else "Cancelled"

        super().__init__(
            document_status=document_status, 
            operation_type=operation_type, 
            nfe_model=self.nfe_model,
            **kwargs
        )
    
    def to_tuple(self) -> tuple:
        return super().to_tuple()