import re
from lxml import etree


def parse_nfe_xml(file_path: str):
    tree = etree.parse(file_path)

    id_nf_list = tree.xpath("//*[local-name()='infNFe']/@Id")
    type_nf_list = tree.xpath("//*[local-name()='tpNF']/text()")

    if not id_nf_list or not type_nf_list:
        raise ValueError(
            f"Erro ao extrair informações do XML da NFe no arquivo: {file_path}"
        )

    nf_key = re.sub(r"\D", "", id_nf_list[0])

    if len(nf_key) != 44:
        raise ValueError(
            f"Chave de acesso inválida ({len(nf_key)} dígitos) no arquivo: {file_path}"
        )

    type_nf = int(type_nf_list[0])

    return (nf_key, type_nf)
