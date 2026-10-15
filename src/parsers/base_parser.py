from pathlib import Path
from typing import Optional


class FiscalDocumentBaseModelParser:

    SUPPORTED_ENCODINGS = ("utf-8", "latin-1", "utf-8-sig")
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_FALLBACK_ENCODING = "latin-1"
    BUFFER_SIZE_BYTES = 4096

    def __init__(self, archive_path: Optional[Path] = None):
        self.file_path: Optional[Path] = archive_path
        self._detected_encoding: Optional[str] = None
        self.company_name: Optional[str] = None

    def _detect_encoding(self) -> str:
        if self._detected_encoding:
            return self._detected_encoding

        if not self.file_path or not self.file_path.exists():
            return self.DEFAULT_ENCODING

        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                with open(self.file_path, "r", encoding=encoding) as file_stream:
                    file_stream.read(self.BUFFER_SIZE_BYTES)
                self._detected_encoding = encoding
                return encoding
            except UnicodeDecodeError:
                continue

        self._detected_encoding = self.DEFAULT_FALLBACK_ENCODING
        return self._detected_encoding

    @staticmethod
    def _convert_to_cents(amount_str: str) -> int:
        if not amount_str:
            return 0
        try:
            amount_float = float(amount_str.replace(",", "."))
            return int(round(amount_float * 100))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _format_date(raw_date: str) -> str:
        if len(raw_date) == 8 and raw_date.isdigit():
            day, month, year = raw_date[0:2], raw_date[2:4], raw_date[4:8]
            return f"{year}-{month}-{day}"
        return "1900-01-01"

    @property
    def enterprise(self) -> str:
        return self.company_name or "EMPRESA_DESCONHECIDA"