from models.fiscal_base_model import FiscalBaseModel

class XmlBaseModel(FiscalBaseModel):
    access_key: str
    nfe_model: str

    def __init__(self, access_key: str, document_status_number: int, **kwargs):
        self.access_key = access_key

        if document_status_number == 0:
            doc_status = "Entrada"
        elif document_status_number == 1:
            doc_status = "Saída"
        else:
            doc_status = "Unknown"

        if len(access_key) >= 22:
            model_code = access_key[20:22]
            if model_code == "55":
                self.nfe_model = "NFe"
            elif model_code == "65":
                self.nfe_model = "NFCe"
            else:
                self.nfe_model = "Unknown"
        else:
            self.nfe_model = "Unknown"
        
        super().__init__(document_status=doc_status, **kwargs)

    def to_tuple(self):
        return super().to_tuple() + (self.access_key, self.nfe_model)