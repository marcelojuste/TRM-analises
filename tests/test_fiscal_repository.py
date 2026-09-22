import pytest
import duckdb
from src.repositories.fiscal_repository import FiscalRepository

@pytest.fixture
def db_conn():
    conn = duckdb.connect(":memory:")

    conn.execute("""
        CREATE TABLE xml_documents (
            access_key VARCHAR,
            cnpj_emit VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            nfe_model INTEGER,
            document_status VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE sped_documents (
            access_key VARCHAR,
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


def test_add_xml_acumula_em_memoria_sem_descarregar(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=5)

    repo.add_xml(("CHAVE_1", "12345678901234", 1000, "2026-09-22", 55, "00"))
    repo.add_xml(("CHAVE_2", "12345678901234", 2000, "2026-09-22", 55, "00"))

    assert len(repo.xml_batch) == 2
    
    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 0


def test_add_xml_descarrega_ao_atingir_batch_size(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=2)

    repo.add_xml(("CHAVE_1", "12345678901234", 1000, "2026-09-22", 55, "00"))
    assert len(repo.xml_batch) == 1

    repo.add_xml(("CHAVE_2", "12345678901234", 2000, "2026-09-22", 55, "00"))

    assert len(repo.xml_batch) == 0 

    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 2


def test_add_sped_atribui_lista_sem_descarregar_automaticamente(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=2)

    lista_sped = [
        ("CHAVE_1", "12345678901234", 1000, "2026-09-22", 55, "00", "SPED_FISCAL"),
        ("CHAVE_2", "12345678901234", 2000, "2026-09-22", 55, "00", "SPED_FISCAL")
    ]
    
    repo.add_sped(lista_sped)

    assert len(repo.sped_batch) == 2

    count = db_conn.execute("SELECT COUNT(*) FROM sped_documents").fetchone()[0]
    assert count == 0


def test_context_manager_descarrega_sobras_ao_sair(db_conn):
    with FiscalRepository(conn=db_conn, batch_size=10) as repo:
        repo.add_xml(("CHAVE_1", "12345678901234", 1000, "2026-09-22", 55, "00"))
        
        lista_sped = [("CHAVE_SPED", "12345678901234", 2000, "2026-09-22", 55, "00", "SPED_FISCAL")]
        repo.add_sped(lista_sped)

        assert len(repo.xml_batch) == 1
        assert len(repo.sped_batch) == 1

    count_xml = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    count_sped = db_conn.execute("SELECT COUNT(*) FROM sped_documents").fetchone()[0]

    assert count_xml == 1
    assert count_sped == 1
    assert len(repo.xml_batch) == 0
    assert len(repo.sped_batch) == 0