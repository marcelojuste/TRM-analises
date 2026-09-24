import pytest
from pathlib import Path
from src.models.sped_document import SpedDocument
from src.parsers.sped_parser import SpedParser 


def test_parse_0000_efd_contribuicoes(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    # 17 pipes -> 18 elementos na lista
    line_0000 = "|0000|006|0|01012023|31012023|Empresa Teste|12345678000190|UF|000000|000|0|1|1|1|1|1|"
    parser._parse_0000(line_0000)
    
    assert parser.sped_type == "EFD_CONTRIBUICOES"
    assert parser.cnpj_emit == "12345678000190"


def test_parse_0000_efd_icms_ipi(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    # 15 pipes -> 16 elementos na lista
    line_0000 = "|0000|015|0|01012023|31012023|Empresa Teste|98765432000110|UF|00|00|0|1|1|1|1|"
    parser._parse_0000(line_0000)
    
    assert parser.sped_type == "EFD_ICMS_IPI"
    assert parser.cnpj_emit == "98765432000110"


def test_parse_0000_unknown(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    line_invalid = "|0001|2|"
    parser._parse_0000(line_invalid)
    
    assert parser.sped_type == "DESCONHECIDO"


def test_parse_C100_valid_line(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    line = "|C100|1|1|3|4|55|00|7|8|12345678901234567890123456789012345678901234|01052023|11|150,55|"
    result = parser._parse_C100(line)
    
    assert result == (55, "00", "12345678901234567890123456789012345678901234", "01-05-2023", 15055)


def test_parse_C100_operation_indicator_not_equal_to_1(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    line = "|C100|0|0|3|4|55|00|7|8|KEY|01052023|11|150,55|"
    result = parser._parse_C100(line)
    
    assert result == ("Homologation",)


def test_parse_C100_empty_values_use_fallback(tmp_path: Path):
    fake_file = tmp_path / "fake.txt"
    fake_file.touch()
    parser = SpedParser(fake_file)
    
    line = "|C100|1|1|3|4||00|7|8|KEY||11||"
    result = parser._parse_C100(line)
    
    assert result == (55, "00", "KEY", "00-00-0000", 0)


def test_parse_sped_complete_file(tmp_path: Path):
    content = (
        "|0000|006|0|01012023|31012023|Empresa Teste|12345678000190|UF|000000|000|0|1|1|1|1|1|\n"
        "|C100|1|1|3|4|55|00|7|8|KEY123|01052023|11|100,00|\n"
    )
    fake_sped = tmp_path / "sped_test.txt"
    fake_sped.write_text(content, encoding="latin-1")

    with SpedParser(fake_sped) as parser:
        assert parser.sped_type == "EFD_CONTRIBUICOES"
        assert parser.cnpj_emit == "12345678000190"
        assert parser.fiscal_notes is not None
        assert len(parser.fiscal_notes) == 1