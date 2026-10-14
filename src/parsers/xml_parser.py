from pathlib import Path
import xml.etree.ElementTree as ET

from src.models.xml_model import XmlBaseModel


class XmlParser:

    PRODUCTION_ENVIRONMENT_CODE = "1"
    ACCESS_KEY_LENGTH = 44
    INVALID_OPERATION_TYPE = -1

    @staticmethod
    def _convert_to_cents(amount_str: str) -> int:
        if not amount_str:
            return 0
        try:
            amount_float = float(amount_str)
            return int(round(amount_float * 100))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _extract_tag_text(element: ET.Element, target_tag: str) -> str:
        for node in element.iter():
            if node.tag.rsplit("}", 1)[-1] == target_tag:
                return node.text or ""
        return ""

    @staticmethod
    def _find_element_by_tag(element: ET.Element, target_tag: str) -> ET.Element | None:
        for node in element.iter():
            if node.tag.rsplit("}", 1)[-1] == target_tag:
                return node
        return None

    @classmethod
    def list_xml_files(cls, directory: Path | str) -> list[Path]:
        directory_path = Path(directory)
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido ou inexistente: {directory}")

        return [
            file_path
            for file_path in directory_path.rglob("*")
            if file_path.is_file() and file_path.suffix.lower() == ".xml"
        ]

    @classmethod
    def parse_xml(cls, xml_path: Path | str) -> XmlBaseModel | None:
        file_path = Path(xml_path)

        if not file_path.exists() or file_path.stat().st_size == 0:
            return None

        try:
            tree = ET.parse(file_path)
            root_element = tree.getroot()
        except ET.ParseError:
            return None

        nfe_info_element = cls._find_element_by_tag(root_element, "infNFe")
        if nfe_info_element is None:
            return None

        environment_type = cls._extract_tag_text(nfe_info_element, "tpAmb")
        if environment_type != cls.PRODUCTION_ENVIRONMENT_CODE:
            return None

        raw_nfe_id = nfe_info_element.attrib.get("Id", "")
        access_key = raw_nfe_id.replace("NFe", "").strip()
        if len(access_key) != cls.ACCESS_KEY_LENGTH:
            return None

        issuer_cnpj = cls._extract_tag_text(nfe_info_element, "CNPJ")

        raw_emission_date = (
            cls._extract_tag_text(nfe_info_element, "dhEmi")
            or cls._extract_tag_text(nfe_info_element, "dEmi")
        )
        emission_date = raw_emission_date.split("T")[0] if raw_emission_date else ""

        raw_operation_type = cls._extract_tag_text(nfe_info_element, "tpNF")
        operation_type_number = (
            int(raw_operation_type)
            if raw_operation_type.isdigit()
            else cls.INVALID_OPERATION_TYPE
        )

        raw_total_amount = cls._extract_tag_text(nfe_info_element, "vNF")
        total_value_cents = cls._convert_to_cents(raw_total_amount)

        return XmlBaseModel(
            access_key=access_key,
            cnpj_issuer=issuer_cnpj,
            total_value=total_value_cents,
            emission_date=emission_date,
            document_status_number=operation_type_number,
        )
