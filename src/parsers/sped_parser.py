from pathlib import Path
from typing import Generator, Optional, Tuple, Union

from src.models.sped_model import SpedBaseModel


class SpedParser:

    SUPPORTED_ENCODINGS = ("utf-8", "latin-1", "utf-8-sig")
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_FALLBACK_ENCODING = "latin-1"
    RECORD_DELIMITER = "|"
    BUFFER_SIZE_BYTES = 4096

    def __init__(self, sped_file: Optional[Union[Path, str]]):
        self.file_path: Optional[Path] = Path(sped_file) if sped_file is not None else None
        self.company_name: Optional[str] = None
        self.issuer_cnpj: str = ""
        self.sped_type: str = "EFD_ICMS_IPI"
        self._detected_encoding: Optional[str] = None

    def get_enterprise(self) -> str:
        return self.company_name or "EMPRESA_DESCONHECIDA"

    def _detect_encoding(self) -> str:
        if self._detected_encoding:
            return self._detected_encoding

        if not self.file_path or not self.file_path.exists():
            return self.DEFAULT_ENCODING

        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                with open(self.file_path, "r", encoding=encoding) as file_stream:
                    file_stream.read(self.BUFFER_SIZE_BYTES)
                self._detected_encoding = encoding
                return encoding
            except UnicodeDecodeError:
                continue

        self._detected_encoding = self.DEFAULT_FALLBACK_ENCODING
        return self._detected_encoding

    def _read_lines(self) -> Generator[str, None, None]:
        if not self.file_path or not self.file_path.exists():
            return

        encoding = self._detect_encoding()
        with open(self.file_path, "r", encoding=encoding, errors="replace") as file_stream:
            for line in file_stream:
                stripped_line = line.strip()
                if stripped_line:
                    yield stripped_line

    @staticmethod
    def _format_sped_date(raw_date: str) -> str:
        if len(raw_date) == 8 and raw_date.isdigit():
            day, month, year = raw_date[0:2], raw_date[2:4], raw_date[4:8]
            return f"{year}-{month}-{day}"
        return "1900-01-01"

    @staticmethod
    def _convert_to_cents(raw_value: str) -> int:
        if not raw_value:
            return 0
        try:
            normalized_value = raw_value.replace(",", ".")
            return int(round(float(normalized_value) * 100))
        except (ValueError, TypeError):
            return 0

    def parse_metadata_only(self) -> None:
        for line in self._read_lines():
            if line.startswith(f"{self.RECORD_DELIMITER}0000{self.RECORD_DELIMITER}"):
                self._parse_record_0000(line)
                break

    def _parse_record_0000(self, line_0000: str) -> None:
        fields = line_0000.split(self.RECORD_DELIMITER)
        if len(fields) < 4 or fields[1] != "0000":
            return

        self.sped_type = "EFD_CONTRIBUICOES" if len(fields) >= 18 else "EFD_ICMS_IPI"

        if len(fields) > 6 and fields[6].strip():
            self.company_name = fields[6].strip()

        if len(fields) > 7:
            self.issuer_cnpj = "".join(filter(str.isdigit, fields[7].strip()))

    def _parse_record_c100(self, line: str) -> Optional[dict]:
        fields = line.split(self.RECORD_DELIMITER)

        if len(fields) < 14:
            return None

        operation_type = fields[2]
        if operation_type == "0":
            return None

        access_key = fields[9]
        if len(access_key) != 44:
            return None

        try:
            nfe_model = int(fields[5]) if fields[5] else 55
        except ValueError:
            nfe_model = 55

        document_status = fields[6] or "00"
        emission_date = self._format_sped_date(fields[10])
        total_value_cents = self._convert_to_cents(fields[12])

        return {
            "nfe_model": nfe_model,
            "document_status": document_status,
            "access_key": access_key,
            "emission_date": emission_date,
            "total_value": total_value_cents,
        }

    def parse_sped(self) -> Generator[Tuple, None, None]:
        for line in self._read_lines():
            if line.startswith(f"{self.RECORD_DELIMITER}0000{self.RECORD_DELIMITER}"):
                self._parse_record_0000(line)
            elif line.startswith(f"{self.RECORD_DELIMITER}C100{self.RECORD_DELIMITER}"):
                parsed_c100 = self._parse_record_c100(line)
                if not parsed_c100:
                    continue

                fiscal_document = SpedBaseModel(
                    sped_number_fields=18 if self.sped_type == "EFD_CONTRIBUICOES" else 1,
                    access_key=parsed_c100["access_key"],
                    cnpj_issuer=self.issuer_cnpj,
                    total_value=parsed_c100["total_value"],
                    emission_date=parsed_c100["emission_date"],
                    document_status_number=1,  # 1 para Saída
                )
                yield fiscal_document.to_tuple()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass