class FiscalBaseModel:
    cnpj_issuer: str
    total_value: float
    emission_date: str
    document_status: str

    def __init__(self, cnpj_issuer: str, total_value: float, emission_date: str, document_status: str = "Unknown"):
        self.cnpj_issuer = cnpj_issuer
        self.total_value = total_value
        self.emission_date = emission_date
        self.document_status = document_status

    def to_tuple(self):
        return (
            self.cnpj_issuer, 
            self.total_value, 
            self.emission_date, 
            self.document_status
        )