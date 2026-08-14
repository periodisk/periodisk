"""Generate or refresh the human oxidation-state review worksheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_ELEMENTS = Path("src/periodisk/resources/elements.json")
DEFAULT_OUTPUT = Path("curation/oxidation_states/review.json")
DEFAULT_WIKIPEDIA = Path("curation/oxidation_states/wikipedia.json")


def _candidate(
    element: dict[str, Any], wikipedia: dict[str, Any] | None = None
) -> dict[str, Any]:
    states = element["oxidation_states"]["value"]
    main = sorted(state for state in states["main"] if state != 0)
    additional = sorted(state for state in states["additional"] if state != 0)
    return {
        "atomic_number": element["atomic_number"],
        "symbol": element["symbol"],
        "mendeleev_main": main,
        "mendeleev_additional": additional,
        "wikipedia_main": wikipedia["main"] if wikipedia else [],
        "wikipedia_additional": (
            sorted(set(wikipedia["states"]) - set(wikipedia["main"]))
            if wikipedia
            else []
        ),
        "print": main,
        "principal": [],
        "evidence": {},
        "status": "pending",
        "reviewer": "",
        "reviewed_date": None,
        "notes": "",
    }


def build(
    elements_path: Path,
    existing_path: Path | None = None,
    wikipedia_path: Path | None = DEFAULT_WIKIPEDIA,
) -> dict[str, Any]:
    source = json.loads(elements_path.read_text(encoding="utf-8"))
    existing: dict[str, dict[str, Any]] = {}
    if existing_path is not None and existing_path.exists():
        old = json.loads(existing_path.read_text(encoding="utf-8"))
        existing = {record["symbol"]: record for record in old["elements"]}

    wikipedia: dict[str, dict[str, Any]] = {}
    if wikipedia_path is not None and wikipedia_path.exists():
        snapshot = json.loads(wikipedia_path.read_text(encoding="utf-8"))
        wikipedia = {record["symbol"]: record for record in snapshot["elements"]}

    records = []
    for element in source["elements"]:
        generated = _candidate(element, wikipedia.get(element["symbol"]))
        old = existing.get(generated["symbol"])
        if old is not None:
            # The bundled runtime data gradually receives reviewed selections.
            # Preserve the originally imported Mendeleev candidates so that
            # later worksheet refreshes do not relabel our decisions as
            # upstream data.
            for field in (
                "mendeleev_main",
                "mendeleev_additional",
                "print",
                "principal",
                "evidence",
                "status",
                "reviewer",
                "reviewed_date",
                "notes",
            ):
                if field in old:
                    generated[field] = old[field]
        records.append(generated)

    return {
        "schema": 1,
        "policy": "README.md",
        "source": "mendeleev-oxidation-states-2024",
        "elements": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elements", type=Path, default=DEFAULT_ELEMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wikipedia", type=Path, default=DEFAULT_WIKIPEDIA)
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="discard existing review decisions instead of preserving them",
    )
    args = parser.parse_args()
    existing = None if args.fresh else args.output
    worksheet = build(args.elements, existing, args.wikipedia)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(worksheet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(worksheet['elements'])} review records to {args.output}")


if __name__ == "__main__":
    main()
