import re
import xml.etree.ElementTree as ET
from typing import Tuple

def parse_nfe_xml(file_path: str) -> Tuple[str, int]:
    nfe_key: str | None = None
    tp_nf: int | None = None

    context = ET.iterparse(file_path, events=("end",))

    for _event, elem in context:
        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag_name == "infNFe" and nfe_key is None:
            raw_id = elem.attrib.get("Id", "")
            cleaned_id = re.sub(r"\D", "", raw_id)
            if cleaned_id:
                nfe_key = cleaned_id

        elif tag_name == "tpNF" and tp_nf is None:
            if elem.text and elem.text.strip().isdigit():
                tp_nf = int(elem.text.strip())

        elem.clear()

    if not nfe_key or tp_nf is None:
        raise ValueError(
            f"Erro ao extrair informações do XML da NFe no arquivo: {file_path} -- nfe_parser.py"
        )

    if len(nfe_key) != 44:
        raise ValueError(
            f"Chave de acesso inválida ({len(nfe_key)} dígitos) no arquivo: {file_path} -- nfe_parser.py"
        )

    return nfe_key, tp_nf
