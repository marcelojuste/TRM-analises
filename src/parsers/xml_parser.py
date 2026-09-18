import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Iterator

from src.models.fiscal_document import FiscalDocument

class XmlParser:

    @staticmethod
    def get_xml_files(directory_path: Path) -> Iterator[Path]:
        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {directory_path}")

        return directory_path.rglob("*.xml")

    @classmethod
    def parse_xml(xml_path: str) -> FiscalDocument | None:
        context = ET.iterparse(xml_path, events=('end',))
        _, root = next(context)

        doc_data = {}
        for event, elem in context:
            tag = elem.tag.split('}')[-1]
            
            if tag == 'tpNF':
                if elem.text != '1':
                    root.clear()
                    return None
            elif tag == 'infNFe':
                doc_data['access_key'] = elem.attrib.get('Id', '').replace('NFe', '')
            elif tag == 'CNPJ' and 'cnpj_emit' not in doc_data:
                doc_data['cnpj_emit'] = elem.text
            elif tag == 'dhEmi' or tag == 'dEmi':
                raw_date = elem.text.split('T')[0]
                doc_data['emission_date'] = raw_date
            elif tag == 'mod':
                doc_data['nf_type'] = int(elem.text)
            elif tag == 'vNF':
                doc_data['total_value'] = int(round(float(elem.text) * 100))
            elif tag == 'cSitNFe':
                doc_data['situation_code'] = elem.text

            elem.clear()
        root.clear()

        if 'access_key' in doc_data:
            return FiscalDocument(
                access_key=doc_data['access_key'],
                cnpj_emit=doc_data['cnpj_emit'],
                total_value=doc_data.get('total_value', 0),
                emission_date=doc_data['emission_date'],
                nf_type=doc_data['nf_type'],
                situation_code=doc_data.get('situation_code', '00')
            )
        
        return None