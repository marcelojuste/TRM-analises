class FiscalRepository:
    def __init__(self, conn, batch_size=1000):
        self.conn = conn
        self.batch_size = batch_size
        self.xml_batch = []
        self.sped_batch = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush_xmls()
        self._flush_speds()

    def add_xml(self, xml_tuple: tuple) -> None:
        self.xml_batch.append(xml_tuple)
        if len(self.xml_batch) >= self.batch_size:
            self._flush_xmls()

    def add_sped(self, sped_tuples: list | list[tuple]) -> None:
        self.sped_batch.extend(sped_tuples)
        if len(self.sped_batch) >= self.batch_size:
            self._flush_speds()

    def _flush_xmls(self) -> None:
        if not self.xml_batch:
            return
        try:
            self.conn.executemany(
                "INSERT INTO xml_documents VALUES (?, ?, ?, ?, ?, ?)", 
                self.xml_batch
            )
        except Exception as e:
            print(f"❌ Erro ao inserir XMLs no banco: {e}")
            raise e
        finally:
            self.xml_batch.clear()

    def _flush_speds(self) -> None:
        if not self.sped_batch:
            return
        try:
            self.conn.executemany(
                "INSERT INTO sped_documents VALUES (?, ?, ?, ?, ?, ?, ?)", 
                self.sped_batch
            )
        except Exception as e:
            print(f"❌ Erro ao inserir SPEDs no banco: {e}")
            raise e
        finally:
            self.sped_batch.clear()