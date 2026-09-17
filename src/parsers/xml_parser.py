import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from src.models.Fiscal_document import FiscalDocument

class XmlParser:

    @staticmethod
    def _to_centavos(value_str: str) -> int:
        if not value_str:
            return 0
        return int(round(float(value_str) * 100))

    @staticmethod
    def get_xml_files(directory_path: Path) -> Iterator[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {directory_path}")

        return directory_path.rglob("*.xml")

    @classmethod
    def parse(cls, file_path: Path | str) -> Iterator[FiscalDocument]:
        context = ET.iterparse(file_path, events=("start", "end"))
        context = iter(context)
        
        try:
            _, root = next(context)
        except StopIteration:
            return

        doc_data = cls._get_empty_doc_data()
        in_emit = False

        for event, elem in context:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if event == "start":
                if tag_name == "emit":
                    in_emit = True

            elif event == "end":
                if tag_name == "infNFe":
                    doc_data["access_key"] = elem.attrib.get("Id", "").replace("NFe", "")

                elif tag_name == "tpAmb":
                    doc_data["tp_amb"] = elem.text.strip() if elem.text else None

                elif tag_name in ("dhEmi", "dEmi"):
                    doc_data["emission_date"] = elem.text[:10] if elem.text else ""

                elif tag_name == "emit":
                    in_emit = False

                elif tag_name == "CNPJ" and in_emit:
                    doc_data["cnpj_emit"] = elem.text.strip() if elem.text else ""

                elif tag_name == "vNF":
                    if elem.text:
                        doc_data["total_value"] = cls._to_centavos(elem.text.strip())

                elif tag_name == "NFe":
                    key = doc_data["access_key"]

                    if doc_data["tp_amb"] == "1" and key and len(key) == 44:
                        yield FiscalDocument(
                            access_key=key,
                            cnpj_emit=doc_data["cnpj_emit"],
                            total_value=doc_data["total_value"],
                            emission_date=doc_data["emission_date"],
                            nf_type=1,
                            situation_code="00"
                        )

                    doc_data = cls._get_empty_doc_data()

                    root.clear()

                elem.clear()

    @staticmethod
    def _get_empty_doc_data() -> dict:
        return {
            "access_key": None,
            "tp_amb": None,
            "emission_date": "",
            "total_value": 0,
            "cnpj_emit": "",
        }