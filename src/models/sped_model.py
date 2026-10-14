from src.models.xml_model import XmlBaseModel

class SpedBaseModel(XmlBaseModel):
    sped_type: str

    def __init__(self, sped_number_fields: int, **kwargs):
        self.sped_type = "EFD_CONTRIBUICOES" if sped_number_fields >= 18 else "EFD_ICMS_IPI"

        super().__init__(**kwargs)

    def to_tuple(self):
        return super().to_tuple() + (self.sped_type,)