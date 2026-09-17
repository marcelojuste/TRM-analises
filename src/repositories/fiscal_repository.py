from typing import List, Tuple

from src.database.database import DisposableAuditDatabase

class FiscalRepository:

    def __init__(self):
        self.xml_batch: List[Tuple] = []
        self.sped_batch: List[Tuple] = []
        self._conn = None

    def set_conn(self, database: DisposableAuditDatabase):
        self._conn = database.get_conn()

    def _flush_xmls(self) -> None:
        if not self._conn:
            ConnectionError("Conexão com o banco não encontrada")

        if self.xml_batch:
            self._conn.executemany(
                "INSERT INTO xml_documents VALUES (?, ?)", 
                self.xml_batch
            )
            self.xml_batch.clear()

    def _flush_speds(self) -> None:
        if not self._conn:
            ConnectionError("Conexão com o banco não encontrada")

        if self.sped_batch:
            self._conn.executemany(
                "INSERT INTO sped_documents Values(?, ?, ?, ?)",
                self.sped_batch
            )
            self.sped_batch.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush_xmls()
        self._flush_speds()
