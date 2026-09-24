from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True, frozen=True)
class AppPaths:
    root_dir: Path
    database_dir: Path
    queries_dir: Path
    schema_path: Path
    temp_files_dir: Path
    images_dir: Path
    icons_dir: Path
    outputs_dir: Path

    @classmethod
    def from_root(cls) -> "AppPaths":
        src_dir = Path(__file__).parent.resolve()
        base_dir = src_dir.parent

        db_dir = src_dir / "database"
        queries_dir = db_dir / "queries"

        return cls(
            root_dir=base_dir,
            database_dir=db_dir,
            queries_dir=queries_dir,
            schema_path=queries_dir / "schema.sql",
            temp_files_dir=src_dir / "temp_files",
            images_dir=src_dir / "views" / "assets" / "images",
            icons_dir=src_dir / "views" / "assets" / "icons",
            outputs_dir=src_dir / "outputs",
        )

    def get_enterprise_db_path(self, enterprise: str) -> Path:
        return self.temp_files_dir / f"audit_{enterprise}.duckdb"


PATHS = AppPaths.from_root()