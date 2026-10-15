import re
from pathlib import Path
from typing import Generator, Optional, Tuple

from src.parsers.xml_parser import XmlParser
from src.models.sped_model import SpedBaseModel


class SpedParser(XmlParser):

    RECORD_DELIMITER = "|"

    def __init__(self, sped_path: Path):
        super().__init__(sped_path)

    def _read_lines(self) -> Generator[str, None, None]:
        if not self.file_path or not self.file_path.exists():
            return

        encoding = self._detect_encoding()
        with open(self.file_path, "r", encoding=encoding, errors="replace") as file_stream:
            for line in file_stream:
                stripped_line = line.strip()
                if stripped_line:
                    yield stripped_line

    def _parse_metadata_only(self) -> None:
        for line in self._read_lines():
            if line.startswith(f"{self.RECORD_DELIMITER}0000{self.RECORD_DELIMITER}"):
                self._parse_record_0000(line)
                break

    def _parse_record_0000(self, line_0000: str) -> Optional[dict]:
        fields = line_0000.split(self.RECORD_DELIMITER)
        if len(fields) < 4 or fields[1] != "0000":
            return None

        company_name = ""
        if len(fields) > 6 and fields[6].strip():
            company_name = fields[6].strip()

        issuer_cnpj = ""
        if len(fields) > 7:
            issuer_cnpj = re.sub(r"\D", "", fields[7].strip())

        return {
            "fields": len(fields),
            "company_name": company_name,
            "issuer_cnpj": issuer_cnpj,
        }

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
        emission_date = self._format_date(fields[10])
        total_value_cents = self._convert_to_cents(fields[12])

        return {
            "nfe_model": nfe_model,
            "document_status": document_status,
            "access_key": access_key,
            "emission_date": emission_date,
            "total_value": total_value_cents,
        }

    def parse_sped(self) -> Generator[Tuple, None, None]:
        parsed_0000 = None
        sped_number_fields: int = 0

        for line in self._read_lines():
            if line.startswith(f"{self.RECORD_DELIMITER}0000{self.RECORD_DELIMITER}"):
                parsed_0000 = self._parse_record_0000(line)
                if parsed_0000:
                    self.company_name = parsed_0000["company_name"]
                    sped_number_fields = parsed_0000["fields"]
            elif line.startswith(f"{self.RECORD_DELIMITER}C100{self.RECORD_DELIMITER}"):
                parsed_c100 = self._parse_record_c100(line)
                if not parsed_c100 or not parsed_0000:
                    continue

                sped_document = SpedBaseModel(
                    sped_number_fields=sped_number_fields,
                    access_key=parsed_c100["access_key"],
                    cnpj_issuer=parsed_0000["issuer_cnpj"],
                    total_value=parsed_c100["total_value"],
                    emission_date=parsed_c100["emission_date"],
                    document_status_number=parsed_c100["document_status"]
                )

                yield sped_document.to_tuple()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass