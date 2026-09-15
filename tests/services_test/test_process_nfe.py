import pytest
from unittest.mock import patch, MagicMock

from src.services.process_xml_files import process_xml_files

@pytest.fixture
def mock_deps_xml():
    """Isola as dependências do módulo src.services.process_xml_files."""
    with patch("src.services.process_xml_files.get_connection") as mock_conn, \
         patch("src.services.process_xml_files.parse_nfe_xml") as mock_parser, \
         patch("src.services.process_xml_files.INSERT_NFE_PATH") as mock_sql_path, \
         patch("src.services.process_xml_files.FILE_ENCODING", "utf-8"):
        
        mock_db_instance = MagicMock()
        mock_conn.return_value = mock_db_instance

        mock_sql_path.exists.return_value = True
        mock_sql_path.read_text.return_value = "INSERT INTO nota_xml (nfe, tpNF) VALUES (?, ?);"

        yield {
            "db": mock_db_instance,
            "parser": mock_parser,
            "sql_path": mock_sql_path,
            "get_connection": mock_conn
        }


def test_process_xml_files_success(tmp_path, mock_deps_xml):
    """Garante a leitura correta dos XMLs e a inserção em lote no banco de dados."""
    xml1 = tmp_path / "nfe_1.xml"
    xml2 = tmp_path / "nfe_2.xml"
    xml1.touch()
    xml2.touch()

    xml_files = [str(xml1), str(xml2)]
    mock_deps_xml["parser"].side_effect = [
        ("35260912345678000195550010000001001234567890", 1),
        ("35260912345678000195550020000002001234567890", 0)
    ]

    process_xml_files(xml_files)

    assert mock_deps_xml["parser"].call_count == 2
    mock_deps_xml["db"].executemany.assert_called_once_with(
        "INSERT INTO nota_xml (nfe, tpNF) VALUES (?, ?);",
        [
            ("35260912345678000195550010000001001234567890", 1),
            ("35260912345678000195550020000002001234567890", 0)
        ]
    )


def test_process_xml_files_empty_list(capsys, mock_deps_xml):
    """Valida o comportamento ao passar uma lista vazia de arquivos."""
    process_xml_files([])

    captured = capsys.readouterr()
    assert "Nenhum arquivo XML válido encontrado" in captured.out
    mock_deps_xml["db"].executemany.assert_not_called()


def test_process_xml_files_invalid_file_path(tmp_path, capsys, mock_deps_xml):
    """Garante o aviso e a interrupção ao fornecer um arquivo inexistente."""
    non_existent_file = str(tmp_path / "invalid.xml")

    process_xml_files([non_existent_file])

    captured = capsys.readouterr()
    assert f"Arquivo XML inválido: {non_existent_file}" in captured.out
    mock_deps_xml["db"].executemany.assert_not_called()


def test_process_xml_files_path_is_directory(tmp_path, capsys, mock_deps_xml):
    """Valida que diretórios passados na lista são rejeitados."""
    sub_dir = tmp_path / "some_directory"
    sub_dir.mkdir()

    process_xml_files([str(sub_dir)])

    captured = capsys.readouterr()
    assert "Arquivo XML inválido:" in captured.out
    mock_deps_xml["db"].executemany.assert_not_called()


def test_process_xml_files_missing_sql_file(tmp_path, capsys, mock_deps_xml):
    """Verifica se interrompe o processo quando o arquivo SQL de inserção não existe."""
    xml_file = tmp_path / "nfe.xml"
    xml_file.touch()

    mock_deps_xml["sql_path"].exists.return_value = False

    process_xml_files([str(xml_file)])

    captured = capsys.readouterr()
    assert "Arquivo SQL de inserção não encontrado:" in captured.out
    mock_deps_xml["db"].executemany.assert_not_called()
