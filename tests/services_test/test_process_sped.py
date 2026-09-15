import pytest
from unittest.mock import patch, MagicMock

from src.services.process_sped import process_sped_file

@pytest.fixture
def mock_deps_sped():
    """Isola as dependências do módulo src.services.process_sped."""
    with patch("src.services.process_sped.get_connection") as mock_conn, \
         patch("src.services.process_sped.INSERT_SPED_IPI_PATH") as mock_ipi_path, \
         patch("src.services.process_sped.INSERT_SPED_COFINS_PATH") as mock_cofins_path, \
         patch("src.services.process_sped.FILE_ENCODING", "utf-8"):

        mock_db_instance = MagicMock()
        mock_conn.return_value = mock_db_instance

        mock_ipi_path.read_text.return_value = "INSERT INTO sped_ipi (nfe, tpNF) VALUES (?, ?);"
        mock_cofins_path.read_text.return_value = "INSERT INTO sped_cofins (nfe, tpNF) VALUES (?, ?);"

        yield {
            "db": mock_db_instance,
            "ipi_path": mock_ipi_path,
            "cofins_path": mock_cofins_path,
        }


def test_process_sped_file_icms_success(mock_deps_sped):
    """Garante a execução da query correta do SPED IPI quando type_sped for 'ICMS'."""
    batch = [("000000100", "1"), ("000000200", "0")]

    process_sped_file(batch, "ICMS")

    mock_deps_sped["ipi_path"].read_text.assert_called_once_with(encoding="utf-8")
    mock_deps_sped["db"].executemany.assert_called_once_with(
        "INSERT INTO sped_ipi (nfe, tpNF) VALUES (?, ?);",
        batch
    )


def test_process_sped_file_cofins_success(mock_deps_sped):
    """Garante a execução da query correta do SPED COFINS quando type_sped for 'COFINS'."""
    batch = [("000000300", "1")]

    process_sped_file(batch, "COFINS")

    mock_deps_sped["cofins_path"].read_text.assert_called_once_with(encoding="utf-8")
    mock_deps_sped["db"].executemany.assert_called_once_with(
        "INSERT INTO sped_cofins (nfe, tpNF) VALUES (?, ?);",
        batch
    )


def test_process_sped_file_empty_batch(mock_deps_sped):
    """Valida o retorno de erro e a interrupção da execução ao receber lista vazia."""
    result = process_sped_file([], "ICMS")

    assert result == "Nenhuma NFe encontrada no arquivo SPED --process_sped_file.py"
    mock_deps_sped["db"].executemany.assert_not_called()


def test_process_sped_file_invalid_type_sped_raises_unbound_local_error(mock_deps_sped):
    """
    DOCUMENTA UM BUG/VULNERABILIDADE DA FUNÇÃO:
    Passar um tipo não mapeado (ex: 'PIS' ou 'icms') causará UnboundLocalError 
    pois `query_sql` não é definida no match/case.
    """
    batch = [("000000100", "1")]

    with pytest.raises(UnboundLocalError):
        process_sped_file(batch, "INVALID_TYPE")

    mock_deps_sped["db"].executemany.assert_not_called()
