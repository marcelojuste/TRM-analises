import pytest
from pathlib import Path
from src.models.fiscal_document import FiscalDocument
from src.parsers.xml_parser import XmlParser


def test_to_centavos_conversoes_validas():
    assert XmlParser._to_centavos("150.50") == 15050
    assert XmlParser._to_centavos("0.01") == 1
    assert XmlParser._to_centavos("100") == 10000


def test_to_centavos_valores_vazios():
    assert XmlParser._to_centavos("") == 0
    assert XmlParser._to_centavos(None) == 0


def test_get_xml_files_sucesso(tmp_path: Path):
    (tmp_path / "nota1.xml").touch()
    (tmp_path / "nota2.xml").touch()
    (tmp_path / "texto.txt").touch()

    files = list(XmlParser.get_xml_files(tmp_path))
    assert len(files) == 2
    assert all(f.suffix == ".xml" for f in files)


def test_get_xml_files_diretorio_invalido():
    path_inexistente = Path("/caminho/que/nao/existe")
    with pytest.raises(FileNotFoundError, match="Diretório inválido"):
        list(XmlParser.get_xml_files(path_inexistente))


def test_parse_nfe_valida_producao(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35260900000000000000550010000000011000000000">
                <ide>
                    <tpAmb>1</tpAmb>
                    <dhEmi>2026-09-17T10:00:00-03:00</dhEmi>
                </ide>
                <emit>
                    <CNPJ>12345678000195</CNPJ>
                </emit>
                <total>
                    <ICMSTot>
                        <vNF>1500.50</vNF>
                    </ICMSTot>
                </total>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file = tmp_path / "nfe_valida.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    docs = list(XmlParser.parse_xml(xml_file))

    assert len(docs) == 1
    doc = docs[0]
    assert isinstance(doc, FiscalDocument)
    assert doc.access_key == "35260900000000000000550010000000011000000000"
    assert doc.cnpj_emit == "12345678000195"
    assert doc.total_value == 150050
    assert doc.emission_date == "2026-09-17"
    assert doc.nf_type == 1
    assert doc.situation_code == "00"


def test_parse_ignora_homologacao(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <NFe>
        <infNFe Id="NFe35260900000000000000550010000000011000000000">
            <ide>
                <tpAmb>2</tpAmb> <!-- Homologação / Teste -->
            </ide>
        </infNFe>
    </NFe>
    """
    xml_file = tmp_path / "nfe_homologacao.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    docs = list(XmlParser.parse_xml(xml_file))
    assert len(docs) == 0


def test_parse_ignora_chave_tamanho_invalido(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <NFe>
        <infNFe Id="NFe12345"> <!-- Chave curta -->
            <ide>
                <tpAmb>1</tpAmb>
            </ide>
        </infNFe>
    </NFe>
    """
    xml_file = tmp_path / "nfe_chave_curta.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    docs = list(XmlParser.parse_xml(xml_file))
    assert len(docs) == 0


def test_parse_arquivo_vazio(tmp_path: Path):
    xml_file = tmp_path / "vazio.xml"
    xml_file.write_text("", encoding="utf-8")

    docs = list(XmlParser.parse_xml(xml_file))
    assert len(docs) == 0