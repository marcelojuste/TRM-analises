from src.models.base_model import FiscalBaseModel


class XmlModel(FiscalBaseModel):
    access_key: str

    NFE_KEY_OPERATION_DICTIONARY = {
        "0": "Entry",
        "1": "Exit",
    }

    NFE_KEY_STATUS_DICTIONARY = {
        "00": "Authorized", 
        "01": "Authorized",
        "02": "Unauthorized",
        "03": "Unauthorized",
    }

    def __init__(
        self, 
        access_key: str, 
        operation_direction: str | int | None = None, 
        document_status: str | None = None, 
        document_status_number: str | int | None = None,
        document_number: int | str | None = None,
        **kwargs
    ):
        self.access_key = access_key

        raw_direction = str(operation_direction) if operation_direction is not None else str(document_status_number)
        calculated_operation_type = self.NFE_KEY_OPERATION_DICTIONARY.get(raw_direction, "Exit")

        raw_status = str(document_status) if document_status is not None else str(document_status_number)
        calculated_status = self.NFE_KEY_STATUS_DICTIONARY.get(raw_status, "Authorized")

        nfe_model = None
        extracted_doc_number = document_number

        if len(access_key) >= 34:
            model_code = access_key[20:22]
            nfe_model = self.NFE_MODELS.get(model_code, "NFe")
            if extracted_doc_number is None:
                extracted_doc_number = access_key[25:34]

        super().__init__(
            document_status=calculated_status,
            operation_type=calculated_operation_type,
            nfe_model=nfe_model,
            document_number=extracted_doc_number,
            **kwargs
        )

    def to_tuple(self) -> tuple:
        return super().to_tuple() + (self.access_key,)