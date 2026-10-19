import duckdb
import pandas as pd
from src.path_manager import PATHS


class FiscalRepository:

    def __init__(self, is_sped: bool):
        self.is_sped = is_sped
        self.fiscal_archive_type = "SPED" if is_sped else "SINTEGRA"

        self.xml_data_hub: list[tuple] = []
        self.fiscal_archive_data_hub: list[tuple] = []

    def add_xml(self, xml: list[tuple]) -> None:
        self.xml_data_hub.extend(xml)

    def add_fiscal_archive(self, fiscal_archive: list[tuple]) -> None:
        self.fiscal_archive_data_hub.extend(fiscal_archive)

    def prepare_data_frames(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        cols_xml = [
            "cnpj_issuer",
            "total_value",
            "emission_date",
            "operation_type",
            "document_status",
            "nfe_model",
            "document_number",
            "access_key",
        ]

        df_xml = pd.DataFrame(self.xml_data_hub, columns=cols_xml)

        if self.is_sped:
            cols_fiscal = cols_xml + ["sped_type"]
        else:
            cols_fiscal = [
                "cnpj_issuer",
                "total_value",
                "emission_date",
                "operation_type",
                "document_status",
                "nfe_model",
                "document_number",
            ]

        df_fiscal = pd.DataFrame(self.fiscal_archive_data_hub, columns=cols_fiscal)

        return df_xml, df_fiscal

    def calculate_metrics(self, df_xml: pd.DataFrame, df_fiscal: pd.DataFrame) -> dict:
        query_sql = """
            SELECT 
                'xmls' AS type,
                COUNT(*) AS qty,
                COALESCE(SUM(total_value), 0) AS val
            FROM df_xml

            UNION ALL

            SELECT 
                'fiscal_archives' AS type,
                COUNT(*) AS qty,
                COALESCE(SUM(total_value), 0) AS val
            FROM df_fiscal;
        """

        con = duckdb.connect(database=":memory:")
        con.register("df_xml", df_xml)
        con.register("df_fiscal", df_fiscal)

        metrics_df = con.execute(query_sql).df()

        metrics = {}
        for _, row in metrics_df.iterrows():
            metrics[row["type"]] = {
                "qty": int(row["qty"]),
                "val": int(row["val"])
            }

        return metrics