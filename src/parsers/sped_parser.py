from typing import Generator
from pathlib import Path

from src.models.sped_document import SpedDocument

class SpedParser:
    fiscal_notes: list[tuple] | None
    cnpj_emit: str
    sped_type: str

    def __init__ (cls, sped_file: Path):
        cls.sped_file = sped_file

    @classmethod
    def _parse_0000(cls, line_0000: str):
        fields = line_0000.split('|')
        if len(fields) < 4 or fields[1] != '0000':
            cls.sped_type = "DESCONHECIDO"
        
        elif len(fields) == 16:
            cls.sped_type = "EFD_CONTRIBUICOES"

        elif len(fields) == 15:
            cls.sped_type = "EFD_ICMS_IPI"

        else: cls.sped_type = "DESCONHECIDO" 

        if len(fields) > 7:
            cnpj_raw = fields[7].strip()
            cls.cnpj_emit = "".join(filter(str.isdigit, cnpj_raw))

    @classmethod
    def _parse_C100(cls, line: str) -> tuple:
        cls.fiscal_notes = []
        if line.startswith('|C100|'):
            fields = line.split('|')
            ind_oper = fields[2]
                    
            if ind_oper != '1':
                return ("Homologation",)
        
            nfe_model = int(fields[5]) if fields[5] else 55
            document_status = fields[6]
            nfe_key = fields[9]
        
            raw_date = fields[10]
            document_date = f"{raw_date[0:2]}-{raw_date[2:4]}-{raw_date[4:8]}" if raw_date else "00-00-0000"
        
            document_raw_value = fields[12].replace(',', '.') if fields[12] else '0'
            total_value = int(round(float(document_raw_value) * 100))

            return (nfe_model, document_status, nfe_key, document_date, total_value)

    @classmethod
    def _parse_sped(cls) -> Generator[SpedDocument]:
        with open(cls.file_path, 'r', encoding='latin-1') as file:
            for line in file:
                if line.startswith('|0000|'):
                    cls.cnpj_emit = cls._parse_0000(1)
                    cls.sped_type = cls._parse_0000(0)

                elif line.startswith('|C100|'):
                    fields_C100 = cls._parse_C100(line)

                else: continue        

                acces_key = fields_C100[2]
                total_value = fields_C100[4]
                emission_date = fields_C100[3]
                nfe_model = fields_C100[0]
                document_status = fields_C100[1]

                fiscal_note =  SpedDocument(
                    access_key=acces_key,
                    cnpj_emit=cls.cnpj_emit,
                    total_value=total_value,
                    emission_date=emission_date,
                    nfe_model=nfe_model,
                    document_status=document_status,
                    sped_type=cls.sped_type
                )

                cls.fiscal_notes.append(fiscal_note.to_tuple())

    def __enter__(self):
        self._parse_sped()

    def __exit__(self, exc_type, exc, tb):
        self._clean_sped_document()
        
    def _clean_sped_document(cls):
        cls.fiscal_notes = None
        cls.sped_dir = None
        
        cls.cnpj_emit = ""
        cls.sped_type = ""