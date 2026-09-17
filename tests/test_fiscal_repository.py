import pytest
import duckdb
from src.repositories.fiscal_repository import FiscalRepository

@pytest.fixture
def db_conn():
    """Cria uma conexão em memória com as tabelas necessárias para cada teste."""
    conn = duckdb.connect(":memory:")
    
    conn.execute("""
        CREATE TABLE xml_documents (
            access_key VARCHAR,
            total_value BIGINT
        );
    """)
    
    conn.execute("""
        CREATE TABLE sped_documents (
            access_key VARCHAR,
            total_value BIGINT,
            emission_date VARCHAR,
            sped_type VARCHAR
        );
    """)
    
    yield conn
    conn.close()


def test_add_xml_acumula_em_memoria_sem_descarregar(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=5)

    repo.add_xml(("CHAVE_1", 1000))
    repo.add_xml(("CHAVE_2", 2000))

    # Garante que os dados ainda estão na lista e nada foi para o banco
    assert len(repo.xml_batch) == 2
    
    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 0


def test_add_xml_descarrega_ao_atingir_batch_size(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=2)

    repo.add_xml(("CHAVE_1", 1000))
    assert len(repo.xml_batch) == 1

    # Ao adicionar o 2º item, atinge o limite do lote e faz o flush automático
    repo.add_xml(("CHAVE_2", 2000))

    assert len(repo.xml_batch) == 0  # Lista limpa em RAM

    count = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    assert count == 2


"""def test_add_sped_descarrega_ao_atingir_batch_size(db_conn):
    repo = FiscalRepository(conn=db_conn, batch_size=2)

    repo.add_sped(("CHAVE_1", 1000, "2026-09-01", "SPED_FISCAL"))
    repo.add_sped(("CHAVE_2", 2000, "2026-09-02", "SPED_FISCAL"))

    assert len(repo.sped_batch) == 0  # Lote limpo após flush

    count = db_conn.execute("SELECT COUNT(*) FROM sped_documents").fetchone()[0]
    assert count == 2"""


"""def test_context_manager_descarrega_sobras_ao_sair(db_conn):
    # Batch size grande (10) para garantir que os itens fiquem na memória
    with FiscalRepository(conn=db_conn, batch_size=10) as repo:
        repo.add_xml(("CHAVE_1", 1000))
        repo.add_sped(("CHAVE_2", 2000, "2026-09-01", "SPED_FISCAL"))
        
        # Antes de sair do bloco, os dados ainda estão nos lotes em RAM
        assert len(repo.xml_batch) == 1
        assert len(repo.sped_batch) == 1

    # Ao sair do bloco 'with', o __exit__ força o flush dos itens pendentes
    count_xml = db_conn.execute("SELECT COUNT(*) FROM xml_documents").fetchone()[0]
    count_sped = db_conn.execute("SELECT COUNT(*) FROM sped_documents").fetchone()[0]

    assert count_xml == 1
    assert count_sped == 1
    assert len(repo.xml_batch) == 0
    assert len(repo.sped_batch) == 0"""