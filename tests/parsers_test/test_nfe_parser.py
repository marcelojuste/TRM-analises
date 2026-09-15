import pytest
from lxml import etree
from src.parsers.nfe_parser import parse_nfe_xml

@pytest.fixture
def create_xml_file(tmp_path):
    """Auxiliar para gerar arquivos XML temporários."""
    def _create(content: str):
        file_path = tmp_path / "nfe_test.xml"
        file_path.write_text(content, encoding="utf-8")
        return file_path
    return _create


def test_parse_nfe_xml_success(create_xml_file):
    """Valida a extração correta da chave de 44 dígitos e a conversão do tpNF para inteiro."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
      <NFe>
        <infNFe Id="NFe35260912345678000195550010000001001234567890">
          <ide><tpNF>1</tpNF></ide>
        </infNFe>
      </NFe>
    </nfeProc>"""
    
    file_path = create_xml_file(xml_content)
    nfe, tp_nf = parse_nfe_xml(file_path)

    assert nfe == "35260912345678000195550010000001001234567890"
    assert tp_nf == 1
    assert isinstance(tp_nf, int)


def test_parse_nfe_xml_strips_non_digits_from_id(create_xml_file):
    """Garante que prefixos como 'NFe' sejam removidos via expressão regular."""
    xml_content = """<infNFe Id="NFe11223344556677889900112233445566778899001122"><tpNF>0</tpNF></infNFe>"""
    
    file_path = create_xml_file(xml_content)
    nfe, tp_nf = parse_nfe_xml(file_path)

    assert nfe == "11223344556677889900112233445566778899001122"
    assert tp_nf == 0

def test_parse_nfe_xml_missing_infnfe_id_raises_value_error(create_xml_file):
    """Dispara ValueError quando a tag infNFe não possui a propriedade Id."""
    xml_content = """<NFe><infNFe><tpNF>1</tpNF></infNFe></NFe>"""
    file_path = create_xml_file(xml_content)

    with pytest.raises(ValueError, match="Erro ao extrair informações do XML"):
        parse_nfe_xml(file_path)


def test_parse_nfe_xml_missing_tpnf_raises_value_error(create_xml_file):
    """Dispara ValueError quando a tag tpNF não está presente no documento."""
    xml_content = """<infNFe Id="NFe35260912345678000195550010000001001234567890"></infNFe>"""
    file_path = create_xml_file(xml_content)

    with pytest.raises(ValueError, match="Erro ao extrair informações do XML"):
        parse_nfe_xml(file_path)


def test_parse_nfe_xml_invalid_key_length_raises_value_error(create_xml_file):
    """Dispara ValueError se a chave numérica tiver tamanho diferente de 44 dígitos."""
    xml_content = """<infNFe Id="NFe12345"><tpNF>1</tpNF></infNFe>"""
    file_path = create_xml_file(xml_content)

    with pytest.raises(ValueError, match="Chave de acesso inválida \(5 dígitos\)"):
        parse_nfe_xml(file_path)


def test_parse_nfe_xml_non_numeric_tpnf_raises_value_error(create_xml_file):
    """Dispara ValueError na conversão int() se tpNF contiver um valor não numérico."""
    xml_content = """<infNFe Id="NFe35260912345678000195550010000001001234567890"><tpNF>ENTRADA</tpNF></infNFe>"""
    file_path = create_xml_file(xml_content)

    with pytest.raises(ValueError):
        parse_nfe_xml(file_path)


def test_parse_nfe_xml_malformed_xml_raises_xml_syntax_error(create_xml_file):
    """Garante que XMLs malformados disparem o erro de parsing sintático do lxml."""
    file_path = create_xml_file("<XMLInvalido><unclosed_tag>")

    with pytest.raises(etree.XMLSyntaxError):
        parse_nfe_xml(file_path)
