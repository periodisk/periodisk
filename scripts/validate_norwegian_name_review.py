"""Validate the completed Norwegian element-name review."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "curation/norwegian_terminology/review.schema.json"
DEFAULT_REVIEW = Path("curation/norwegian_terminology/review.json")
DEFAULT_ELEMENTS = Path("src/periodisk/resources/elements.json")
DEFAULT_LOCALE = Path("src/periodisk/resources/locales/nb_NO.json")

SOURCE_HOSTS = {
    "naob": "naob.no",
    "bokmaalsordboka": "ordbokene.no",
    "nynorskordboka": "ordbokene.no",
    "snl": "snl.no",
}

# Decisions whose reviewed name must be the name rendered from nb_NO.json.
SETTLED_DECISIONS = {"retained", "changed"}


def _schema_errors(review: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(review), key=lambda e: list(e.path)):
        location = "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.path
        )
        errors.append(f"review{location}: {error.message}")
    return errors


def validate(
    review: dict[str, Any],
    elements: dict[str, Any],
    locale: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = _schema_errors(review, schema)
    if review.get("schema") != 1:
        errors.append("review.schema must be 1")
    if review.get("locale") != "nb_NO":
        errors.append("review.locale must be nb_NO")

    try:
        date.fromisoformat(review["reviewed_date"])
    except (KeyError, TypeError, ValueError):
        errors.append("review.reviewed_date must be an ISO date")

    records = review.get("elements")
    if not isinstance(records, list):
        return [*errors, "review.elements must be a list"]

    expected = elements["elements"]
    names = locale["element_names"]
    if len(records) != len(expected):
        errors.append(f"review has {len(records)} records; expected {len(expected)}")

    for index, (record, element) in enumerate(zip(records, expected, strict=False)):
        context = f"elements[{index}]"
        atomic_number = element["atomic_number"]
        symbol = element["symbol"]
        if record.get("atomic_number") != atomic_number:
            errors.append(f"{context}.atomic_number must be {atomic_number}")
        if record.get("symbol") != symbol:
            errors.append(f"{context}.symbol must be {symbol}")
        decision = record.get("decision")
        if decision not in SETTLED_DECISIONS:
            errors.append(
                f"{context}.decision must be retained or changed in a completed audit"
            )
        elif record.get("reviewed_name") != names[symbol]:
            errors.append(f"{context}.reviewed_name must match nb_NO.json")

        sources = record.get("sources")
        if not isinstance(sources, dict):
            errors.append(f"{context}.sources must be an object")
            continue
        if set(sources) != set(SOURCE_HOSTS):
            errors.append(f"{context}.sources must contain all registered sources")
            continue
        for source_id, expected_host in SOURCE_HOSTS.items():
            source = sources[source_id]
            if not isinstance(source.get("headword"), str) or not source["headword"]:
                errors.append(
                    f"{context}.sources.{source_id}.headword must be non-empty"
                )
            url = source.get("url")
            if not isinstance(url, str):
                errors.append(f"{context}.sources.{source_id}.url must be a string")
                continue
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != expected_host:
                errors.append(
                    f"{context}.sources.{source_id}.url must use https://{expected_host}"
                )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--elements", type=Path, default=DEFAULT_ELEMENTS)
    parser.add_argument("--locale", type=Path, default=DEFAULT_LOCALE)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    elements = json.loads(args.elements.read_text(encoding="utf-8"))
    locale = json.loads(args.locale.read_text(encoding="utf-8"))
    errors = validate(review, elements, locale)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(f"Validated {len(review['elements'])} Norwegian element names")


if __name__ == "__main__":
    main()
