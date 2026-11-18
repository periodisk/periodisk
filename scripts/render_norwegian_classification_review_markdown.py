"""Render the Norwegian classification-term review as a Markdown table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REVIEW = Path("curation/norwegian_terminology/classifications.json")
DEFAULT_OUTPUT = Path("curation/norwegian_terminology/CLASSIFICATIONS_TABLE.md")

SOURCE_LABELS = {
    "naob": "NAOB",
    "bokmaalsordboka": "BM",
    "snl": "SNL",
    "iupac-red-book-2005": "IUPAC 2005",
    "chebi": "ChEBI",
    "wikipedia-no": "no.wp",
    "wikipedia-en": "en.wp",
}

MODE_HEADINGS = {
    "detailed": "Detailed classification",
    "broad": "Broad classification",
}


def _escape(text: str) -> str:
    return text.replace("|", "&#124;").replace("\n", " ")


def _row(term: dict[str, Any]) -> str:
    links = " · ".join(
        f"[{SOURCE_LABELS[source['source']]}: {_escape(source['entry'])}]"
        f"({source['url']})"
        for source in term["sources"]
    )
    not_listed = ", ".join(SOURCE_LABELS[source] for source in term["not_listed"])
    scope = ", ".join(term.get("members") or term.get("includes", []))
    decision = term["decision"].capitalize()
    if "previous_term" in term:
        decision += f" (was {_escape(term['previous_term'])})"
    return (
        f"| `{term['key']}` | {_escape(term['reviewed_term'])} | {decision} "
        f"| {scope} | {links} | {not_listed or '—'} | {_escape(term['notes'])} |"
    )


def render(review: dict[str, Any]) -> str:
    lines = [
        "# Norwegian classification-term review",
        "",
        "This file is generated from [`classifications.json`](classifications.json).",
        "Do not edit it directly. See the [curation README](README.md) for the scope",
        "and method.",
        "",
        "BM denotes Bokmålsordboka. **Not listed** names sources that were searched",
        "but have no entry for the term.",
    ]
    for mode, heading in MODE_HEADINGS.items():
        lines += [
            "",
            f"## {heading}",
            "",
            "| Key | Reviewed term | Decision | Scope | Sources | Not listed | Notes |",
            "|---|---|---|---|---|---|---|",
        ]
        lines += [_row(term) for term in review["terms"] if term["mode"] == mode]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    args.output.write_text(render(review), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
