from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from openpyxl import load_workbook

from src.app_paths import AppPaths
from src.services.audit_service import AuditService


@pytest.fixture
def mock_paths(tmp_path, monkeypatch):
    root_dir = tmp_path
    database_dir = root_dir / "database"
    queries_dir = database_dir / "queries"
    temp_files_dir = root_dir / "temp_files"
    outputs_dir = root_dir / "outputs"
    schema_path = queries_dir / "schema.sql"

    queries_dir.mkdir(parents=True, exist_ok=True)
    temp_files_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    (queries_dir / "audit.sql").write_text("SELECT 1;", encoding="utf-8")
    schema_path.write_text("CREATE TABLE test (id INT);", encoding="utf-8")

    fake_paths = AppPaths(
        root_dir=root_dir,
        database_dir=database_dir,
        queries_dir=queries_dir,
        schema_path=schema_path,
        temp_files_dir=temp_files_dir,
        images_dir=root_dir / "images",
        icons_dir=root_dir / "icons",
        outputs_dir=outputs_dir,
    )

    monkeypatch.setattr("src.services.audit_service.PATHS", fake_paths)
    monkeypatch.setattr("src.database.database.PATHS", fake_paths)
    return fake_paths


def test_audit_service_initialization():
    nfe_dir = Path("/tmp/nfe")
    nfce_dir = Path("/tmp/nfce")
    sped_fiscal = Path("/tmp/sped_fiscal.txt")
    sped_cofins = Path("/tmp/sped_cofins.txt")

    service = AuditService(
        nfe_dir=nfe_dir,
        nfce_dir=nfce_dir,
        sped_fiscal_path=sped_fiscal,
        sped_cofins_path=sped_cofins
    )

    assert service.nfe_dir == nfe_dir
    assert service.nfce_dir == nfce_dir
    assert service.sped_fiscal_path == sped_fiscal
    assert service.sped_cofins_path == sped_cofins


@patch("src.services.audit_service.ExportService")
@patch("src.services.audit_service.FiscalRepository")
@patch("src.services.audit_service.DisposableAuditDatabase")
@patch("src.services.audit_service.XmlParser.get_xml_files")
@patch("src.services.audit_service.SpedParser")
def test_run_pipeline_with_only_sped_cofins(
    mock_sped_parser,
    mock_get_xml_files,
    mock_db,
    mock_repo,
    mock_export_service,
    mock_paths,
    tmp_path,
):
    sped_cofins_file = tmp_path / "sped_cofins.txt"
    sped_cofins_file.touch()
    
    mock_sped_instance = MagicMock()
    mock_sped_instance.parse_sped.return_value = [("SPED_COFINS_NOTE_1",)]
    mock_sped_instance.get_enterprise.return_value = "EMPRESA_COFINS_LTDA"
    mock_sped_parser.return_value.__enter__.return_value = mock_sped_instance
    
    mock_get_xml_files.return_value = []

    service = AuditService(
        nfe_dir=None,
        nfce_dir=None,
        sped_fiscal_path=None,
        sped_cofins_path=sped_cofins_file
    )
    service.run_pipeline()

    mock_db.assert_called_once_with(enterprise="EMPRESA_COFINS_LTDA")
    
    repo_instance = mock_repo.return_value.__enter__.return_value
        
    repo_instance.add_sped.assert_called_once_with([("SPED_COFINS_NOTE_1",)])


@patch("src.services.audit_service.ExportService")
@patch("src.services.audit_service.FiscalRepository")
@patch("src.services.audit_service.DisposableAuditDatabase")
@patch("src.services.audit_service.XmlParser")
@patch("src.services.audit_service.SpedParser")
def test_run_pipeline_fallback_enterprise_name(
    mock_sped_parser,
    mock_xml_parser,
    mock_db,
    mock_repo,
    mock_export_service,
    mock_paths,
):
    mock_sped_instance = MagicMock()
    mock_sped_instance.fiscal_notes = []
    mock_sped_instance.get_enterprise.return_value = None
    mock_sped_parser.return_value.__enter__.return_value = mock_sped_instance

    mock_xml_parser.get_xml_files.return_value = []

    service = AuditService(
        nfe_dir=None,
        nfce_dir=None,
        sped_fiscal_path=None,
        sped_cofins_path=None
    )
    result = service.run_pipeline()

    mock_db.assert_called_once_with(enterprise="EMPRESA_DESCONHECIDA")
    expected_output_path = mock_paths.outputs_dir / "relatorio_auditoria_EMPRESA_DESCONHECIDA.xlsx"

    assert result["excel_path"] == expected_output_path


@patch("src.services.audit_service.ProcessPoolExecutor")
@patch("src.services.audit_service.XmlParser")
@patch("src.services.audit_service.SpedParser")
def test_audit_service_real_pipeline_execution(
    mock_sped_parser, mock_xml_parser, mock_executor_class, mock_paths, tmp_path
):
    mock_executor = MagicMock()
    mock_executor.__enter__.return_value = mock_executor
    mock_executor.map.side_effect = lambda func, iterable, **kwargs: [func(x) for x in iterable]
    mock_executor_class.return_value = mock_executor
    
    mock_sped_instance = MagicMock()
    mock_sped_instance.get_enterprise.return_value = "EMPRESA TESTE REAL SA"
        
    mock_sped_instance.parse_sped.return_value = [
        (
            "31240112345678000195550010000123451000123456",
            "12345678000195",
            10000,
            "2026-09-17",
            55,
            "00",
            "EFD_ICMS_IPI"
        )
    ]
    mock_sped_parser.return_value.__enter__.return_value = mock_sped_instance
    
    fake_doc_tuple = (
        "31240112345678000195550010000123451000123456",
        "12345678000195",
        10000,
        "2026-09-17",
        55,
        "00"
    )
    
    mock_xml_parser.get_xml_files.return_value = [tmp_path / "nfe.xml"]
    mock_xml_parser.parse_xml_to_tuple.return_value = fake_doc_tuple
    
    mock_paths.schema_path.write_text("""
        CREATE TABLE IF NOT EXISTS xml_documents (
            access_key VARCHAR PRIMARY KEY,
            cnpj_emit VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            nfe_model INT,
            document_status VARCHAR
            );
        CREATE TABLE IF NOT EXISTS sped_documents (
            access_key VARCHAR,
            cnpj_emit VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            nfe_model INT,
            document_status VARCHAR,
            sped_type VARCHAR,
            PRIMARY KEY (access_key, sped_type)
        );
    """, encoding="utf-8")
    
    (mock_paths.queries_dir / "audit.sql").write_text("""
        SELECT access_key AS chave, total_value AS valor FROM xml_documents
        UNION ALL
        SELECT access_key AS chave, total_value AS valor FROM sped_documents;
    """, encoding="utf-8")
    
    sped_fiscal_file = tmp_path / "sped.txt"
    sped_fiscal_file.touch()
    
    service = AuditService(
        nfe_dir=tmp_path,
        nfce_dir=None,
        sped_fiscal_path=sped_fiscal_file,
        sped_cofins_path=None
    )
    service.run_pipeline()
    
    expected_excel = mock_paths.outputs_dir / "relatorio_auditoria_EMPRESA TESTE REAL SA.xlsx"
    assert expected_excel.exists(), "O arquivo Excel não foi gerado no disco!"
    
    wb = load_workbook(expected_excel)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    
    assert len(rows) > 1, f"Relatório vazio! Linhas encontradas: {len(rows)}"
    assert len(rows) == 5