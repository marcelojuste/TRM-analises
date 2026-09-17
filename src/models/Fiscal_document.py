from dataclasses import dataclass

@dataclass(slots=True)
class FiscalDocument:
    access_key: str
    total_value: int
    emission_date: str
    recipient_cnpj: str

    def __init__(self, access_key: str, total_value: int, emission_date: str, recipient_cnpj: str):
        self.access_key = access_key
        self.total_value = total_value
        self.emission_date = emission_date
        self.recipient_cnpj = recipient_cnpj

    def to_tuple(self) -> tuple:
        return (
            self.access_key,
            self.total_value
        )