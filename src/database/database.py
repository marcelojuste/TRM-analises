import os
import shutil
import duckdb
from typing import Optional

from src.app_paths import PATHS

class DisposableAuditDatabase:
    def __init__(self, enterprise: str, memory_limit: str = "1GB"):
        self.enterprise = enterprise
        self.db_path = PATHS.get_enterprise_db_path(enterprise)
        self.memory_limit = memory_limit
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    def get_conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            raise RuntimeError(
                "A conexão com o banco não está ativa. Utilize a classe dentro de um bloco 'with'."
            )
        return self._conn

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        self._purge_temp_dir()
        PATHS.temp_files_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._conn = duckdb.connect(database=str(self.db_path))
            self._conn.execute(f"SET memory_limit = '{self.memory_limit}';")
            self._conn.execute("SET threads = 2;")

            if PATHS.schema_path.exists():
                schema_sql = PATHS.schema_path.read_text(encoding="utf-8")
                self._conn.execute(schema_sql)

        except Exception as e:
            self._close_connection()
            self._purge_temp_dir()
            raise RuntimeError(f"Erro ao inicializar o banco de dados descartável: {e}") from e

        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._close_connection()
        self._purge_temp_dir()

    def _close_connection(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None

    def _purge_temp_dir(self) -> None:
        if not PATHS.temp_files_dir.exists():
            return

        for item in PATHS.temp_files_dir.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    os.remove(item)
            except OSError:
                pass
