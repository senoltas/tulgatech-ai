import json
from pathlib import Path
from typing import Any, Dict, Optional


class JSONReport:
    """JSON rapor formatı"""

    def __init__(self, out_dir: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parents[2]  # tulgatech_ai kök
        self.out_dir = out_dir or (base_dir / "reports")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: Dict[str, Any], filename: str) -> Path:
        if not filename.lower().endswith(".json"):
            filename += ".json"

        path = self.out_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
