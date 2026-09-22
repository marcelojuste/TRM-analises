import pytest
from pathlib import Path
from src.models.sped_document import SpedDocument
from src.parsers.sped_parser import SpedParser 

def test_parse_0000_efd_contribuicoes():
    line_0000 = "|0000|2|3|4|5|6| 12.345.678/0001-90 |8|9|10|11|12|13|14|"
    
    SpedParser._parse_0000(line_0000)
    
    assert SpedParser.sped_type == "EFD_CONTRIBUICOES"
    assert SpedParser.cnpj_emit == "12345678000190"


def test_parse_0000_efd_icms_ipi():
    line_0000 = "|0000|2|3|4|5|6| 98.765.432/0001-10 |8|9|10|11|12|13|"
    
    SpedParser._parse_0000(line_0000)
    
    assert SpedParser.sped_type == "EFD_ICMS_IPI"
    assert SpedParser.cnpj_emit == "98765432000110"


def test_parse_0000_desconhecido():
    line_invalid = "|0001|2|"
    
    SpedParser._parse_0000(line_invalid)
    
    assert SpedParser.sped_type == "DESCONHECIDO"

def test_parse_C100_linha_valida():
    line = "|C100|1|1|3|4|55|00|7|8|12345678901234567890123456789012345678901234|01052023|11|150,55|"
    
    result = SpedParser._parse_C100(line)
    
    assert result == (55, "00", "12345678901234567890123456789012345678901234", "01-05-2023", 15055)


def test_parse_C100_indicador_operacao_diferente_de_1():
    line = "|C100|0|0|3|4|55|00|7|8|CHAVE|01052023|11|150,55|"
    
    result = SpedParser._parse_C100(line)
    
    assert result == ("Homologation",)


def test_parse_C100_valores_vazios_usam_fallback():
    line = "|C100|1|1|3|4||00|7|8|CHAVE||11||"
    
    result = SpedParser._parse_C100(line)
    
    assert result == (55, "00", "CHAVE", "00-00-0000", 0)


def test_parse_sped_arquivo_completo(tmp_path):
    content = (
        "|0000|2|3|4|5|6| 12.345.678/0001-90 |8|9|10|11|12|13|14|\n"
        "|C100|1|1|3|4|55|00|7|8|CHAVE123|01052023|11|100,00|\n"
    )
    fake_sped = tmp_path / "sped_test.txt"
    fake_sped.write_text(content, encoding="latin-1")

    SpedParser.file_path = fake_sped
    SpedParser.fiscal_notes = []
    
    list(SpedParser._parse_sped())
    
    assert SpedParser.sped_type == "EFD_CONTRIBUICOES"
    assert SpedParser.cnpj_emit == "12345678000190"
    assert len(SpedParser.fiscal_notes) == 1