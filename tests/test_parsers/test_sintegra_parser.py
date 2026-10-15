from pathlib import Path
import pytest

from src.parsers.sintegra_parser import SintegraParser


LINE_50_VALIDA = (
    "5007958391000109ISENTO        20260923MG550010090121407T0000000066070"
    "000000000000000000000000000000000000000000000000000000000N"
)


@pytest.fixture
def empty_parser() -> SintegraParser:
    return SintegraParser(None)


@pytest.fixture
def sample_sintegra_file(tmp_path: Path) -> Path:
    content = (
        "10084281640001260010206540094 EMPRESA TESTE                       Juiz de Fora                  MG00000000002026090120260930331\n"
        f"{LINE_50_VALIDA}\n"
        "61                            2026090165     47947647976700000005427950000000000000000000000000000000000000000000005427950000 \n"
    )
    file_path = tmp_path / "sintegra_test.txt"
    file_path.write_text(content, encoding="latin-1")
    return file_path


def test_parse_record_10_valid_line(empty_parser: SintegraParser):
    line_10 = "10084281640001260010206540094 EMPRESA TESTE                       Juiz de Fora                  MG00000000002026090120260930331"
    
    result = empty_parser._parse_record_10(line_10)

    assert result is not None
    assert result["cnpj_issuer"] == "08428164000126"
    assert result["company_name"] == "EMPRESA TESTE"


def test_parse_record_10_invalid_line(empty_parser: SintegraParser):
    line_short = "1008428164000126"
    assert empty_parser._parse_record_10(line_short) is None


def test_parse_record_50_valid_line(empty_parser: SintegraParser):
    result = empty_parser._parse_record_50(LINE_50_VALIDA)

    assert result is not None
    assert result["emission_date"] == "20260923"
    assert result["operation_type_code"] == "T"
    assert result["total_value"] == 66070
    assert result["document_status_code"] == "N"


def test_parse_record_50_invalid_line(empty_parser: SintegraParser):
    line_invalid = "5007958391000109ISENTO"
    assert empty_parser._parse_record_50(line_invalid) is None


def test_parse_record_61_valid_line(empty_parser: SintegraParser):
    line_61 = "61                            2026090165     47947647976700000005427950000000000000000000000000000000000000000000005427950000 "

    result = empty_parser._parse_record_61(line_61)

    assert result is not None
    assert result["emission_date"] == "20260901"
    assert result["total_value"] == 542795


def test_parse_record_61_invalid_line(empty_parser: SintegraParser):
    line_invalid = "61                            20260901"
    assert empty_parser._parse_record_61(line_invalid) is None


def test_parse_sintegra_full_file(sample_sintegra_file: Path):
    parser = SintegraParser(sample_sintegra_file)
    documents = list(parser.parse_sintegra())

    assert parser.company_name == "EMPRESA TESTE"
    assert parser.cnpj_issuer == "08428164000126"

    assert len(documents) == 2

    doc_50 = documents[0]
    assert doc_50[0] == "08428164000126"
    assert doc_50[1] == 66070             
    assert doc_50[2] == "2026-09-23"      

    doc_61 = documents[1]
    assert doc_61[0] == "08428164000126"  
    assert doc_61[1] == 542795            
    assert doc_61[2] == "2026-09-01" 


def test_parse_sintegra_file_without_header_10(tmp_path: Path):
    content = f"{LINE_50_VALIDA}\n"
    file_path = tmp_path / "no_header.txt"
    file_path.write_text(content)

    parser = SintegraParser(file_path)
    documents = list(parser.parse_sintegra())

    assert len(documents) == 0
    assert parser.cnpj_issuer is None