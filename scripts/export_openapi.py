from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND))

from app.main import app  # noqa: E402


def main() -> None:
    output_dir = ROOT / "docs" / "openapi"
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    (output_dir / "openapi.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        import yaml
    except ModuleNotFoundError:
        (output_dir / "openapi.yaml").write_text(
            "# Install pyyaml to export YAML. JSON schema is available in openapi.json.\n",
            encoding="utf-8",
        )
        return
    (output_dir / "openapi.yaml").write_text(yaml.safe_dump(schema, allow_unicode=True, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
