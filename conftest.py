import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.resolve()

if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))