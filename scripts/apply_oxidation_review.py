"""Apply completed oxidation-state review decisions to the runtime dataset."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.validate_oxidation_review import validate

DEFAULT_REVIEW = Path("curation/oxidation_states/review.json")
DEFAULT_ELEMENTS = Path("src/periodisk/resources/elements.json")
CURATED_SOURCE = "curated-oxidation-states-2026.1"


def apply_review(
    elements: dict[str, Any],
    review: dict[str, Any],
    *,
    require_complete: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    """Return an updated dataset and the symbols whose reviewed values changed."""

    errors = validate(review, require_complete=require_complete)
    if errors:
        raise ValueError("\n".join(errors))

    result = deepcopy(elements)
    element_records = result.get("elements", [])
    review_records = review.get("elements", [])
    if len(element_records) != len(review_records):
        raise ValueError("runtime dataset and review worksheet have different lengths")

    applied: list[str] = []
    for element, decision in zip(element_records, review_records, strict=True):
        identity = (element.get("atomic_number"), element.get("symbol"))
        review_identity = (decision.get("atomic_number"), decision.get("symbol"))
        if identity != review_identity:
            raise ValueError(
                f"runtime/review identity mismatch: {identity!r} != {review_identity!r}"
            )
        if decision["status"] != "reviewed":
            continue

        printed = list(decision["print"])
        candidates = set(decision["mendeleev_main"])
        candidates.update(decision["mendeleev_additional"])
        candidates.update(printed)
        element["oxidation_states"] = {
            "value": {
                "main": printed,
                "additional": sorted(candidates - set(printed)),
            },
            "source": CURATED_SOURCE,
            "note": (
                "Reviewed general-chemistry selection; evidence and editorial "
                "rationale are recorded in curation/oxidation_states/review.json."
            ),
        }
        applied.append(str(element["symbol"]))

    return result, applied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--elements", type=Path, default=DEFAULT_ELEMENTS)
    parser.add_argument(
        "--output",
        type=Path,
        help="write elsewhere instead of replacing --elements",
    )
    parser.add_argument(
        "--complete",
        action="store_true",
        help="refuse to write unless all 118 records are reviewed",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and report without writing",
    )
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    elements = json.loads(args.elements.read_text(encoding="utf-8"))
    updated, applied = apply_review(elements, review, require_complete=args.complete)
    destination = args.output or args.elements
    if not args.dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    action = "Would apply" if args.dry_run else "Applied"
    if applied:
        print(f"{action} {len(applied)} reviewed records: {', '.join(applied)}")
    else:
        print(f"{action} 0 records; no worksheet records are marked reviewed.")


if __name__ == "__main__":
    main()
