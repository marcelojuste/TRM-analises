from pathlib import Path
import pytest

from src.models.xml_model import XmlModel
from src.parsers.xml_parser import XmlParser


def test_convert_to_cents():
    assert XmlParser._convert_to_cents("150.55") == 15055
    assert XmlParser._convert_to_cents("0") == 0
    assert XmlParser._convert_to_cents("") == 0
    assert XmlParser._convert_to_cents(None) == 0


def test_xml_base_model_tuple():
    access_key = "35230112345678000195550010000000011234567890"
    model = XmlModel(
        access_key=access_key,
        document_status_number=1,
        cnpj_issuer="12345678000195",
        total_value=15055,
        emission_date="2023-01-01",
    )

    assert model.to_tuple() == (
        "12345678000195",
        15055,
        "2023-01-01",
        "Exit",
        "Authorized",
        "NFe",
        "1",
        access_key,
    )


def test_parse_xml_non_existent_file():
    parser = XmlParser(Path("arquivo_inexistente.xml"))
    results = list(parser.parse_xml())
    assert results == []


def test_parse_xml_empty_file(tmp_path: Path):
    empty_file = tmp_path / "empty.xml"
    empty_file.touch()

    parser = XmlParser(empty_file)
    results = list(parser.parse_xml())
    assert results == []


def test_parse_xml_valid(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35230112345678000195550010000000011234567890">
                <ide>
                    <tpAmb>1</tpAmb>
                    <dhEmi>2023-01-01T10:00:00-03:00</dhEmi>
                    <tpNF>1</tpNF>
                </ide>
                <emit>
                    <CNPJ>12345678000195</CNPJ>
                </emit>
                <total>
                    <ICMSTot>
                        <vNF>150.55</vNF>
                    </ICMSTot>
                </total>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file = tmp_path / "valid_nfe.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    parser = XmlParser(xml_file)
    results = list(parser.parse_xml())

    assert len(results) == 1
    assert results[0] == (
        "12345678000195",
        15055,
        "2023-01-01",
        "Exit",
        "Authorized",
        "NFe",
        "1",
        "35230112345678000195550010000000011234567890",
    )


def test_parse_xml_homologation_environment(tmp_path: Path):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe Id="NFe35230112345678000195550010000000011234567890">
                <ide>
                    <tpAmb>2</tpAmb>
                </ide>
            </infNFe>
        </NFe>
    </nfeProc>
    """
    xml_file = tmp_path / "homolog_nfe.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    parser = XmlParser(xml_file)
    results = list(parser.parse_xml())
    assert results == []