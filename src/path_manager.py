import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AppPaths:
    root_dir: Path
    src_dir: Path
    scripts_dir: Path
    sintegra_query_path: Path
    sped_query_path: Path
    assets_dir: Path
    images_dir: Path
    icons_dir: Path
    outputs_dir: Path

    @classmethod
    def from_root(cls) -> "AppPaths":
        if getattr(sys, "frozen", False):
            base_dir = Path(sys._MEIPASS).resolve()
            src_dir = base_dir / "src"
        else:
            current_file_dir = Path(__file__).parent.resolve()
            src_dir = current_file_dir if current_file_dir.name == "src" else current_file_dir.parent
            base_dir = src_dir.parent

        scripts_dir = src_dir / "repositories" / "scripts"
        assets_dir = src_dir / "views" / "assets"

        paths = cls(
            root_dir=base_dir,
            src_dir=src_dir,
            scripts_dir=scripts_dir,
            sintegra_query_path=scripts_dir / "sintegra_audit_query.sql",
            sped_query_path=scripts_dir / "sped_audit_query.sql",
            assets_dir=assets_dir,
            images_dir=assets_dir / "images",
            icons_dir=assets_dir / "icons",
            outputs_dir=src_dir / "outputs",
        )

        paths.ensure_directories()
        return paths

    def ensure_directories(self) -> None:
        directories_to_create = [
            self.outputs_dir,
            self.scripts_dir,
        ]
        for directory in directories_to_create:
            directory.mkdir(parents=True, exist_ok=True)


PATHS = AppPaths.from_root()