import pytest
from src.parsers.sped_parser import parse_sped


def test_parse_sped_valid_c100(tmp_path):
    """
    Testa o processamento de uma linha C100 válida com indicador de situação '00'.
    """
    # Cria um arquivo temporário simulando o arquivo SPED
    sped_file = tmp_path / "sped_test.txt"
    # Campos:
    # fields[0] = C100
    # fields[1] = 1 (type_nfe)
    # fields[5] = 00 (sit_doc)
    # fields[8] = 35200112345678901234550010000000012345678901 (id_nfe)
    content = "|C100|1|2|3|4|00|6|7|35200112345678901234550010000000012345678901|\n"
    sped_file.write_text(content, encoding="latin-1")

    results = list(parse_sped(str(sped_file)))

    assert len(results) == 1
    assert results[0] == {
        "id_nfe": "35200112345678901234550010000000012345678901",
        "type_nfe": "1",
    }


def test_parse_sped_invalid_situation(tmp_path):
    """
    Testa que uma linha C100 com situação diferente de '00' é ignorada.
    """
    sped_file = tmp_path / "sped_test.txt"
    # fields[5] = '01' (situação inválida para processamento)
    content = "|C100|1|2|3|4|01|6|7|35200112345678901234550010000000012345678901|\n"
    sped_file.write_text(content, encoding="latin-1")

    results = list(parse_sped(str(sped_file)))

    assert len(results) == 0


def test_parse_sped_ignored_record_type(tmp_path):
    """
    Testa que registros diferentes de C100 são ignorados.
    """
    sped_file = tmp_path / "sped_test.txt"
    content = (
        "|REG_IGNORADO|1|2|3|\n"
        "|C170|1|2|3|4|5|6|7|8|9|\n"
    )
    sped_file.write_text(content, encoding="latin-1")

    results = list(parse_sped(str(sped_file)))

    assert len(results) == 0


def test_parse_sped_multiple_records(tmp_path):
    """
    Testa o processamento de múltiplos registros mistos, garantindo que
    apenas os C100 válidos sejam retornados.
    """
    sped_file = tmp_path / "sped_test.txt"
    content = (
        "|REG_IGNORADO|1|2|3|\n"
        "|C100|1|2|3|4|00|6|7|35200112345678901234550010000000012345678901|\n"
        "|C100|0|2|3|4|01|6|7|35200112345678901234550010000000012345678902|\n"
        "|C100|0|2|3|4|00|6|7|35200112345678901234550010000000012345678903|\n"
    )
    sped_file.write_text(content, encoding="latin-1")

    results = list(parse_sped(str(sped_file)))

    assert len(results) == 2
    assert results[0] == {
        "id_nfe": "35200112345678901234550010000000012345678901",
        "type_nfe": "1",
    }
    assert results[1] == {
        "id_nfe": "35200112345678901234550010000000012345678903",
        "type_nfe": "0",
    }
