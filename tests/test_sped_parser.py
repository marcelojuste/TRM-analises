from pathlib import Path
import pytest

from src.parsers.sped_parser import SpedParser


def test_sped_parser_accepts_none():
    parser = SpedParser(None)
    assert parser.sped_file is None
    assert parser.file_path is None
    assert parser.get_enterprise() == "EMPRESA_DESCONHECIDA"


def test_parse_0000_icms_ipi():
    parser = SpedParser(None)
    line = "|0000|005|0|01012023|31012023|EMPRESA TESTE SA|12345678000195|"
    parser._parse_0000(line)

    assert parser.sped_type == "EFD_ICMS_IPI"
    assert parser.enterprise_name == "EMPRESA TESTE SA"
    assert parser.cnpj_emit == "12345678000195"


def test_parse_0000_contribuicoes():
    parser = SpedParser(None)
    line = "|0000|005|0|01012023|31012023|EMPRESA CONTRIBUICOES LTDA|12345678000195|MG|3106200||0|||||||"
    parser._parse_0000(line)

    assert parser.sped_type == "EFD_CONTRIBUICOES"
    assert parser.enterprise_name == "EMPRESA CONTRIBUICOES LTDA"
    assert parser.cnpj_emit == "12345678000195"


def test_parse_C100_valid_line(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)

    line = "|C100|1|0|PART001|55|00|1|100|12345678901234567890123456789012345678901234|01052023|01052023|150,55|"
    result = parser._parse_C100(line)

    assert result == (55, "00", "12345678901234567890123456789012345678901234", "2023-05-01", 15055)


def test_parse_C100_invalid_ind_oper(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)

    line = "|C100|0|0|PART001|55|00|1|100|12345678901234567890123456789012345678901234|01052023|01052023|150,55|"
    result = parser._parse_C100(line)

    assert result == ()


def test_parse_C100_invalid_key_length(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)

    line = "|C100|1|0|PART001|55|00|1|100|123456789|01052023|01052023|150,55|"
    result = parser._parse_C100(line)

    assert result == ()