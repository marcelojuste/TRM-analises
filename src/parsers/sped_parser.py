from typing import Generator
from pathlib import Path

from src.models.sped_document import SpedDocument


class SpedParser:
    def __init__(self, sped_file: Path):
        self.sped_file = Path(sped_file)
        self.file_path = Path(sped_file)
        self.enterprise_name: str | None = None
        self.fiscal_notes: list[tuple] = []
        self.cnpj_emit: str = ""
        self.sped_type: str = "EFD_ICMS_IPI"

    def get_enterprise(self):
        return self.enterprise_name or "EMPRESA_DESCONHECIDA"

    def _parse_0000(self, line_0000: str):
        fields = line_0000.strip().split('|')

        if len(fields) < 4 or fields[1] != '0000':
            return

        total_fields = len(fields)

        if total_fields >= 18:
            self.sped_type = "EFD_CONTRIBUICOES"
        else:
            self.sped_type = "EFD_ICMS_IPI"

        if len(fields) > 6 and fields[6].strip():
            self.enterprise_name = fields[6].strip()

        if len(fields) > 7:
            cnpj_raw = fields[7].strip()
            self.cnpj_emit = "".join(filter(str.isdigit, cnpj_raw))

    def _parse_C100(self, line: str) -> tuple:
        fields = line.strip().split('|')

        if len(fields) < 14:
            return ()

        try:
            nfe_model = int(fields[5].strip()) if fields[5].strip() else 55
        except ValueError:
            nfe_model = 55

        document_status = fields[6].strip() if len(fields) > 6 else "00"

        access_key = fields[9].strip() if len(fields) > 9 else ""

        if len(access_key) != 44:
            return ()

        raw_date = fields[10].strip() if len(fields) > 10 else ""
        if len(raw_date) == 8:
            document_date = f"{raw_date[4:8]}-{raw_date[2:4]}-{raw_date[0:2]}"
        else:
            document_date = "1900-01-01"

        raw_value = fields[12].strip() if len(fields) > 12 else "0"
        document_raw_value = raw_value.replace(',', '.') if raw_value else '0'
        
        try:
            total_value = int(round(float(document_raw_value) * 100))
        except ValueError:
            total_value = 0

        return (nfe_model, document_status, access_key, document_date, total_value)

    def _parse_sped(self) -> Generator[SpedDocument, None, None]:
        self.fiscal_notes = []

        if not self.file_path or not self.file_path.exists():
            return

        lines = []
        for encoding in ['latin-1', 'utf-8', 'utf-8-sig']:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except (UnicodeDecodeError, Exception):
                continue

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.startswith('|0000|'):
                self._parse_0000(line_str)

            elif line_str.startswith('|C100|'):
                parsed_c100 = self._parse_C100(line_str)
                if not parsed_c100:
                    continue

                nfe_model, document_status, access_key, emission_date, total_value = parsed_c100

                fiscal_note = SpedDocument(
                    access_key=access_key,
                    cnpj_emit=self.cnpj_emit,
                    total_value=total_value,
                    emission_date=emission_date,
                    nfe_model=nfe_model,
                    document_status=document_status,
                    sped_type=self.sped_type
                )

                self.fiscal_notes.append(fiscal_note.to_tuple())
                yield fiscal_note

    def __enter__(self):
        list(self._parse_sped())
        return self

    def __exit__(self, exc_type, exc, tb):
        pass