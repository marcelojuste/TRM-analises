from typing import Generator
from pathlib import Path

from src.models.sped_document import SpedDocument

class SpedParser:
    def __init__(self, sped_file: Path):
        self.sped_file = sped_file
        self.file_path = sped_file
        self.enterprise_name: str | None = None
        self.fiscal_notes: list[tuple] | None = None
        self.cnpj_emit: str = ""
        self.sped_type: str = ""

    def _parse_0000(self, line_0000: str):
        fields = line_0000.strip().split('|')
        
        if len(fields) < 4 or fields[1] != '0000':
            self.sped_type = "DESCONHECIDO"
            return

        # A EFD Contribuições tem no mínimo 16 pipes no cabeçalho (len >= 17)
        # A EFD ICMS/IPI tem 15 pipes no cabeçalho padrão (len == 16 ou 17 dependendo do separador)
        total_fields = len(fields)

        if total_fields >= 18:
            self.sped_type = "EFD_CONTRIBUICOES"
        elif total_fields in (16, 17):
            self.sped_type = "EFD_ICMS_IPI"
        else:
            self.sped_type = "DESCONHECIDO"

        if not self.enterprise_name and len(fields) > 6:
            self.enterprise_name = fields[6].strip()

        if len(fields) > 7:
            cnpj_raw = fields[7].strip()
            self.cnpj_emit = "".join(filter(str.isdigit, cnpj_raw))

    def _parse_C100(self, line: str) -> tuple:
        if line.startswith('|C100|'):
            fields = line.strip().split('|')
            if len(fields) < 3:
                return ()
                
            ind_oper = fields[2]
                    
            if ind_oper != '1':
                return ("Homologation",)

            nfe_model = int(fields[6].strip()) if len(fields) > 6 and fields[6].strip() else 55
            document_status = fields[7].strip() if len(fields) > 7 else ""
            nfe_key = fields[10].strip() if len(fields) > 10 else ""
        
            raw_date = fields[11].strip() if len(fields) > 11 else ""
            document_date = f"{raw_date[0:2]}-{raw_date[2:4]}-{raw_date[4:8]}" if len(raw_date) == 8 else "00-00-0000"
        
            raw_value = fields[13].strip() if len(fields) > 13 else ""
            document_raw_value = raw_value.replace(',', '.') if raw_value else '0'
            total_value = int(round(float(document_raw_value) * 100))

            return (nfe_model, document_status, nfe_key, document_date, total_value)
            
        return ()

    def _parse_sped(self) -> Generator[SpedDocument, None, None]:
        if self.fiscal_notes is None:
            self.fiscal_notes = []

        if not self.file_path or not self.file_path.exists():
            return

        with open(self.file_path, 'r', encoding='latin-1') as file:
            for line in file:
                line_str = line.strip()
                if not line_str:
                    continue

                if line_str.startswith('|0000|'):
                    self._parse_0000(line_str)

                elif line_str.startswith('|C100|'):
                    fields_C100 = self._parse_C100(line_str)
                    
                    if fields_C100 == ("Homologation",) or not fields_C100:
                        continue

                    nfe_model, document_status, access_key, emission_date, total_value = fields_C100

                    fiscal_note = SpedDocument(
                        access_key=access_key,
                        cnpj_emit=self.cnpj_emit,
                        total_value=total_value,
                        emission_date=emission_date,
                        nf_type=nfe_model,
                        situation_code=document_status,
                        sped_type=self.sped_type
                    )

                    self.fiscal_notes.append(fiscal_note.to_tuple())
                    yield fiscal_note

    def __enter__(self):
        list(self._parse_sped())
        return self

    def __exit__(self, exc_type, exc, tb):
        pass