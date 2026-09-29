from pathlib import Path
from typing import Generator, Optional, Tuple, Union

from src.models.sped_document import SpedDocument


class SpedParser:
    ENCODINGS = ('utf-8', 'latin-1', 'utf-8-sig')

    def __init__(self, sped_file: Optional[Union[Path, str]]):
        self.file_path: Optional[Path] = Path(sped_file) if sped_file is not None else None
        self.enterprise_name: Optional[str] = None
        self.cnpj_emit: str = ""
        self.sped_type: str = "EFD_ICMS_IPI"

    def get_enterprise(self) -> str:
        return self.enterprise_name or "EMPRESA_DESCONHECIDA"

    def _read_lines(self) -> Generator[str, None, None]:
        if not self.file_path or not self.file_path.exists():
            return

        for encoding in self.ENCODINGS:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str:
                            yield line_str
                return
            except UnicodeDecodeError:
                continue

    def parse_metadata_only(self) -> None:
        for line in self._read_lines():
            if line.startswith('|0000|'):
                self._parse_0000(line)
                break

    def _parse_0000(self, line_0000: str) -> None:
        fields = line_0000.split('|')
        if len(fields) < 4 or fields[1] != '0000':
            return

        self.sped_type = "EFD_CONTRIBUICOES" if len(fields) >= 18 else "EFD_ICMS_IPI"

        if len(fields) > 6 and fields[6].strip():
            self.enterprise_name = fields[6].strip()

        if len(fields) > 7:
            self.cnpj_emit = "".join(filter(str.isdigit, fields[7].strip()))

    def _parse_C100(self, line: str) -> Optional[Tuple[int, str, str, str, int]]:
        fields = line.split('|')
        if len(fields) < 14 or fields[2] == "0":
            return None

        access_key = fields[9]
        if len(access_key) != 44:
            return None

        try:
            nfe_model = int(fields[5]) if fields[5] else 55
        except ValueError:
            nfe_model = 55

        document_status = fields[6] or "00"

        raw_date = fields[10]
        document_date = (
            f"{raw_date[4:8]}-{raw_date[2:4]}-{raw_date[0:2]}"
            if len(raw_date) == 8 else "1900-01-01"
        )

        raw_value = fields[12].replace(',', '.') if fields[12] else '0'
        try:
            total_value = int(round(float(raw_value) * 100))
        except ValueError:
            total_value = 0

        return nfe_model, document_status, access_key, document_date, total_value

    def parse_sped(self) -> Generator[Tuple, None, None]:
        for line in self._read_lines():
            if line.startswith('|0000|'):
                self._parse_0000(line)
            elif line.startswith('|C100|'):
                parsed_c100 = self._parse_C100(line)
                if not parsed_c100:
                    continue

                nfe_model, doc_status, access_key, emission_date, total_value = parsed_c100

                fiscal_note = SpedDocument(
                    access_key=access_key,
                    cnpj_emit=self.cnpj_emit,
                    total_value=total_value,
                    emission_date=emission_date,
                    nfe_model=nfe_model,
                    document_status=doc_status,
                    sped_type=self.sped_type,
                )
                yield fiscal_note.to_tuple()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass