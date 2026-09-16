from dataclasses import dataclass

@dataclass(slots=True)
class FiscalDocument:
    access_key: str
    total_value: int
    emission_date: str
    exit_date: str
    recipient_cnpj: str

    def to_tuple(self) -> tuple:
        return (
            self.access_key,
            self.total_value,
            self.emission_date,
            self.exit_date,
            self.recipient_cnpj,
        )