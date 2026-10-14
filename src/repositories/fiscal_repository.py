import pandas as pd

class FiscalRepository:
    def __init__(self, conn, batch_size: int = 100000):
        self.conn = conn
        self.batch_size = batch_size
        self.xml_batch = []
        self.sped_batch = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush_xmls()
        self._flush_speds()

    def add_xml(self, xml_tuples: list | list[tuple] | tuple) -> None:
        if isinstance(xml_tuples, list):
            self.xml_batch.extend(xml_tuples)
        elif isinstance(xml_tuples, tuple):
            self.xml_batch.append(xml_tuples)

        if len(self.xml_batch) >= self.batch_size:
            self._flush_xmls()

    def add_sped(self, sped_tuples: list | list[tuple] | tuple) -> None:
        if isinstance(sped_tuples, list):
            self.sped_batch.extend(sped_tuples)
        elif isinstance(sped_tuples, tuple):
            self.sped_batch.append(sped_tuples)

        if len(self.sped_batch) >= self.batch_size:
            self._flush_speds()

    def _flush_xmls(self) -> None:
        if not getattr(self, 'xml_batch', None):
            return

        try:
            df_xml = pd.DataFrame(self.xml_batch, columns=[
                "access_key", "cnpj_emit", "total_value", 
                "emission_date", "nfe_model", "document_status"
            ])

            self.conn.execute("""
                INSERT INTO xml_documents 
                SELECT * FROM df_xml;
            """)

        except Exception as e:
            print(f"❌ Erro ao inserir XMLs no banco: {e}")
            raise e
        finally:
            self.xml_batch.clear()

    def _flush_speds(self) -> None:
        if not getattr(self, 'sped_batch', None):
            return

        try:
            df_sped = pd.DataFrame(self.sped_batch, columns=[
                "access_key", "cnpj_emit", "total_value", 
                "emission_date", "nfe_model", "document_status", "sped_type"
            ])

            self.conn.execute("""
                INSERT OR IGNORE INTO sped_documents 
                SELECT * FROM df_sped;
            """)

        except Exception as e:
            print(f"❌ Erro ao inserir SPEDs no banco: {e}")
            raise e
        finally:
            self.sped_batch.clear()

    def get_xml_metrics(self) -> dict:
        query = "SELECT COUNT(*), COALESCE(SUM(total_value), 0) / 100.0 FROM xml_documents WHERE document_status != '02';"
        qty, val = self.conn.execute(query).fetchone()
        return {"qty": qty or 0, "val": val or 0.0}

    def get_sped_metrics(self) -> dict:
        query = "SELECT COUNT(*), COALESCE(SUM(total_value), 0) / 100.0 FROM sped_documents WHERE document_status != '02';"
        qty, val = self.conn.execute(query).fetchone()
        return {"qty": qty or 0, "val": val or 0.0}