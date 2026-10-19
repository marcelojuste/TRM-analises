from pathlib import Path
import pytest

from src.models.sped_model import SpedModel
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


@pytest.mark.parametrize(
    "line_0000, expected_fields, expected_name, expected_cnpj",
    [
        (
            "|0000|005|0|01012023|31012023|EMPRESA TESTE SA|12345678000195|",
            9,
            "EMPRESA TESTE SA",
            "12345678000195",
        ),
        (
            "|0000|005|0|01012023|31012023|EMPRESA CONTRIBUICOES LTDA|12345678000195|MG|3106200||0|||||||",
            19,
            "EMPRESA CONTRIBUICOES LTDA",
            "12345678000195",
        ),
    ],
)
def test_parse_record_0000_detection(
    empty_parser: SpedParser,
    line_0000: str,
    expected_fields: int,
    expected_name: str,
    expected_cnpj: str,
):
    result = empty_parser._parse_record_0000(line_0000)

    assert result is not None
    assert result["fields"] == expected_fields
    assert result["company_name"] == expected_name
    assert result["issuer_cnpj"] == expected_cnpj

    model = SpedModel(
        sped_number_fields=result["fields"],
        access_key="35230112345678000195550010000000011234567890",
        document_status_number=1,
        cnpj_issuer=result["issuer_cnpj"],
        total_value=1000,
        emission_date="2023-01-01",
    )
    expected_type = "EFD_CONTRIBUTIONS" if expected_fields >= 18 else "EFD_ICMS_IPI"
    assert model.sped_type == expected_type


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
    assert SpedParser._format_date(raw_date) == expected_iso_date


def test_parse_sped_full_integration(tmp_path: Path):
    content = (
        "|0000|005|0|01012023|31012023|EMPRESA TESTE SA|12345678000195|\n"
        "|C100|1|0|PART001|55|00|1|100|12345678901234567890123456789012345678901234|01052023|01052023|150,55|\n"
    )
    sped_file = tmp_path / "sped.txt"
    sped_file.write_text(content, encoding="utf-8")

    parser = SpedParser(sped_file)
    results = list(parser.parse_sped())

    assert len(results) == 1
    assert parser.company_name == "EMPRESA TESTE SA"