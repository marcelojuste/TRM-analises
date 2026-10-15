class FiscalBaseModel:
    cnpj_issuer: str
    total_value: float | int
    emission_date: str
    operation_type: str | None
    document_status: str | None
    nfe_model: str | None

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
        **kwargs
    ):
        self.cnpj_issuer = cnpj_issuer
        self.total_value = total_value
        self.emission_date = emission_date
        self.document_status = document_status
        self.operation_type = operation_type
        self.nfe_model = nfe_model

    def to_tuple(self):
        return (
            self.cnpj_issuer, 
            self.total_value, 
            self.emission_date, 
            self.operation_type,
            self.document_status,
            self.nfe_model,
        )