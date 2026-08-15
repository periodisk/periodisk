import importlib.util
import inspect
import re
import tomllib
from pathlib import Path

import periodisk

ROOT = Path(__file__).parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
DOCUMENTATION_ROOTS = (
    ROOT / "README.md",
    ROOT / "LICENSE-CONTENT.md",
    ROOT / "THIRD_PARTY_NOTICES.md",
    ROOT / "docs",
    ROOT / "examples",
    ROOT / "curation",
)


def _documentation_files() -> list[Path]:
    documents: list[Path] = []
    for path in DOCUMENTATION_ROOTS:
        documents.extend(path.rglob("*.md") if path.is_dir() else [path])
    return documents


def test_local_markdown_links_resolve() -> None:
    missing: list[str] = []
    for document in _documentation_files():
        text = document.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            path = target.split("#", 1)[0]
            if not (document.parent / path).exists():
                line = text.count("\n", 0, match.start()) + 1
                missing.append(f"{document.relative_to(ROOT)}:{line}: {target}")

    assert missing == []


def test_package_version_matches_project_metadata() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert periodisk.__version__ == metadata["project"]["version"]


def test_rendering_entry_points_are_top_level_functions() -> None:
    for name in ("render_svg", "render_pdf", "render_table"):
        assert inspect.isfunction(getattr(periodisk, name))
    assert importlib.util.find_spec("periodisk.render_svg") is None
    assert importlib.util.find_spec("periodisk.render_pdf") is None
