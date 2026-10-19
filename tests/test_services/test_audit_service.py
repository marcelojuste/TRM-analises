from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd
import threading
import pytest

from src.services.audit_service import AuditService


@pytest.fixture
def temp_nfe_dir(tmp_path: Path) -> Path:
    nfe_dir = tmp_path / "nfe"
    nfe_dir.mkdir()
    (nfe_dir / "note1.xml").write_text("<xml>1</xml>")
    (nfe_dir / "note2.XML").write_text("<xml>2</xml>")
    (nfe_dir / "ignore.txt").write_text("ignore")
    return nfe_dir


@pytest.fixture
def temp_fiscal_file(tmp_path: Path) -> Path:
    fiscal_file = tmp_path / "sped.txt"
    fiscal_file.write_text("|0000|...\n|C100|...")
    return fiscal_file


def test_get_xml_files_valid_directory(temp_nfe_dir: Path):
    files = AuditService._get_xml_files(temp_nfe_dir)
    assert len(files) == 2
    assert all(f.suffix.lower() == ".xml" for f in files)


def test_get_xml_files_invalid_directory(tmp_path: Path):
    invalid_path = tmp_path / "non_existing_dir"
    with pytest.raises(FileNotFoundError, match="Caminho do diretório inválido"):
        AuditService._get_xml_files(invalid_path)


def test_check_cancellation_triggered():
    cancel_event = threading.Event()
    cancel_event.set()
    service = AuditService(
        fiscal_archive_path=Path("fake.txt"),
        cancel_event=cancel_event,
    )
    with pytest.raises(InterruptedError, match="Operação cancelada pelo utilizador."):
        service._check_cancellation()


def test_check_cancellation_not_triggered():
    cancel_event = threading.Event()
    service = AuditService(
        fiscal_archive_path=Path("fake.txt"),
        cancel_event=cancel_event,
    )
    service._check_cancellation()


def test_run_pipeline_missing_xml_dirs(temp_fiscal_file: Path):
    service = AuditService(
        fiscal_archive_path=temp_fiscal_file,
        nfe_dir_path=Path("invalid_nfe_path"),
        is_sped=True,
    )
    with pytest.raises(FileNotFoundError, match="Diretórios de XMLs não foram informados"):
        service.run_pipeline()


def test_run_pipeline_missing_fiscal_file(temp_nfe_dir: Path):
    service = AuditService(
        fiscal_archive_path=None,
        nfe_dir_path=temp_nfe_dir,
        is_sped=True,
    )
    with pytest.raises(FileNotFoundError, match="Arquivos fiscais não foram informados"):
        service.run_pipeline()


@patch("src.services.audit_service.PATHS")
@patch("src.services.audit_service.SpedParser")
@patch("src.services.audit_service.XmlParser")
def test_run_pipeline_sped_success(
    mock_xml_parser,
    mock_sped_parser,
    mock_paths,
    temp_nfe_dir: Path,
    temp_fiscal_file: Path,
    tmp_path: Path,
):
    mock_xml_instance = MagicMock()
    mock_xml_instance.parse_xml.return_value = [
        ("12345678000195", 10000, "2023-01-01", "Exit", "Authorized", "NFe", "1", "35230112345678000195550010000000011234567890")
    ]
    mock_xml_parser.return_value = mock_xml_instance

    mock_sped_instance = MagicMock()
    mock_sped_instance.enterprise = "EMPRESA DE TESTE SA"
    mock_sped_instance.parse_sped.return_value = [
        ("12345678000195", 10000, "2023-01-01", "Exit", "Authorized", "NFe", "1", "35230112345678000195550010000000011234567890", "EFD_ICMS_IPI")
    ]
    mock_sped_parser.return_value.__enter__.return_value = mock_sped_instance

    query_file = tmp_path / "query.sql"
    query_file.write_text("SELECT 'OK' as status")
    mock_paths.sped_query_path = query_file

    service = AuditService(
        fiscal_archive_path=temp_fiscal_file,
        nfe_dir_path=temp_nfe_dir,
        is_sped=True,
    )

    result = service.run_pipeline()

    assert result["enterprise"] == "EMPRESA DE TESTE SA"
    assert "metrics" in result
    assert isinstance(result["audit_results"], pd.DataFrame)
    assert result["audit_results"].iloc[0]["status"] == "OK"


@patch("src.services.audit_service.PATHS")
@patch("src.services.audit_service.SintegraParser")
@patch("src.services.audit_service.XmlParser")
def test_run_pipeline_sintegra_success(
    mock_xml_parser,
    mock_sintegra_parser,
    mock_paths,
    temp_nfe_dir: Path,
    temp_fiscal_file: Path,
    tmp_path: Path,
):
    mock_xml_instance = MagicMock()
    mock_xml_instance.parse_xml.return_value = [
        ("12345678000195", 5000, "2023-01-01", "Exit", "Authorized", "NFe", "1", "35230112345678000195550010000000011234567890")
    ]
    mock_xml_parser.return_value = mock_xml_instance

    mock_sintegra_instance = MagicMock()
    mock_sintegra_instance.enterprise = "EMPRESA SINTEGRA LTDA"
    mock_sintegra_instance.parse_sintegra.return_value = [
        ("12345678000195", 5000, "2023-01-01", "Exit", "Authorized", "NFe", "1")
    ]
    mock_sintegra_parser.return_value = mock_sintegra_instance

    query_file = tmp_path / "sintegra_query.sql"
    query_file.write_text("SELECT 'OK_SINTEGRA' as status")
    mock_paths.sintegra_query_path = query_file

    service = AuditService(
        fiscal_archive_path=temp_fiscal_file,
        nfe_dir_path=temp_nfe_dir,
        is_sped=False,
    )

    result = service.run_pipeline()

    assert result["enterprise"] == "EMPRESA SINTEGRA LTDA"
    assert "metrics" in result
    assert isinstance(result["audit_results"], pd.DataFrame)
    assert result["audit_results"].iloc[0]["status"] == "OK_SINTEGRA"