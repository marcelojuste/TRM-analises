from pathlib import Path
import duckdb

class ExportService:
    @staticmethod
    def export_query_to_csv(
        conn: duckdb.DuckDBPyConnection, 
        sql_file_path: Path, 
        output_csv_path: Path,
        delimiter: str = ";"
    ) -> None:
        if not sql_file_path.exists():
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_file_path}")

        sql_query = sql_file_path.read_text(encoding="utf-8").strip()
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)

        copy_statement = f"COPY ({sql_query}) TO '{output_csv_path.as_posix()}' (HEADER, DELIMITER '{delimiter}');"
        conn.execute(copy_statement)