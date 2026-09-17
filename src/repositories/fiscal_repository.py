from typing import List, Tuple, Optional  # 1. Adicionado Optional aqui
import duckdb

from src.database.database import DisposableAuditDatabase


class FiscalRepository:
    def __init__(self, conn: Optional[duckdb.DuckDBPyConnection] = None, batch_size: int = 1000):
        self.xml_batch: List[Tuple] = []
        self.sped_batch: List[Tuple] = []
        self._conn = conn
        self.batch_size: int = batch_size

    def add_xml(self, xml_tuple: tuple) -> None:
        self.xml_batch.append(xml_tuple)

        if len(self.xml_batch) >= self.batch_size:
            self._flush_xmls()

    def add_sped(self, sped_tuple: tuple) -> None:
        self.sped_batch.append(sped_tuple)

        if len(self.sped_batch) >= self.sped_batch:
            self._flush_speds()

    def _flush_xmls(self) -> None:
        if self.xml_batch and self._conn:
        if not self._conn:
            ConnectionError("Conexão com o banco não encontrada")

        if self.xml_batch:
            self._conn.executemany(
                "INSERT INTO xml_documents VALUES (?, ?)", 
                self.xml_batch
            )
            self.xml_batch.clear()

    def _flush_speds(self) -> None:
        if self.sped_batch and self._conn:
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
