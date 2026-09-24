import pytest
from pathlib import Path
from src.models.fiscal_document import FiscalDocument
from src.parsers.xml_parser import XmlParser


def test_to_centavos_valid_conversions():
    assert XmlParser._to_centavos("150.50") == 15050
    assert XmlParser._to_centavos("0.01") == 1
    assert XmlParser._to_centavos("100") == 10000


def test_to_centavos_empty_values():
    assert XmlParser._to_centavos("") == 0
    assert XmlParser._to_centavos(None) == 0


def test_get_xml_files_success(tmp_path: Path):
    (tmp_path / "note1.xml").touch()
    (tmp_path / "note2.xml").touch()
    (tmp_path / "text.txt").touch()

    files = list(XmlParser.get_xml_files(tmp_path))
    assert len(files) == 2
    assert all(f.suffix == ".xml" for f in files)


def test_get_xml_files_invalid_directory():
    non_existent_path = Path("/path/that/does/not/exist")
    with pytest.raises(FileNotFoundError, match="Diretório inválido"):
        list(XmlParser.get_xml_files(non_existent_path))


def test_parse_valid_production_nfe(tmp_path: Path):
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
    xml_file = tmp_path / "valid_nfe.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    doc = XmlParser.parse_xml(xml_file)

    assert doc is not None
    assert isinstance(doc, FiscalDocument)
    assert doc.access_key == "35260900000000000000550010000000011000000000"
    assert doc.cnpj_emit == "12345678000195"
    assert doc.total_value == 150050
    assert doc.emission_date == "2026-09-17"
    assert doc.nfe_model == 1
    assert doc.document_status == "00"


def test_parse_ignores_homologation(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <NFe>
        <infNFe Id="NFe35260900000000000000550010000000011000000000">
            <ide>
                <tpAmb>2</tpAmb> <!-- Homologation / Test -->
            </ide>
        </infNFe>
    </NFe>
    """
    xml_file = tmp_path / "homologation_nfe.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    doc = XmlParser.parse_xml(xml_file)
    assert doc is None


def test_parse_ignores_invalid_key_length(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <NFe>
        <infNFe Id="NFe12345"> <!-- Short key -->
            <ide>
                <tpAmb>1</tpAmb>
            </ide>
        </infNFe>
    </NFe>
    """
    xml_file = tmp_path / "short_key_nfe.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    doc = XmlParser.parse_xml(xml_file)
    assert doc is None


def test_parse_empty_file(tmp_path: Path):
    xml_file = tmp_path / "empty.xml"
    xml_file.write_text("", encoding="utf-8")

    doc = XmlParser.parse_xml(xml_file)
    assert doc is None