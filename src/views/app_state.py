from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd


@dataclass
class AppState:
    is_sped_mode: bool = True
    is_running: bool = False
    xml_paths: List[Path] = field(default_factory=list)
    fiscal_paths: List[Path] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    audit_results: Optional[pd.DataFrame] = None
    enterprise_name: str = "EMPRESA_DESCONHECIDA"

    def reset_paths_and_metrics(self):
        self.xml_paths.clear()
        self.fiscal_paths.clear()
        self.metrics.clear()
        self.audit_results = None
        self.enterprise_name = "EMPRESA_DESCONHECIDA"

    def set_mode(self, is_sped: bool):
        self.is_sped_mode = is_sped
        if not is_sped and len(self.fiscal_paths) > 1:
            self.fiscal_paths = self.fiscal_paths[:1]