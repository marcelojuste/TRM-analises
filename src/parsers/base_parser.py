from pathlib import Path
from typing import Generator, Optional

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

    def _read_lines(self) -> Generator[str, None, None]:
        if not self.file_path or not self.file_path.exists():
            return

        encoding = self._detect_encoding()
        with open(self.file_path, "r", encoding=encoding, errors="replace") as file_stream:
            for line in file_stream:
                stripped_line = line.strip()
                if stripped_line:
                    yield stripped_line

    @staticmethod
    def _convert_to_cents(amount_str: str) -> int:
        if not amount_str:
            return 0
        try:
            amount_float = float(amount_str.replace(",", "."))
            return int(round(amount_float * 100))
        except (ValueError, TypeError):
            return 0

    @property
    def enterprise(self) -> str:
        return self.company_name or "EMPRESA_DESCONHECIDA"