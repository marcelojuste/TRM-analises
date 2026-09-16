import re
from pathlib import Path
from typing import Iterator, Tuple, Union


def parse_sped(file_path: Union[str, Path]) -> Iterator[Tuple[str, int]]:
    path_obj = Path(file_path) if isinstance(file_path, str) else file_path

    with open(path_obj, mode="r", encoding="latin-1") as file:
        for line in file:
            clean_line = line.strip()
            if not clean_line.startswith("|C100|"):
                continue

            fields = clean_line.split("|")

            if len(fields) < 10 or fields[6] != "00":
                continue

            try:
                operation_type = int(fields[2])
            except ValueError:
                continue

            nfe_candidate = fields[9].strip() if len(fields) > 9 else ""

            if len(nfe_candidate) == 44 and nfe_candidate.isdigit():
                nfe_key = nfe_candidate
            else:
                match = re.search(r"\b\d{44}\b", clean_line)
                if match:
                    nfe_key = match.group(0)
                else:
                    nfe_key = fields[8].strip() if len(fields) > 8 else ""

            if nfe_key:
                yield nfe_key, operation_type
