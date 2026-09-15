import pytest
from unittest.mock import patch, MagicMock

from src.services.audit import audit_query

@patch("src.services.audit.get_connection")
@patch("src.services.audit.QUERY_AUDIT_PATH")
@patch("src.services.audit.FILE_ENCODING", "utf-8")
def test_audit_query_executes_sql_from_file_successfully(mock_query_path, mock_get_conn):
    """
    Garante que audit_query lê o arquivo SQL com o encoding correto 
    e envia a query diretamente para a conexão do banco de dados.
    """
    fake_sql = "COPY (SELECT * FROM audit) TO 'output/auditoria.csv' (HEADER TRUE);"
    mock_query_path.read_text.return_value = fake_sql

    mock_db_conn = MagicMock()
    mock_get_conn.return_value = mock_db_conn

    audit_query()

    mock_query_path.read_text.assert_called_once_with(encoding="utf-8")

    mock_get_conn.assert_called_once()

    mock_db_conn.execute.assert_called_once_with(fake_sql)


@patch("src.services.audit.get_connection")
@patch("src.services.audit.QUERY_AUDIT_PATH")
@patch("src.services.audit.FILE_ENCODING", "utf-8")
def test_audit_query_propagates_file_not_found_error(mock_query_path, mock_get_conn):
    """Garante que a função lança exceção se o arquivo de query SQL não for encontrado."""
    mock_query_path.read_text.side_effect = FileNotFoundError("Arquivo SQL não encontrado")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        audit_query()

    mock_get_conn.assert_not_called()
