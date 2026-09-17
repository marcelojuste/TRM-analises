import pytest
from pathlib import Path
import duckdb
from src.app_paths import AppPaths
from src.database import DisposableAuditDatabase


@pytest.fixture
def mock_paths(tmp_path, monkeypatch):
    root_dir = tmp_path
    database_dir = root_dir / "database"
    temp_files_dir = root_dir / "temp_files"
    schema_path = database_dir / "queries" / "schema.sql"

    database_dir.mkdir(parents=True, exist_ok=True)
    temp_files_dir.mkdir(parents=True, exist_ok=True)
    schema_path.parent.mkdir(parents=True, exist_ok=True)

    fake_paths = AppPaths(
        root_dir=root_dir,
        database_dir=database_dir,
        schema_path=schema_path,
        temp_files_dir=temp_files_dir,
    )

    monkeypatch.setattr("src.database.database.PATHS", fake_paths)
    return fake_paths


def test_purge_on_enter_removes_pre_existing_garbage(mock_paths):
    """Garante que qualquer arquivo ou subpasta pré-existente em temp_files é apagado ao entrar no 'with'."""
    old_file = mock_paths.temp_files_dir / "lixo_antigo.tmp"
    old_file.write_text("conteúdo residual")

    old_subdir = mock_paths.temp_files_dir / "pasta_residual"
    old_subdir.mkdir()
    (old_subdir / "arquivo_dentro.xml").write_text("<xml>teste</xml>")

    assert old_file.exists()
    assert old_subdir.exists()

    enterprise = "empresa_teste"
    with DisposableAuditDatabase(enterprise) as conn:
        assert not old_file.exists()
        assert not old_subdir.exists()
        assert isinstance(conn, duckdb.DuckDBPyConnection)


def test_purge_on_exit_removes_all_application_temp_files(mock_paths):
    """Garante que TUDO o que for criado na sessão (banco, .wal, XMLs extraídos, subpastas) é apagado ao sair do 'with'."""
    enterprise = "empresa_teste"
    db_path = mock_paths.get_enterprise_db_path(enterprise)

    with DisposableAuditDatabase(enterprise) as conn:
        assert db_path.exists()

        conn.execute("CREATE TABLE notas (id INT, valor INT);")
        conn.execute("INSERT INTO notas VALUES (1, 1000);")

        temp_xml = mock_paths.temp_files_dir / "nota_processada.xml"
        temp_xml.write_text("<nfe>dados</nfe>")

        temp_folder = mock_paths.temp_files_dir / "extracao_zip"
        temp_folder.mkdir()
        (temp_folder / "temp.dat").write_bytes(b"12345")

        assert temp_xml.exists()
        assert temp_folder.exists()

    arquivos_restantes = list(mock_paths.temp_files_dir.iterdir())
    assert len(arquivos_restantes) == 0


def test_schema_applied_and_purged_on_completion(mock_paths):
    """Valida se o schema.sql é executado no banco temporário e limpo corretamente após a execução."""
    mock_paths.schema_path.write_text(
        "CREATE TABLE xml_documents (chave_acesso VARCHAR PRIMARY KEY, valor_centavos INT);",
        encoding="utf-8",
    )

    enterprise = "empresa_schema"
    db_path = mock_paths.get_enterprise_db_path(enterprise)

    with DisposableAuditDatabase(enterprise) as conn:
        tables = conn.execute("SHOW TABLES;").fetchall()
        table_names = [t[0] for t in tables]
        assert "xml_documents" in table_names

    assert not db_path.exists()
    assert len(list(mock_paths.temp_files_dir.iterdir())) == 0


def test_purge_on_schema_error(mock_paths):
    """Garante que mesmo que o schema.sql falhe com erro de sintaxe, o banco é fechado e temp_files é limpo."""
    mock_paths.schema_path.write_text("SINTAXE_INVALIDA_DE_SQL;", encoding="utf-8")

    enterprise = "empresa_erro"

    with pytest.raises(RuntimeError, match="Erro ao carregar o schema do banco de dados"):
        with DisposableAuditDatabase(enterprise):
            pass

    assert len(list(mock_paths.temp_files_dir.iterdir())) == 0
