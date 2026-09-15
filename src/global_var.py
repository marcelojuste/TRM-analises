from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "trm_analises.db"
SCHEMA_PATH = BASE_DIR / "database" / "sql" / "schema.sql"

FILE_ENCODING = "utf-8"

INSERT_NFE_PATH = BASE_DIR / "database" / "sql" / "insert_nfe.sql"
INSERT_SPED_COFINS_PATH = BASE_DIR / "database" / "sql" / "insert_sped_cofins.sql"
INSERT_SPED_IPI_PATH = BASE_DIR / "database" / "sql" / "insert_sped_ipi.sql"
QUERY_AUDIT_PATH = BASE_DIR / "database" / "sql" / "audit_query.sql"
