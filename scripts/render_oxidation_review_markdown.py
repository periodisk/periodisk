"""Render the oxidation-state review worksheet as linked Markdown tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REVIEW = Path("curation/oxidation_states/review.json")
DEFAULT_SOURCES = Path("curation/oxidation_states/sources.json")
DEFAULT_OUTPUT = Path("curation/oxidation_states/REVIEW_TABLE.md")


def _state_label(state: int) -> str:
    if state > 0:
        return f"+{state}"
    return str(state).replace("-", "−")


def _anchor(symbol: str, state: int) -> str:
    sign = "m" if state < 0 else "p" if state > 0 else "z"
    return f"{symbol.lower()}-{sign}{abs(state)}"


def _escape(text: str) -> str:
    return text.replace("|", "&#124;").replace("\n", " ")


def render(review: dict[str, Any], sources: dict[str, Any]) -> str:
    selected_states = [
        state for element in review["elements"] for state in element["print"]
    ]
    states = range(min(selected_states), max(selected_states) + 1)
    lines = [
        "# Oxidation-state review table",
        "",
        "This file is generated from [`review.json`](review.json). Do not edit it",
        "directly. Empty cells are reviewed omissions, not missing records.",
        "",
        "The matrix gives one row per element. Each populated cell shows the",
        "representative species and links to the corresponding support record",
        "below.",
        "",
        "## Matrix",
        "",
        "| Z | Element | " + " | ".join(_state_label(state) for state in states) + " |",
        "|---:|:---:|" + "|".join(":---:" for _ in states) + "|",
    ]

    for element in review["elements"]:
        cells = []
        for state in states:
            item = element["evidence"].get(str(state))
            if item is None:
                cells.append("—")
            else:
                representative = _escape(item["representative"])
                anchor = _anchor(element["symbol"], state)
                cells.append(f'<a href="#{anchor}">{representative}</a>')
        lines.append(
            f"| {element['atomic_number']} | {element['symbol']} | "
            + " | ".join(cells)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Support records",
            "",
            "The citation identifiers are broad rather than page-specific. See the",
            "[curation README](README.md) for their intended scope and limitations.",
            "",
            "| Element | State | Representative | Inclusion rationale | Citation |",
            "|:---:|---:|---|---|---|",
        ]
    )
    used_sources: set[str] = set()
    for element in review["elements"]:
        for state in element["print"]:
            item = element["evidence"][str(state)]
            source = item["source"]
            used_sources.add(source)
            lines.append(
                f'| <a id="{_anchor(element["symbol"], state)}"></a>{element["symbol"]} '
                f"| {_state_label(state)} | {_escape(item['representative'])} "
                f"| {_escape(item['reason'])} | [^{source}] |"
            )

    lines.extend(["", "## References", ""])
    for source_id in sorted(used_sources):
        source = sources[source_id]
        citation = source["citation"]
        if source.get("url"):
            citation += f" [{source.get('doi', 'Link')}]({source['url']})."
        elif source.get("isbn"):
            citation += f" ISBN {source['isbn']}."
        lines.extend([f"[^{source_id}]: {citation}", ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    sources = json.loads(args.sources.read_text(encoding="utf-8"))["sources"]
    output = render(review, sources)
    args.output.write_text(output, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
