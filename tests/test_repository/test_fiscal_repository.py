import pandas as pd
import pytest

from src.repositories.fiscal_repository import FiscalRepository


@pytest.fixture
def sample_xml_data() -> list[tuple]:
    return [
        (
            "12345678000195",
            15055,
            "2023-01-01",
            "Exit",
            "Authorized",
            "NFe",
            "1",
            "35230112345678000195550010000000011234567890",
        ),
        (
            "12345678000195",
            20000,
            "2023-01-02",
            "Exit",
            "Authorized",
            "NFe",
            "2",
            "35230112345678000195550010000000021234567890",
        ),
    ]


@pytest.fixture
def sample_sped_data() -> list[tuple]:
    return [
        (
            "12345678000195",
            15055,
            "2023-01-01",
            "Exit",
            "Authorized",
            "NFe",
            "1",
            "35230112345678000195550010000000011234567890",
            "EFD_ICMS_IPI",
        )
    ]


@pytest.fixture
def sample_sintegra_data() -> list[tuple]:
    return [
        (
            "12345678000195",
            15055,
            "2023-01-01",
            "Exit",
            "Authorized",
            "NFe",
            "1",
        )
    ]


def test_initialization_sped():
    repo = FiscalRepository(is_sped=True)
    assert repo.is_sped is True
    assert repo.fiscal_archive_type == "SPED"
    assert repo.xml_data_hub == []
    assert repo.fiscal_archive_data_hub == []


def test_initialization_sintegra():
    repo = FiscalRepository(is_sped=False)
    assert repo.is_sped is False
    assert repo.fiscal_archive_type == "SINTEGRA"


def test_add_xml_and_fiscal_archive(sample_xml_data, sample_sped_data):
    repo = FiscalRepository(is_sped=True)
    repo.add_xml(sample_xml_data)
    repo.add_fiscal_archive(sample_sped_data)

    assert len(repo.xml_data_hub) == 2
    assert len(repo.fiscal_archive_data_hub) == 1


def test_prepare_data_frames_sped(sample_xml_data, sample_sped_data):
    repo = FiscalRepository(is_sped=True)
    repo.add_xml(sample_xml_data)
    repo.add_fiscal_archive(sample_sped_data)

    df_xml, df_fiscal = repo.prepare_data_frames()

    assert isinstance(df_xml, pd.DataFrame)
    assert isinstance(df_fiscal, pd.DataFrame)

    assert "access_key" in df_xml.columns
    assert "sped_type" in df_fiscal.columns
    assert len(df_xml) == 2
    assert len(df_fiscal) == 1


def test_prepare_data_frames_sintegra(sample_xml_data, sample_sintegra_data):
    repo = FiscalRepository(is_sped=False)
    repo.add_xml(sample_xml_data)
    repo.add_fiscal_archive(sample_sintegra_data)

    df_xml, df_fiscal = repo.prepare_data_frames()

    assert "sped_type" not in df_fiscal.columns
    assert list(df_fiscal.columns) == [
        "cnpj_issuer",
        "total_value",
        "emission_date",
        "operation_type",
        "document_status",
        "nfe_model",
        "document_number",
    ]


def test_calculate_metrics(sample_xml_data, sample_sped_data):
    repo = FiscalRepository(is_sped=True)
    repo.add_xml(sample_xml_data)
    repo.add_fiscal_archive(sample_sped_data)

    df_xml, df_fiscal = repo.prepare_data_frames()
    metrics = repo.calculate_metrics(df_xml, df_fiscal)

    assert "xmls" in metrics
    assert "fiscal_archives" in metrics

    assert metrics["xmls"]["qty"] == 2
    assert metrics["xmls"]["val"] == 35055

    assert metrics["fiscal_archives"]["qty"] == 1
    assert metrics["fiscal_archives"]["val"] == 15055


def test_calculate_metrics_empty_dataframes():
    repo = FiscalRepository(is_sped=True)
    df_xml, df_fiscal = repo.prepare_data_frames()

    metrics = repo.calculate_metrics(df_xml, df_fiscal)

    assert metrics["xmls"]["qty"] == 0
    assert metrics["xmls"]["val"] == 0
    assert metrics["fiscal_archives"]["qty"] == 0
    assert metrics["fiscal_archives"]["val"] == 0