from pathlib import Path
from typing import Generator, Optional

from src.models.sintegra_model import SintegraModel
from src.parsers.base_parser import FiscalDocumentBaseModelParser

class SintegraParser(FiscalDocumentBaseModelParser):

    def __init__(self, sintegra_path: Optional[Path] = None):
        super().__init__(sintegra_path)
        self.cnpj_issuer: Optional[str] = None

    @staticmethod
    def _format_date(raw_date: str) -> str:
        if len(raw_date) == 8 and raw_date.isdigit():
            year, month, day = raw_date[0:4], raw_date[4:6], raw_date[6:8]
            return f"{year}-{month}-{day}"
        return "1900-01-01"

    def _parse_record_10(self, line_10: str) -> Optional[dict]:
        if len(line_10) < 126 or not line_10.startswith("10"):
            return None

        return {
            "company_name": line_10[30:65].strip(),
            "cnpj_issuer": line_10[2:16].strip(),
        }

    def _parse_record_50(self, line_50: str) -> Optional[dict]:
        if len(line_50) < 126 or not line_50.startswith(("50", "51")):
            return None

        raw_doc_number = line_50[45:51].strip()
        cfop = line_50[51:55].strip()
        emitente_code = line_50[55:56].strip()
        raw_value = line_50[56:69].strip()
        status_code = line_50[125:126].strip()

        if emitente_code:
            operation_type_code = emitente_code
        elif cfop and len(cfop) > 0:
            operation_type_code = "P" if cfop[0] in ("5", "6", "7") else "T"
        else:
            operation_type_code = "P"

        total_value_cents = int(raw_value) if raw_value.isdigit() else 0

        return {
            "emission_date": line_50[30:38].strip(),
            "operation_type_code": operation_type_code,
            "total_value": total_value_cents,
            "document_status_code": status_code,
            "document_number": int(raw_doc_number) if raw_doc_number.isdigit() else None,
        }

    def _parse_record_61(self, line_61: str) -> Optional[dict]:
        if len(line_61) < 119 or not line_61.startswith("61"):
            return None

        raw_value = line_61[57:70].strip()
        raw_start_num = line_61[38:44].strip()

        return {
            "emission_date": line_61[30:38].strip(),
            "total_value": int(raw_value) if raw_value.isdigit() else 0,
            "document_number": int(raw_start_num) if raw_start_num.isdigit() else None,
        }

    def parse_sintegra(self) -> Generator[tuple, None, None]:
        parsed_10 = None

        for line in self._read_lines():
            if line.startswith("10"):
                parsed_10 = self._parse_record_10(line)
                if parsed_10:
                    self.company_name = parsed_10.get("company_name")
                    self.cnpj_issuer = parsed_10.get("cnpj_issuer")
                continue

            if not parsed_10 or not self.cnpj_issuer:
                continue

            document_data = None

            if line.startswith(("50", "51")):
                parsed_50 = self._parse_record_50(line)
                if parsed_50:
                    document_data = {
                        "total_value": parsed_50.get("total_value"),
                        "emission_date": self._format_date(parsed_50.get("emission_date")),
                        "document_status_code": parsed_50.get("document_status_code"),
                        "operation_type_code": parsed_50.get("operation_type_code"),
                        "document_number": parsed_50.get("document_number"),
                        "model_code": "55",
                    }

            elif line.startswith("61"):
                parsed_61 = self._parse_record_61(line)
                if parsed_61:
                    document_data = {
                        "total_value": parsed_61.get("total_value"),
                        "emission_date": self._format_date(parsed_61.get("emission_date")),
                        "document_status_code": "N",
                        "operation_type_code": "P",
                        "document_number": parsed_61.get("document_number"),
                        "model_code": "65",
                    }

            if not document_data or any(value is None for value in [document_data.get("total_value"), document_data.get("emission_date")]):
                continue

            sintegra_document = SintegraModel(
                cnpj_issuer=self.cnpj_issuer,
                **document_data
            )

            yield sintegra_document.to_tuple()