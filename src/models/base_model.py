class FiscalBaseModel:
    cnpj_issuer: str
    total_value: float | int
    emission_date: str
    operation_type: str | None
    document_status: str | None
    nfe_model: str | None
    document_number: int | str | None

    NFE_MODELS = {
        "55": "NFe",
        "65": "NFCe"
    }

    def __init__(
        self,
        cnpj_issuer: str,
        total_value: float | int,
        emission_date: str,
        document_status: str | None = None,
        operation_type: str | None = None,
        nfe_model: str | None = None,
        document_number: int | str | None = None
    ):
        self.cnpj_issuer = cnpj_issuer
        self.total_value = total_value
        self.emission_date = emission_date
        self.document_status = document_status
        self.operation_type = operation_type
        self.nfe_model = nfe_model
        self.document_number = str(document_number).lstrip("0") if document_number is not None else None

    def to_tuple(self) -> tuple:
        return (
            self.cnpj_issuer, 
            self.total_value, 
            self.emission_date, 
            self.operation_type,
            self.document_status,
            self.nfe_model,
            self.document_number,
        )