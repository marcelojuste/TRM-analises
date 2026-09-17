import xml.etree.ElementTree as ET
from typing import Iterator
from pathlib import Path

from src.models.fiscal_document import FiscalDocument
from src.repositories.fiscal_repository import FISCAL_REPOSITORY

class XmlParser:

    def _to_centavos(value_str: str) -> int:
        if not value_str:
            return 0
        return int(round(float(value_str) * 100))

    def _get_xml(directory_path: Path) -> list:
        if not directory_path.exists() or not directory_path.is_dir():
            return FileNotFoundError(f"Diretorio inválido: {directory_path}")

        pattern = "*xml"
        xml_files = list(directory_path.rglob(pattern))

        if not xml_files:
            return FileNotFoundError(f"Nenhum arquivo XML encontrado no diretório: {directory_path}")

        return xml_files

    def parse(file_path: str) -> Iterator[FiscalDocument]:
        context = ET.iterparse(file_path, events=("end",))
        _, root = next(context)

        doc_data = {
            "access_key": None,
            "tp_amb": None,
            "emission_date": "",
            "exit_date": "",
            "recipient_cnpj": "",
            "total_value": 0,
            "in_dest": False,
        }

        handlers = {
            "infNFe": lambda e: doc_data.update(
                access_key=e.attrib.get("Id", "").replace("NFe", "")
            ),
            "tpAmb": lambda e: doc_data.update(tp_amb=e.text.strip() if e.text else None),
            "dhEmi": lambda e: doc_data.update(
                emission_date=e.text[:10] if e.text else ""
            ),
            "dhSaiEnt": lambda e: doc_data.update(
                exit_date=e.text[:10] if e.text else ""
            ),
            "dSaiEnt": lambda e: doc_data.update(
                exit_date=e.text[:10] if e.text else ""
            ),
            "dest": lambda e: doc_data.update(in_dest=True),
            "CNPJ": lambda e: doc_data.update(
                recipient_cnpj=e.text.strip(), in_dest=False
            ) if doc_data["in_dest"] and e.text else None,
            "vNF": lambda e: doc_data.update(
                total_value=cls._to_cents(e.text.strip())
            ) if e.text else None,
        }

        for _event, elem in context:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if handler := handlers.get(tag_name):
                handler(elem)

            elif tag_name == "NFe":
                key = doc_data["access_key"]
                
                if doc_data["tp_amb"] == "1" and key:
                    if len(key) != 44:
                        raise ValueError(f"Chave de acesso inválida ({len(key)} dígitos): {file_path}")

                    xml = FiscalDocument(
                        access_key=key,
                        total_value=doc_data["total_value"],
                        emission_date=doc_data["emission_date"],
                        recipient_cnpj=doc_data["recipient_cnpj"],
                    )

                    FISCAL_REPOSITORY.xml_batch.append(
                        xml.to_tuple()
                    )

                doc_data = {k: 0 if k == "total_value" else ("" if "date" in k or "cnpj" in k else None) for k in doc_data}
                doc_data["in_dest"] = False

                elem.clear()
                root.clear()
