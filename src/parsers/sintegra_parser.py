from pathlib import Path

from src.parsers.base_parser import FiscalDocumentBaseModelParser
from src.models.sintegra_model import SintegraBaseModel

class SintegraParser(FiscalDocumentBaseModelParser):

    def __init__(self, sintegra_path: Path):
        super().__init__(sintegra_path)

    def _parse_record_10(self, line_10: str) -> dict: 
        return {
            "company_name": line_10[30:64],
            "cnpj_issuer": line_10[2:15]
        }

    def _parse_record_50_51(self, line_50_51: str) -> dict:
        return {
            "emission_date": line_50_51[30:37],
            "operation_type_code": line_50_51[55],
            "total_value": line_50_51[56:68],
            "document_status_code": line_50_51[122]
        }

    def _parse_record_61(self, line_61: str) -> dict:
        return {
            "emission_date": line_61[30:37],
            "total_value": line_61[57:69]
        }

    def _parse_sintegra_file(self):
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
                        "model_code": "55",
                    }

            elif line.startswith("61"):
                parsed_61 = self._parse_record_61(line)
                if parsed_61:
                    document_data = {
                        "total_value": parsed_61.get("total_value"),
                        "emission_date": self._format_date(parsed_61.get("emission_date")),
                        "document_status_code": "N",
                        "operation_type_code": "T",
                        "model_code": "65",
                    }

            if not document_data or any(value is None for value in document_data.values()):
                continue

            sintegra_document = SintegraBaseModel(
                cnpj_issuer=self.cnpj_issuer,
                **document_data
            )

            yield sintegra_document.to_tuple()
