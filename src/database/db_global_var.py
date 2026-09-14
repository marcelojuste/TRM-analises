BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "trm_analises.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

FILE_ENCODING = "utf-8"

INSERT_NFE_PATH = BASE_DIR / "sql" / "insert_nfe.sql"
INSERT_SPED_COFINS_PATH = BASE_DIR / "sql" / "insert_sped_cofins.sql"
INSERT_SPED_IPI_PATH = BASE_DIR / "sql" / "insert_sped_ipi.sql"
QUERY_AUDIT_PATH = BASE_DIR / "sql" / "query_audit.sql"
