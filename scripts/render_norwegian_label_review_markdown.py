"""Render the Norwegian label and explanatory-text review as a Markdown table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REVIEW = Path("curation/norwegian_terminology/labels.json")
DEFAULT_OUTPUT = Path("curation/norwegian_terminology/LABELS_TABLE.md")

SOURCE_LABELS = {"naob": "NAOB", "bokmaalsordboka": "BM", "snl": "SNL"}
SECTION_HEADINGS = {
    "labels": "Labels",
    "source_notes": "Source notes",
    "units": "Units",
}


def _escape(text: str) -> str:
    # Rendered line breaks are shown as " / " so each row stays on one line.
    return text.replace("|", "&#124;").replace("\n", " / ")


def _row(item: dict[str, Any]) -> str:
    links = " · ".join(
        f"[{SOURCE_LABELS[source['source']]}: {_escape(source['entry'])}]"
        f"({source['url']})"
        for source in item["sources"]
    )
    not_listed = ", ".join(SOURCE_LABELS[source] for source in item["not_listed"])
    decision = item["decision"].capitalize()
    if "previous_text" in item:
        decision += f" (was {_escape(item['previous_text'])})"
    return (
        f"| `{item['key']}` | {_escape(item['reviewed_text'])} | {decision} "
        f"| {links or '—'} | {not_listed or '—'} | {_escape(item['notes'])} |"
    )


def render(review: dict[str, Any]) -> str:
    lines = [
        "# Norwegian label and explanatory-text review",
        "",
        "This file is generated from [`labels.json`](labels.json). Do not edit it",
        "directly. See the [curation README](README.md) for the scope and method.",
        "",
        "BM denotes Bokmålsordboka. **Not listed** names sources that were searched",
        "but have no entry for the term. A ` / ` marks a rendered line break.",
    ]
    for section, heading in SECTION_HEADINGS.items():
        lines += [
            "",
            f"## {heading}",
            "",
            "| Key | Reviewed text | Decision | Sources | Not listed | Notes |",
            "|---|---|---|---|---|---|",
        ]
        lines += [_row(item) for item in review["items"] if item["section"] == section]
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
