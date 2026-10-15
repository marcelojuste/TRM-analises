from src.models.base_model import FiscalBaseModel


class XmlBaseModel(FiscalBaseModel):
    access_key: str

    NFE_KEY_OPERATION_DICTIONARY = {
        "0": "Entrada",
        "1": "Saída",
    }

    NFE_KEY_STATUS_DICTIONARY = {
        "00": "Autorizada", 
        "01": "Autorizada",
        "02": "Nao autorizada",
        "03": "Nao autorizada",
    }

    def __init__(
        self, 
        access_key: str, 
        operation_direction: str | int | None = None, 
        document_status: str | None = None, 
        document_status_number: str | int | None = None,
        **kwargs
    ):
        self.access_key = access_key

        raw_direction = operation_direction if operation_direction is not None else document_status_number
        calculated_operation_type = self.NFE_KEY_OPERATION_DICTIONARY.get(raw_direction, "Saída")

        raw_status = document_status if document_status is not None else document_status_number
        calculated_status = self.NFE_KEY_STATUS_DICTIONARY.get(raw_status, "Autorizada")

        nfe_model = None
        if len(access_key) >= 22:
            model_code = access_key[20:22]
            nfe_model = self.NFE_MODELS.get(model_code, "NFe")

        super().__init__(
            document_status=calculated_status,
            operation_type=calculated_operation_type,
            nfe_model=nfe_model,
            **kwargs
        )

    def to_tuple(self):
        return (
            self.cnpj_issuer,
            self.total_value,
            self.emission_date,
            self.operation_type,
            self.access_key,
            self.nfe_model,
        )