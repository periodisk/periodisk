"""Collect a revision-pinned oxidation-state snapshot from English Wikipedia."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TITLE = "Template:List_of_oxidation_states_of_the_elements"
API = "https://en.wikipedia.org/w/api.php"
DEFAULT_OUTPUT = Path("curation/oxidation_states/wikipedia.json")
STATES = tuple(range(-5, 10))


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, Any]]] = []
        self._row: list[dict[str, Any]] | None = None
        self._cell: dict[str, Any] | None = None
        self._bold_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = {"text": [], "bold": False}
        elif tag in {"b", "strong"} and self._cell is not None:
            self._bold_depth += 1
            self._cell["bold"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"b", "strong"} and self._bold_depth:
            self._bold_depth -= 1
        elif tag == "td" and self._row is not None and self._cell is not None:
            self._cell["text"] = " ".join("".join(self._cell["text"]).split())
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell["text"].append(data)


def parse_table(html: str) -> list[dict[str, Any]]:
    parser = _TableParser()
    parser.feed(html)
    elements: list[dict[str, Any]] = []
    for cells in parser.rows:
        if len(cells) < 18 or not str(cells[0]["text"]).isdigit():
            continue
        atomic_number = int(cells[0]["text"])
        if not 1 <= atomic_number <= 118:
            continue
        symbol = str(cells[2]["text"])
        present = [
            state
            for state, cell in zip(STATES, cells[3:18], strict=True)
            if cell["text"]
        ]
        main = [
            state
            for state, cell in zip(STATES, cells[3:18], strict=True)
            if cell["bold"]
        ]
        elements.append(
            {
                "atomic_number": atomic_number,
                "symbol": symbol,
                "states": present,
                "main": main,
            }
        )
    if [item["atomic_number"] for item in elements] != list(range(1, 119)):
        raise ValueError(
            "Wikipedia table did not yield exactly elements 1–118 in order"
        )
    return elements


def build_snapshot(
    payload: dict[str, Any], retrieved_at: str | None = None
) -> dict[str, Any]:
    parsed = payload["parse"]
    revision = int(parsed["revid"])
    return {
        "schema": 1,
        "source": "wikipedia-oxidation-states",
        "title": parsed["title"],
        "revision": revision,
        "permanent_url": (
            f"https://en.wikipedia.org/w/index.php?title={TITLE}&oldid={revision}"
        ),
        "retrieved_at": retrieved_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "license": "CC BY-SA 4.0",
        "attribution": "Wikipedia contributors",
        "scope_note": (
            "Occurrences in compounds and complexes; elemental standard states and "
            "allotropes are excluded. Bold values in the source are recorded as main."
        ),
        "elements": parse_table(parsed["text"]),
    }


def fetch() -> dict[str, Any]:
    query = urlencode(
        {
            "action": "parse",
            "page": TITLE,
            "prop": "text|revid",
            "format": "json",
            "formatversion": 2,
        }
    )
    request = Request(
        f"{API}?{query}",
        headers={"User-Agent": "periodisk-curation/2026.1 (educational data audit)"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="use a saved MediaWiki API response")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = (
        json.loads(args.input.read_text(encoding="utf-8")) if args.input else fetch()
    )
    snapshot = build_snapshot(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {len(snapshot['elements'])} records from Wikipedia revision "
        f"{snapshot['revision']} to {args.output}"
    )


if __name__ == "__main__":
    main()
