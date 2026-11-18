"""Validate the Norwegian classification-term review."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "curation/norwegian_terminology/classifications.schema.json"
DEFAULT_REVIEW = Path("curation/norwegian_terminology/classifications.json")
DEFAULT_ELEMENTS = Path("src/periodisk/resources/elements.json")
DEFAULT_LOCALE = Path("src/periodisk/resources/locales/nb_NO.json")

SOURCE_HOSTS = {
    "naob": "naob.no",
    "bokmaalsordboka": "ordbokene.no",
    "snl": "snl.no",
    "iupac-red-book-2005": "iupac.org",
    "chebi": "www.ebi.ac.uk",
    "wikipedia-no": "no.wikipedia.org",
    "wikipedia-en": "en.wikipedia.org",
}

# Detailed categories merged into each broad class. A test checks this against
# the renderer so the documented scope cannot drift from the rendered one.
BROAD_INCLUDES = {
    "transition-metal": [
        "alkali-metal",
        "alkaline-earth-metal",
        "transition-metal",
        "post-transition-metal",
        "lanthanide",
        "actinide",
    ],
    "metalloid": ["metalloid"],
    "reactive-nonmetal": ["reactive-nonmetal", "halogen"],
    "noble-gas": ["noble-gas"],
}

LOCALE_SECTIONS = {"detailed": "classifications", "broad": "broad_classifications"}

# Decisions whose reviewed term must be the term rendered from nb_NO.json.
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


def _members(elements: dict[str, Any], key: str) -> list[str]:
    return [
        element["symbol"]
        for element in elements["elements"]
        if key in element["classifications"]
    ]


def validate(
    review: dict[str, Any],
    elements: dict[str, Any],
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

    terms = review.get("terms")
    if not isinstance(terms, list):
        return [*errors, "review.terms must be a list"]

    expected = [
        (mode, key)
        for mode, section in LOCALE_SECTIONS.items()
        for key in locale[section]
    ]
    actual = [(term.get("mode"), term.get("key")) for term in terms]
    if actual != expected:
        errors.append(
            "review.terms must cover every locale classification term in locale order"
        )

    for index, term in enumerate(terms):
        context = f"terms[{index}]"
        mode, key = term.get("mode"), term.get("key")
        section = locale.get(LOCALE_SECTIONS.get(mode, ""), {})
        if key not in section:
            errors.append(f"{context} has no {mode} term {key!r} in nb_NO.json")
            continue

        decision = term.get("decision")
        if decision not in SETTLED_DECISIONS:
            errors.append(
                f"{context}.decision must be retained or changed in a completed review"
            )
        elif term.get("reviewed_term") != section[key]:
            errors.append(f"{context}.reviewed_term must match nb_NO.json")
        if decision == "changed" and term.get("previous_term") == term.get(
            "reviewed_term"
        ):
            errors.append(f"{context}.previous_term must differ from reviewed_term")

        if mode == "detailed" and term.get("members") != _members(elements, key):
            errors.append(f"{context}.members must match elements.json")
        if mode == "broad" and term.get("includes") != BROAD_INCLUDES.get(key):
            errors.append(f"{context}.includes must match the broad mapping")

        cited = set()
        for source_index, source in enumerate(term.get("sources", [])):
            source_id = source.get("source")
            cited.add(source_id)
            expected_host = SOURCE_HOSTS.get(source_id)
            parsed = urlparse(source.get("url", ""))
            if parsed.scheme != "https" or parsed.hostname != expected_host:
                errors.append(
                    f"{context}.sources[{source_index}].url must use "
                    f"https://{expected_host}"
                )
        overlap = cited & set(term.get("not_listed", []))
        if overlap:
            errors.append(
                f"{context}.not_listed must not include cited sources: "
                + ", ".join(sorted(overlap))
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
    print(f"Validated {len(review['terms'])} Norwegian classification terms")


if __name__ == "__main__":
    main()
