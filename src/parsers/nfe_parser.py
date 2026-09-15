import re
import lxml


def parse_nfe_xml(file_path: str):
    tree = lxml.etree.parse(file_path)

    id_nf_list = tree.xpath("//*[local-name()='infNFe']/@Id")
    type_nf_list = tree.xpath("//*[local-name()='tpNF']/text()")

    if not id_nf_list or not type_nf_list:
        raise ValueError(
            f"Erro ao extrair informações do XML da NFe no arquivo: {file_path} --xml_parser.py"
        )

    nfe = re.sub(r"\D", "", id_nf_list[0])

    if len(nfe) != 44:
        raise ValueError(
            f"Chave de acesso inválida ({len(nfe)} dígitos) no arquivo: {file_path} --xml_parser.py"
        )

    tpNF = int(type_nf_list[0])


    yield (
        nfe,
        tpNF
    )
