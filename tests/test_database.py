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
    old_file = mock_paths.temp_files_dir / "old_garbage.tmp"
    old_file.write_text("residual content")

    old_subdir = mock_paths.temp_files_dir / "residual_folder"
    old_subdir.mkdir()
    (old_subdir / "file_inside.xml").write_text("<xml>test</xml>")

    assert old_file.exists()
    assert old_subdir.exists()

    enterprise = "test_company"
    with DisposableAuditDatabase(enterprise) as conn:
        assert not old_file.exists()
        assert not old_subdir.exists()
        assert isinstance(conn, duckdb.DuckDBPyConnection)


def test_purge_on_exit_removes_all_application_temp_files(mock_paths):
    enterprise = "test_company"
    db_path = mock_paths.get_enterprise_db_path(enterprise)

    with DisposableAuditDatabase(enterprise) as conn:
        assert db_path.exists()

        conn.execute("CREATE TABLE invoices (id INT, amount INT);")
        conn.execute("INSERT INTO invoices VALUES (1, 1000);")

        temp_xml = mock_paths.temp_files_dir / "processed_invoice.xml"
        temp_xml.write_text("<nfe>data</nfe>")

        temp_folder = mock_paths.temp_files_dir / "zip_extraction"
        temp_folder.mkdir()
        (temp_folder / "temp.dat").write_bytes(b"12345")

        assert temp_xml.exists()
        assert temp_folder.exists()

    remaining_files = list(mock_paths.temp_files_dir.iterdir())
    assert len(remaining_files) == 0


def test_schema_applied_and_purged_on_completion(mock_paths):
    mock_paths.schema_path.write_text(
        "CREATE TABLE xml_documents (access_key VARCHAR PRIMARY KEY, total_cents INT);",
        encoding="utf-8",
    )

    enterprise = "schema_company"
    db_path = mock_paths.get_enterprise_db_path(enterprise)

    with DisposableAuditDatabase(enterprise) as conn:
        tables = conn.execute("SHOW TABLES;").fetchall()
        table_names = [t[0] for t in tables]
        assert "xml_documents" in table_names

    assert not db_path.exists()
    assert len(list(mock_paths.temp_files_dir.iterdir())) == 0


def test_purge_on_schema_error(mock_paths):
    mock_paths.schema_path.write_text("INVALID_SQL_SYNTAX;", encoding="utf-8")

    enterprise = "error_company"

    with pytest.raises(RuntimeError, match="Error loading database schema"):
        with DisposableAuditDatabase(enterprise):
            pass

    assert len(list(mock_paths.temp_files_dir.iterdir())) == 0