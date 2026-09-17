import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from src.models.fiscal_document import FiscalDocument

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

        # CORREÇÃO: Removemos o list() em volta do rglob. 
        # O rglob retorna um gerador, que não consome memória RAM iterando pastas enormes.
        return directory_path.rglob("*.xml")

    @classmethod
    def parse(cls, file_path: Path | str) -> Iterator[FiscalDocument]:
        # CORREÇÃO: Adicionamos o evento "start" para sabermos quando entramos em uma tag
        context = ET.iterparse(file_path, events=("start", "end"))
        context = iter(context)
        
        try:
            # Pegamos o elemento raiz (root) do XML. Ele é a chave para não vazar memória.
            _, root = next(context)
        except StopIteration:
            return # Arquivo XML vazio

        doc_data = cls._get_empty_doc_data()
        in_emit = False # Movemos a flag para fora do dicionário para controle de estado

        for event, elem in context:
            # Remove namespaces (ex: {http://www.portalfiscal...}infNFe -> infNFe)
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            # EVENTO START: A tag abriu (ex: <emit>)
            if event == "start":
                if tag_name == "emit":
                    in_emit = True # Entramos no bloco do emitente!
                    
            # EVENTO END: A tag fechou (ex: </emit> ou </CNPJ>)
            # É apenas no fechamento que temos garantia de que o elem.text e elem.attrib foram lidos inteiros
            elif event == "end":
                if tag_name == "infNFe":
                    doc_data["access_key"] = elem.attrib.get("Id", "").replace("NFe", "")

                elif tag_name == "tpAmb":
                    doc_data["tp_amb"] = elem.text.strip() if elem.text else None

                elif tag_name in ("dhEmi", "dEmi"): # in permite checar NFe 3.10 e 4.00
                    doc_data["emission_date"] = elem.text[:10] if elem.text else ""

                elif tag_name == "emit":
                    in_emit = False # Saímos do bloco do emitente

                elif tag_name == "CNPJ" and in_emit:
                    doc_data["cnpj_emit"] = elem.text.strip() if elem.text else ""

                elif tag_name == "vNF":
                    if elem.text:
                        doc_data["total_value"] = cls._to_centavos(elem.text.strip())

                elif tag_name == "NFe":
                    key = doc_data["access_key"]

                    # Valida apenas ambiente de produção (1) com chave válida de 44 dígitos
                    if doc_data["tp_amb"] == "1" and key and len(key) == 44:
                        yield FiscalDocument(
                            access_key=key,
                            cnpj_emit=doc_data["cnpj_emit"],
                            total_value=doc_data["total_value"],
                            emission_date=doc_data["emission_date"],
                            nf_type=1,
                            situation_code="00"
                        )

                    # Reseta o dicionário para a próxima nota (se for um arquivo de lote nfeProc)
                    doc_data = cls._get_empty_doc_data()

                    # CORREÇÃO VITAL DE MEMÓRIA:
                    # Ao fechar a tag <NFe>, nós limpamos todos os filhos pendurados no root
                    # Isso garante que a memória seja esvaziada a cada nota processada
                    root.clear()

                # Limpa a "casca" do elemento atual para poupar memória da iteração
                elem.clear()

    @staticmethod
    def _get_empty_doc_data() -> dict:
        # Extraído para um método para manter o código limpo ao resetar
        return {
            "access_key": None,
            "tp_amb": None,
            "emission_date": "",
            "total_value": 0,
            "cnpj_emit": "",
        }