import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Generator, Optional

from src.models.xml_model import XmlModel
from src.parsers.base_parser import FiscalDocumentBaseModelParser


class XmlParser(FiscalDocumentBaseModelParser):

    PRODUCTION_ENVIRONMENT_CODE = "1"
    ACCESS_KEY_LENGTH = 44
    INVALID_OPERATION_TYPE = -1

    def __init__(self, xml_path: Optional[Path] = None, **kwargs):
        super().__init__(xml_path, **kwargs)
        self.file_path = xml_path

    @staticmethod
    def _extract_tag_text(element: ET.Element, target_tag: str) -> str:
        for node in element.iter():
            if isinstance(node.tag, str) and node.tag.rsplit("}", 1)[-1] == target_tag:
                return node.text or ""
        return ""

    @staticmethod
    def _find_element_by_tag(element: ET.Element, target_tag: str) -> Optional[ET.Element]:
        for node in element.iter():
            if isinstance(node.tag, str) and node.tag.rsplit("}", 1)[-1] == target_tag:
                return node
        return None

    def parse_xml(self) -> Generator[tuple, None, None]:
        if not self.file_path or not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return

        try:
            tree = ET.parse(self.file_path)
            root_element = tree.getroot()
        except ET.ParseError:
            return

        nfe_info_element = self._find_element_by_tag(root_element, "infNFe")
        if nfe_info_element is None:
            return

        environment_type = self._extract_tag_text(nfe_info_element, "tpAmb")
        if environment_type != self.PRODUCTION_ENVIRONMENT_CODE:
            return

        raw_nfe_id = nfe_info_element.attrib.get("Id", "")
        access_key = raw_nfe_id.replace("NFe", "").strip()
        if len(access_key) != self.ACCESS_KEY_LENGTH:
            return

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

        xml_document = XmlModel(
            access_key=access_key,
            cnpj_issuer=issuer_cnpj,
            total_value=total_value_cents,
            emission_date=emission_date,
            document_status_number=operation_type_number,
        )

        yield xml_document.to_tuple()