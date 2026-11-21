"""Validate the in-repo config and the synthetic example files.

Scaffolding version: checks that each file present parses as YAML. Pydantic model
validation (and `checks`) is wired in by tasks 2.1/2.2.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    ROOT / "config" / "pipeline.yaml",
    ROOT / "examples" / "companies.example.yaml",
    ROOT / "examples" / "screening.example.yml",
    ROOT / "examples" / "profile.example.yml",
]


def main() -> int:
    failed = False
    for path in FILES:
        rel = path.relative_to(ROOT)
        if not path.exists():
            print(f"skip  {rel} (not created yet)")
            continue
        try:
            yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            failed = True
            print(f"FAIL  {rel}: {exc}")
        else:
            print(f"ok    {rel}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
