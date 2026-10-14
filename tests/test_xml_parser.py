from pathlib import Path
import pytest

from src.parsers.sped_parser import SpedParser

@pytest.fixture
def empty_parser() -> SpedParser:
    return SpedParser(None)


@pytest.fixture
def file_parser(tmp_path: Path) -> SpedParser:
    fake_file = tmp_path / "fake_sped.txt"
    fake_file.touch()
    return SpedParser(fake_file)

def test_sped_parser_accepts_none(empty_parser: SpedParser):
    assert empty_parser.file_path is None
    assert empty_parser.get_enterprise() == "EMPRESA_DESCONHECIDA"


@pytest.mark.parametrize(
    "line_0000, expected_type, expected_name, expected_cnpj",
    [
        (
            "|0000|005|0|01012023|31012023|EMPRESA TESTE SA|12345678000195|",
            "EFD_ICMS_IPI",
            "EMPRESA TESTE SA",
            "12345678000195",
        ),
        (
            "|0000|005|0|01012023|31012023|EMPRESA CONTRIBUICOES LTDA|12345678000195|MG|3106200||0|||||||",
            "EFD_CONTRIBUICOES",
            "EMPRESA CONTRIBUICOES LTDA",
            "12345678000195",
        ),
    ],
)

def test_parse_record_0000_detection(
    empty_parser: SpedParser,
    line_0000: str,
    expected_type: str,
    expected_name: str,
    expected_cnpj: str,
):
    empty_parser._parse_record_0000(line_0000)

    assert empty_parser.sped_type == expected_type
    assert empty_parser.company_name == expected_name
    assert empty_parser.issuer_cnpj == expected_cnpj

def test_parse_record_c100_valid_line(file_parser: SpedParser):
    valid_c100_line = (
        "|C100|1|0|PART001|55|00|1|100|"
        "12345678901234567890123456789012345678901234|"
        "01052023|01052023|150,55|"
    )

    result = file_parser._parse_record_c100(valid_c100_line)

    assert result == {
        "nfe_model": 55,
        "document_status": "00",
        "access_key": "12345678901234567890123456789012345678901234",
        "emission_date": "2023-05-01",
        "total_value": 15055,
    }


@pytest.mark.parametrize(
    "invalid_line",
    [
        "|C100|0|0|PART001|55|00|1|100|12345678901234567890123456789012345678901234|01052023|01052023|150,55|",
        "|C100|1|0|PART001|55|00|1|100|123456789|01052023|01052023|150,55|",
        "|C100|1|0|PART001|55|00|",
    ],
)

def test_parse_record_c100_invalid_lines(file_parser: SpedParser, invalid_line: str):
    result = file_parser._parse_record_c100(invalid_line)

    assert result is None


@pytest.mark.parametrize(
    "raw_date, expected_iso_date",
    [
        ("01052023", "2023-05-01"),
        ("31122026", "2026-12-31"),
        ("invalid", "1900-01-01"),
        ("", "1900-01-01"),
    ],
)

def test_format_sped_date(raw_date: str, expected_iso_date: str):
    assert SpedParser._format_sped_date(raw_date) == expected_iso_date


@pytest.mark.parametrize(
    "raw_val, expected_cents",
    [
        ("150,55", 15055),
        ("0,00", 0),
        ("100", 10000),
        (None, 0),
    ],
)

def test_convert_to_cents(raw_val: str, expected_cents: int):
    assert SpedParser._convert_to_cents(raw_val) == expected_cents
