import pytest
from src.parsers.xml_parser import parse_nfe_xml


def test_parse_nfe_xml_valid(tmp_path):
    """
    Testa o processamento de um XML de NFe perfeitamente válido.
    """
    xml_file = tmp_path / "nfe_valid.xml"
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35200112345678901234550010000000012345678901">
                <ide>
                    <tpNF>1</tpNF>
                </ide>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file.write_text(content, encoding="utf-8")

    key, type_nf = parse_nfe_xml(str(xml_file))

    assert key == "35200112345678901234550010000000012345678901"
    assert type_nf == 1


def test_parse_nfe_xml_missing_elements(tmp_path):
    """
    Testa que uma exceção ValueError é levantada se elementos obrigatórios estiverem ausentes.
    """
    xml_file = tmp_path / "nfe_missing.xml"
    # Sem a tag tpNF
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35200112345678901234550010000000012345678901">
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        parse_nfe_xml(str(xml_file))
    
    assert "Erro ao extrair informações do XML da NFe" in str(excinfo.value)


def test_parse_nfe_xml_invalid_key_length(tmp_path):
    """
    Testa que uma exceção ValueError é levantada se a chave de acesso (ID) não possuir 44 dígitos.
    """
    xml_file = tmp_path / "nfe_invalid_key.xml"
    # ID possui apenas 10 dígitos numéricos
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe1234567890">
                <ide>
                    <tpNF>0</tpNF>
                </ide>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        parse_nfe_xml(str(xml_file))
    
    assert "Chave de acesso inválida" in str(excinfo.value)


def test_parse_nfe_xml_non_numeric_type(tmp_path):
    """
    Testa que uma exceção ValueError é levantada se o tipo de NFe (tpNF) não for conversível para inteiro.
    """
    xml_file = tmp_path / "nfe_invalid_type.xml"
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35200112345678901234550010000000012345678901">
                <ide>
                    <tpNF>ABC</tpNF>
                </ide>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_nfe_xml(str(xml_file))
