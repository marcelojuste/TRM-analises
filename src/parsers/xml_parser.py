import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from src.models.fiscal_document import FiscalDocument


class XmlParser:

    @staticmethod
    def _to_centavos(val: str | None) -> int:
        if not val:
            return 0
        try:
            return int(round(float(val) * 100))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def get_xml_files(directory_path: Path) -> Iterator[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {directory_path}")

        return directory_path.rglob("*.xml")

    @staticmethod
    def parse_xml(xml_path: Path | str) -> FiscalDocument | None:
        xml_path = Path(xml_path)

        if not xml_path.exists() or xml_path.stat().st_size == 0:
            return None

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError:
            return None

        def find_text(elem, tag_name: str) -> str:
            for node in elem.iter():
                if node.tag.split("}")[-1] == tag_name:
                    return node.text or ""
            return ""

        def find_elem(elem, tag_name: str):
            for node in elem.iter():
                if node.tag.split("}")[-1] == tag_name:
                    return node
            return None

        inf_nfe = find_elem(root, "infNFe")
        if inf_nfe is None:
            return None

        tp_amb = find_text(inf_nfe, "tpAmb")
        if tp_amb != "1":
            return None

        raw_id = inf_nfe.attrib.get("Id", "")
        access_key = raw_id.replace("NFe", "").strip()
        if len(access_key) != 44:
            return None

        cnpj_emit = find_text(inf_nfe, "CNPJ")
        
        raw_date = find_text(inf_nfe, "dhEmi") or find_text(inf_nfe, "dEmi")
        emission_date = raw_date.split("T")[0] if raw_date else ""

        mod_val = find_text(inf_nfe, "mod")
        nf_type = int(mod_val) if mod_val.isdigit() else 1

        v_nf = find_text(inf_nfe, "vNF")
        total_value = XmlParser._to_centavos(v_nf)

        situation_code = find_text(inf_nfe, "cSitNFe") or "00"

        return FiscalDocument(
            access_key=access_key,
            cnpj_emit=cnpj_emit,
            total_value=total_value,
            emission_date=emission_date,
            nf_type=nf_type,
            situation_code=situation_code,
        )