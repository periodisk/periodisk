"""Validate the Norwegian label and explanatory-text review."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "curation/norwegian_terminology/labels.schema.json"
DEFAULT_REVIEW = Path("curation/norwegian_terminology/labels.json")
DEFAULT_LOCALE = Path("src/periodisk/resources/locales/nb_NO.json")

SOURCE_HOSTS = {
    "naob": "naob.no",
    "bokmaalsordboka": "ordbokene.no",
    "snl": "snl.no",
}
SECTIONS = ("labels", "source_notes", "units")

# Decisions whose reviewed text must be the text rendered from nb_NO.json.
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
    locale: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = _schema_errors(review, schema)

    try:
        date.fromisoformat(review["reviewed_date"])
    except (KeyError, TypeError, ValueError):
        errors.append("review.reviewed_date must be an ISO date")

    items = review.get("items")
    if not isinstance(items, list):
        return [*errors, "review.items must be a list"]

    expected = [(section, key) for section in SECTIONS for key in locale[section]]
    if [(item.get("section"), item.get("key")) for item in items] != expected:
        errors.append("review.items must cover every locale label in locale order")

    for index, item in enumerate(items):
        context = f"items[{index}]"
        section = locale.get(item.get("section"), {})
        key = item.get("key")
        if key not in section:
            errors.append(f"{context} has no {item.get('section')} key {key!r}")
            continue

        decision = item.get("decision")
        if decision not in SETTLED_DECISIONS:
            errors.append(
                f"{context}.decision must be retained or changed in a completed review"
            )
        elif item.get("reviewed_text") != section[key]:
            errors.append(f"{context}.reviewed_text must match nb_NO.json")
        if decision == "changed" and item.get("previous_text") == item.get(
            "reviewed_text"
        ):
            errors.append(f"{context}.previous_text must differ from reviewed_text")

        cited = set()
        for source_index, source in enumerate(item.get("sources", [])):
            source_id = source.get("source")
            cited.add(source_id)
            expected_host = SOURCE_HOSTS.get(source_id)
            parsed = urlparse(source.get("url", ""))
            if parsed.scheme != "https" or parsed.hostname != expected_host:
                errors.append(
                    f"{context}.sources[{source_index}].url must use "
                    f"https://{expected_host}"
                )
        overlap = cited & set(item.get("not_listed", []))
        if overlap:
            errors.append(
                f"{context}.not_listed must not include cited sources: "
                + ", ".join(sorted(overlap))
            )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--locale", type=Path, default=DEFAULT_LOCALE)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    locale = json.loads(args.locale.read_text(encoding="utf-8"))
    errors = validate(review, locale)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(f"Validated {len(review['items'])} Norwegian labels and notes")


if __name__ == "__main__":
    main()
