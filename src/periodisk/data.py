"""Load immutable JSON resources bundled with the package."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from .models import Element, Source
from .settings import SUPPORTED_ELECTRONEGATIVITY_SCALES, SUPPORTED_LOCALES

_REQUIRED_CLASSIFICATIONS = {
    "alkali-metal",
    "alkaline-earth-metal",
    "transition-metal",
    "post-transition-metal",
    "metalloid",
    "reactive-nonmetal",
    "halogen",
    "noble-gas",
    "lanthanide",
    "actinide",
}
_REQUIRED_LABELS = {
    "title",
    "atomic_number",
    "element_symbol",
    "element_name",
    "atomic_weight",
    "electronegativity",
    "first_ionisation_energy",
    "oxidation_states",
    "electron_configuration",
    "radioactive",
    "unknown_chemistry",
    "radioactive_sign",
    "sources",
    "split_classification",
}
_REQUIRED_BROAD_CLASSIFICATIONS = {
    "transition-metal",
    "metalloid",
    "reactive-nonmetal",
    "noble-gas",
}
_REQUIRED_UNITS = {"first_ionisation_energy"}
_REQUIRED_SOURCE_NOTES = {
    "atomic_masses",
    "ionisation_energies",
    "electron_configurations",
    "oxidation_states",
    *SUPPORTED_ELECTRONEGATIVITY_SCALES,
}


def _read_json(relative_path: str) -> dict[str, Any]:
    resource = files("periodisk").joinpath("resources", relative_path)
    with resource.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_elements() -> tuple[Element, ...]:
    raw = _read_json("elements.json")
    return tuple(Element.from_dict(item) for item in raw["elements"])


def load_sources() -> dict[str, Source]:
    raw = _read_json("sources.json")
    return {
        source_id: Source.from_dict(source_id, value)
        for source_id, value in raw["sources"].items()
    }


def load_locale(locale: str) -> dict[str, Any]:
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    resource = _read_json(f"locales/{locale}.json")
    _validate_locale(resource, locale)
    return resource


def _validate_locale(resource: dict[str, Any], expected_locale: str) -> None:
    """Fail early when a translation resource is incomplete or malformed."""

    if not isinstance(resource, dict):
        raise ValueError(f"{expected_locale}: locale resource must be an object")
    if resource.get("locale") != expected_locale:
        raise ValueError(
            f"Locale resource identifies itself as {resource.get('locale')!r}"
        )
    if resource.get("decimal_separator") not in {".", ","}:
        raise ValueError(f"Invalid decimal separator for {expected_locale}")
    missing_value = resource.get("missing_value")
    if not isinstance(missing_value, str) or not missing_value:
        raise ValueError(f"{expected_locale}: missing_value must be a non-empty string")
    element_names = resource.get("element_names")
    if not isinstance(element_names, dict) or len(element_names) != 118:
        raise ValueError(f"{expected_locale}: element_names must contain 118 entries")
    invalid_names = [
        symbol
        for symbol, name in element_names.items()
        if not isinstance(symbol, str) or not isinstance(name, str) or not name.strip()
    ]
    if invalid_names:
        raise ValueError(
            f"{expected_locale}: invalid element names for {invalid_names}"
        )
    if not isinstance(resource.get("element_names_source"), str):
        raise ValueError(f"{expected_locale}: missing element_names_source")
    requirements = {
        "labels": _REQUIRED_LABELS,
        "classifications": _REQUIRED_CLASSIFICATIONS,
        "broad_classifications": _REQUIRED_BROAD_CLASSIFICATIONS,
        "units": _REQUIRED_UNITS,
        "source_notes": _REQUIRED_SOURCE_NOTES,
    }
    for section, required_keys in requirements.items():
        actual = resource.get(section)
        if not isinstance(actual, dict):
            raise ValueError(f"{expected_locale}: missing locale section {section!r}")
        missing = required_keys - actual.keys()
        if missing:
            raise ValueError(
                f"{expected_locale}: {section} is missing {sorted(missing)}"
            )
