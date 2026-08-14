"""Validate the oxidation-state worksheet and report review progress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REVIEW = Path("curation/oxidation_states/review.json")


def validate(data: dict[str, Any], require_complete: bool = False) -> list[str]:
    errors: list[str] = []
    records = data.get("elements", [])
    if len(records) != 118:
        errors.append(f"expected 118 elements, found {len(records)}")
    if [record.get("atomic_number") for record in records] != list(range(1, 119)):
        errors.append("elements must be in atomic-number order")

    for record in records:
        label = record.get("symbol", "?")
        printed = record.get("print", [])
        principal = record.get("principal", [])
        if printed != sorted(set(printed)):
            errors.append(f"{label}: print states must be sorted and unique")
        carbon_range = label == "C" and printed == list(range(-4, 5))
        nitrogen_selection = label == "N" and printed == [-3, 1, 2, 3, 4, 5]
        if 0 in printed and not carbon_range:
            errors.append(f"{label}: state zero requires a documented exception")
        if len(printed) > 5 and not (carbon_range or nitrogen_selection):
            errors.append(f"{label}: more than five print states")
        if principal != sorted(set(principal)):
            errors.append(f"{label}: principal states must be sorted and unique")
        if not set(principal).issubset(printed):
            errors.append(f"{label}: principal states must be a subset of print states")

        status = record.get("status")
        if status not in {"pending", "reviewed", "needs-research"}:
            errors.append(f"{label}: invalid status {status!r}")
        if require_complete and status != "reviewed":
            errors.append(f"{label}: review is not complete")
        if status == "reviewed":
            expected = {str(state) for state in printed}
            evidence = record.get("evidence", {})
            if set(evidence) != expected:
                errors.append(f"{label}: evidence must match printed states")
            for state, item in evidence.items():
                for field in ("representative", "reason", "source"):
                    if not str(item.get(field, "")).strip():
                        errors.append(f"{label} {state}: evidence {field} is empty")
            if not str(record.get("reviewer", "")).strip():
                errors.append(f"{label}: reviewed record has no reviewer")
            if not record.get("reviewed_date"):
                errors.append(f"{label}: reviewed record has no date")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate(data, require_complete=args.complete)
    if errors:
        raise SystemExit("\n".join(errors))
    counts = dict.fromkeys(("pending", "reviewed", "needs-research"), 0)
    for record in data["elements"]:
        counts[record["status"]] += 1
    print(
        f"Worksheet valid: {counts['reviewed']} reviewed, "
        f"{counts['pending']} pending, {counts['needs-research']} needing research."
    )


if __name__ == "__main__":
    main()
