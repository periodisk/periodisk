"""Validate source-tree resources without installing the package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from periodisk.cli import main

raise SystemExit(main(["validate", "--release"]))
