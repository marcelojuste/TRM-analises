import pytest
import duckdb
from src.repositories.fiscal_repository import FiscalRepository

import pytest
import duckdb
from src.repositories.fiscal_repository import FiscalRepository

@pytest.fixture
def db_conn():
    conn = duckdb.connect(":memory:")

    conn.execute("""
        CREATE TABLE xml_documents (
            access_key VARCHAR PRIMARY KEY,
            cnpj_emit VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            nfe_model INTEGER,
            document_status VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE sped_documents (
            access_key VARCHAR PRIMARY KEY,
            cnpj_emit VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            nfe_model INTEGER,
            document_status VARCHAR,
            sped_type VARCHAR
        );
    """)
    
    yield conn
    conn.close()

def test_add_xml_accumulates_in_memory_without_flushing(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=5)

    repo.add_xml(("KEY_1", "12345678901234", 1000, "2026-09-22", 55, "00"))
    repo.add_xml(("KEY_2", "12345678901234", 2000, "2026-09-22", 55, "00"))

    assert len(repo.xml_batch) == 2
    
    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 0


def test_add_xml_flushes_when_batch_size_reached(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=2)

    repo.add_xml(("KEY_1", "12345678901234", 1000, "2026-09-22", 55, "00"))
    assert len(repo.xml_batch) == 1

    repo.add_xml(("KEY_2", "12345678901234", 2000, "2026-09-22", 55, "00"))

    assert len(repo.xml_batch) == 0 

    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 2


def test_metrics_ignore_cancelled_documents(db_conn):
    with FiscalRepository(conn=db_conn, batch_size=10) as repo:
        repo.add_xml(("KEY_1", "12345678901234", 10000, "2026-09-22", 55, "00"))
        repo.add_xml(("KEY_2", "12345678901234", 5000, "2026-09-22", 55, "02"))

        repo.add_sped([
            ("KEY_S1", "12345678901234", 20000, "2026-09-22", 55, "00", "EFD_ICMS_IPI"),
            ("KEY_S2", "12345678901234", 3000, "2026-09-22", 55, "02", "EFD_ICMS_IPI")
        ])

    repo = FiscalRepository(conn=db_conn)
    xml_metrics = repo.get_xml_metrics()
    sped_metrics = repo.get_sped_metrics()

    assert xml_metrics == {"qty": 1, "val": 100.0}
    assert sped_metrics == {"qty": 1, "val": 200.0}