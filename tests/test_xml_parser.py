from pathlib import Path
import pytest

from src.models.xml_model import XmlBaseModel
from src.parsers.xml_parser import XmlParser


def test_list_xml_files(tmp_path: Path):
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("<root></root>")

    txt_file = tmp_path / "test.txt"
    txt_file.write_text("hello")

    files = XmlParser.list_xml_files(tmp_path)
    assert len(files) == 1
    assert files[0] == xml_file


def test_convert_to_cents():
    assert XmlParser._convert_to_cents("150.55") == 15055
    assert XmlParser._convert_to_cents("0") == 0
    assert XmlParser._convert_to_cents("") == 0
    assert XmlParser._convert_to_cents(None) == 0


def test_xml_base_model_tuple():
    model = XmlBaseModel(
        access_key="35230112345678000195550010000000011234567890",
        document_status_number=1,
        cnpj_issuer="12345678000195",
        total_value=15055,
        emission_date="2023-01-01",
    )

    assert model.to_tuple() == (
        "12345678000195",
        15055,
        "2023-01-01",
        "Saída",
        "35230112345678000195550010000000011234567890",
        "NFe",
    )


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
    generator = parser.parse_xml()
    assert generator is not None

    results = list(generator)
    assert len(results) == 1
    assert results[0] == (
        "12345678000195",
        15055,
        "2023-01-01",
        "Saída",
        "35230112345678000195550010000000011234567890",
        "NFe",
    )