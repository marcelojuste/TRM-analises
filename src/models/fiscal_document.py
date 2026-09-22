from dataclasses import dataclass

@dataclass
class FiscalDocument:
    access_key: str
    cnpj_emit: str
    total_value: int
    emission_date: str
    nf_type: int
    situation_code: str

    def to_tuple(self) -> tuple:
        return (
            self.access_key,
            self.cnpj_emit,
            self.total_value,
            self.emission_date,
            self.nf_type,
            self.situation_code,
        )