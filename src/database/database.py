from pathlib import Path
import os
import shutil
import duckdb

from src.app_paths import PATHS


class DisposableAuditDatabase:
    def __init__(self, enterprise: str, memory_limit: str = "1GB"):
        self.enterprise = enterprise
        self.db_path = PATHS.get_enterprise_db_path(enterprise)
        self.memory_limit = memory_limit
        self._conn = None

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        # 1. Garante que qualquer resíduo anterior na pasta temp_files seja removido
        self._purge_temp_dir()
        PATHS.temp_files_dir.mkdir(parents=True, exist_ok=True)

        # 2. Conecta ao DuckDB dentro da pasta limpa
        self._conn = duckdb.connect(database=str(self.db_path))

        # 3. Limites de hardware (Windows 7 / 4 GB RAM)
        self._conn.execute(f"SET memory_limit = '{self.memory_limit}';")
        self._conn.execute("SET threads = 2;")

        # 4. Executa DDL do schema se existir
        if PATHS.schema_path.exists():
            try:
                schema_sql = PATHS.schema_path.read_text(encoding="utf-8")
                self._conn.execute(schema_sql)
            except Exception as e:
                if self._conn:
                    self._conn.close()
                    self._conn = None
                self._purge_temp_dir()
                raise RuntimeError(f"Erro ao carregar o schema do banco de dados: {e}") from e

        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
            self._conn = None

        self._purge_temp_dir()

    def _purge_temp_dir(self) -> None:
        """Limpa todo o conteúdo de temp_files_dir de forma segura."""
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
            