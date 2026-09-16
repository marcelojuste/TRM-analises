import pytest
from unittest.mock import mock_open, patch
from src.parsers.sped_parser import parse_sped

def test_parse_sped_ignores_non_00_situations(tmp_path):
    """Verifica se registros com COD_SIT != '00' são ignorados."""
    content = (
        "|C100|0|1|000001|55|00|001|123456789|35260900000000000000550010000000011000000000|01012026|\n"
        "|C100|0|1|000002|55|02|001|123456789|35260900000000000000550010000000021000000000|01012026|\n"
        "|C100|0|1|000003|55|04|001|123456789|35260900000000000000550010000000031000000000|01012026|\n"
    )
    file_path = tmp_path / "sped_status.txt"
    file_path.write_text(content, encoding="latin-1")

    result = parse_sped(file_path)

    assert len(result) == 1
    assert result == [("35260900000000000000550010000000011000000000", "0")]

def test_parse_sped_empty_file(tmp_path):
    """Garante que um arquivo vazio retorne uma lista vazia sem quebrar."""
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="latin-1")

    result = parse_sped(file_path)

    assert result == []

def test_parse_sped_no_c100_lines(tmp_path):
    """Garante o comportamento quando o SPED não contém nenhuma linha |C100|."""
    content = "|0000|000|...\n|C990|10|\n"
    file_path = tmp_path / "no_c100.txt"
    file_path.write_text(content, encoding="latin-1")

    result = parse_sped(file_path)

    assert result == []

def test_parse_sped_handles_latin1_characters():
    """Valida se caracteres acentuados típicos do latin-1 não causam erro de decoding."""
    content = "|C100|0|1|000001|55|00|001|123456789|35260900000000000000550010000000011000000000|01012026|Razão Social Com Ação|\n"

    with patch("builtins.open", mock_open(read_data=content.encode("latin-1").decode("latin-1"))):
        result = parse_sped("fake_path.txt")
        assert result == [("35260900000000000000550010000000011000000000", "0")]

def test_parse_sped_file_not_found():
    """Garante que o erro FileNotFoundError seja disparado se o arquivo não existir."""
    with pytest.raises(FileNotFoundError):
        parse_sped("caminho/inexistente/sped.txt")

def test_parse_sped_malformed_c100_line_is_ignored(tmp_path):
    """Garante que linhas C100 incompletas/malformatadas são ignoradas com segurança."""
    content = "|C100|0|1|000001|\n"
    file_path = tmp_path / "malformed.txt"
    file_path.write_text(content, encoding="latin-1")

    result = parse_sped(file_path)
    assert result == []
