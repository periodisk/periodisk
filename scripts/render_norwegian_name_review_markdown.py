"""Render the Norwegian element-name review as a Markdown table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REVIEW = Path("curation/norwegian_terminology/review.json")
DEFAULT_OUTPUT = Path("curation/norwegian_terminology/REVIEW_TABLE.md")

SOURCE_LABELS = {
    "naob": "NAOB",
    "bokmaalsordboka": "BM",
    "nynorskordboka": "NN",
    "snl": "SNL",
}


def _escape(text: str) -> str:
    return text.replace("|", "&#124;").replace("\n", " ")


def render(review: dict[str, Any]) -> str:
    lines = [
        "# Norwegian element-name review",
        "",
        "This file is generated from [`review.json`](review.json). Do not edit it",
        "directly. See the [curation README](README.md) for the scope and method.",
        "",
        "BM denotes Bokmålsordboka and NN denotes Nynorskordboka. The NN",
        "headword is supplementary because Periodisk currently renders Bokmål.",
        "",
        "| Z | Symbol | Reviewed Bokmål name | Sources | Decision | Notes |",
        "|---:|:---:|---|---|---|---|",
    ]

    for element in review["elements"]:
        links = []
        for source_id, label in SOURCE_LABELS.items():
            source = element["sources"][source_id]
            headword = _escape(source["headword"])
            links.append(f"[{label}: {headword}]({source['url']})")
        decision = element["decision"].capitalize()
        notes = _escape(element.get("notes", "")) or "—"
        lines.append(
            f"| {element['atomic_number']} | {element['symbol']} "
            f"| {_escape(element['reviewed_name'])} | {' · '.join(links)} "
            f"| {decision} | {notes} |"
        )

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
