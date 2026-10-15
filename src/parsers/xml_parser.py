import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Generator, List, Optional

from src.models.xml_model import XmlBaseModel
from src.parsers.base_parser import FiscalDocumentBaseModelParser


class XmlParser(FiscalDocumentBaseModelParser):

    PRODUCTION_ENVIRONMENT_CODE = "1"
    ACCESS_KEY_LENGTH = 44
    INVALID_OPERATION_TYPE = -1

    def __init__(self, xml_path: Optional[Path] = None):
        super().__init__(xml_path)

    @staticmethod
    def _extract_tag_text(element: ET.Element, target_tag: str) -> str:
        for node in element.iter():
            if node.tag.rsplit("}", 1)[-1] == target_tag:
                return node.text or ""
        return ""

    @staticmethod
    def _find_element_by_tag(element: ET.Element, target_tag: str) -> Optional[ET.Element]:
        for node in element.iter():
            if node.tag.rsplit("}", 1)[-1] == target_tag:
                return node
        return None

    def parse_xml(self, xml_path: Optional[Path] = None) -> Generator[tuple[str, str, int, str, int], None, None] | None:
        file_path = xml_path or self.file_path
        if not file_path or not file_path.exists() or file_path.stat().st_size == 0:
            return None

        try:
            tree = ET.parse(file_path)
            root_element = tree.getroot()
        except ET.ParseError:
            return None

        nfe_info_element = self._find_element_by_tag(root_element, "infNFe")
        if nfe_info_element is None:
            return None

        environment_type = self._extract_tag_text(nfe_info_element, "tpAmb")
        if environment_type != self.PRODUCTION_ENVIRONMENT_CODE:
            return None

        raw_nfe_id = nfe_info_element.attrib.get("Id", "")
        access_key = raw_nfe_id.replace("NFe", "").strip()
        if len(access_key) != self.ACCESS_KEY_LENGTH:
            return None

        issuer_cnpj = self._extract_tag_text(nfe_info_element, "CNPJ")

        raw_emission_date = (
            self._extract_tag_text(nfe_info_element, "dhEmi")
            or self._extract_tag_text(nfe_info_element, "dEmi")
        )
        emission_date = raw_emission_date.split("T")[0] if raw_emission_date else ""

        raw_operation_type = self._extract_tag_text(nfe_info_element, "tpNF")
        operation_type_number = (
            int(raw_operation_type)
            if raw_operation_type.isdigit()
            else self.INVALID_OPERATION_TYPE
        )

        raw_total_amount = self._extract_tag_text(nfe_info_element, "vNF")
        total_value_cents = self._convert_to_cents(raw_total_amount)

        xml_document = XmlBaseModel(
            access_key=access_key,
            cnpj_issuer=issuer_cnpj,
            total_value=total_value_cents,
            emission_date=emission_date,
            document_status_number=operation_type_number,
        )

        yield xml_document.to_tuple()