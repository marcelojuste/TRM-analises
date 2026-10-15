from src.models.xml_model import XmlModel

class SpedModel(XmlModel):

    def __init__(self, access_key: str, sped_number_fields: int, **kwargs):
        self.sped_type = "EFD_CONTRIBUICOES" if sped_number_fields >= 18 else "EFD_ICMS_IPI"
        super().__init__(access_key=access_key, **kwargs)

    def to_tuple(self):
        return super().to_tuple() + (self.sped_type,)
