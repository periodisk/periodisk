"""Validation rules shared by development scripts, tests, and releases."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Mapping
from decimal import Decimal, InvalidOperation

from .models import IONISATION_ENERGY_UNIT, Element, Source
from .settings import SUPPORTED_ELECTRONEGATIVITY_SCALES

CLASSIFICATIONS = {
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
CHEMISTRY_STATUSES = {"established", "partly-characterised", "unknown"}


def _is_integer(value: object) -> bool:
    """Return whether value is an integer, excluding booleans."""

    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    """Return whether value is a finite real number, excluding booleans."""

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_positive_decimal_text(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        number = Decimal(value)
    except InvalidOperation:
        return False
    return number.is_finite() and number > 0


def validate_dataset(
    elements: Iterable[Element],
    sources: Mapping[str, Source],
    *,
    release: bool = False,
) -> list[str]:
    """Return all detected problems rather than failing on the first one."""

    records = tuple(elements)
    errors: list[str] = []
    numbers = Counter(element.atomic_number for element in records)
    symbols = Counter(element.symbol for element in records)

    for number, count in numbers.items():
        if count > 1:
            errors.append(f"duplicate atomic number: {number}")
    for symbol, count in symbols.items():
        if count > 1:
            errors.append(f"duplicate element symbol: {symbol}")

    for element in records:
        label = f"{element.symbol} ({element.atomic_number})"
        if (
            not _is_integer(element.atomic_number)
            or not 1 <= element.atomic_number <= 118
        ):
            errors.append(f"{label}: atomic number must be between 1 and 118")
        if not _is_integer(element.period) or not 1 <= element.period <= 7:
            errors.append(f"{label}: period must be between 1 and 7")
        if element.group is not None and (
            not _is_integer(element.group) or not 1 <= element.group <= 18
        ):
            errors.append(f"{label}: group must be between 1 and 18 or null")
        if not 1 <= len(element.classifications) <= 2:
            errors.append(f"{label}: must have one or two classifications")
        elif len(set(element.classifications)) != len(element.classifications):
            errors.append(f"{label}: classifications must be unique")
        unknown = set(element.classifications) - CLASSIFICATIONS
        if unknown:
            errors.append(f"{label}: unknown classifications: {sorted(unknown)}")
        if element.chemistry_status not in CHEMISTRY_STATUSES:
            errors.append(
                f"{label}: invalid chemistry status {element.chemistry_status!r}"
            )
        if not element.symbol.isalpha() or not element.symbol[0].isupper():
            errors.append(f"{label}: invalid element symbol")
        if element.first_ionisation_energy.unit != IONISATION_ENERGY_UNIT:
            errors.append(
                f"{label}: first ionisation energy unit must be "
                f"{IONISATION_ENERGY_UNIT!r}"
            )
        energy = element.first_ionisation_energy.value
        if energy is not None and (not _is_number(energy) or energy <= 0):
            errors.append(f"{label}: first ionisation energy must be positive or null")
        if not isinstance(element.has_no_stable_isotopes.value, bool):
            errors.append(f"{label}: stable-isotope flag must be boolean")
        if not isinstance(element.atomic_weight.value, dict):
            errors.append(f"{label}: atomic weight must be a structured object")
        else:
            kind = element.atomic_weight.value.get("kind")
            if kind not in {"abridged-standard", "mass-number"}:
                errors.append(f"{label}: invalid atomic-weight kind {kind!r}")
            display = element.atomic_weight.value.get("display")
            if not isinstance(display, str) or not display.strip():
                errors.append(
                    f"{label}: atomic-weight display must be a non-empty string"
                )
            elif kind == "abridged-standard":
                value = element.atomic_weight.value.get("value")
                uncertainty = element.atomic_weight.value.get("uncertainty")
                if not _is_positive_decimal_text(value):
                    errors.append(
                        f"{label}: abridged atomic weight requires a positive "
                        "decimal-string value"
                    )
                if not _is_positive_decimal_text(uncertainty):
                    errors.append(
                        f"{label}: abridged atomic weight requires a positive "
                        "decimal-string uncertainty"
                    )
                if isinstance(value, str) and display != value:
                    errors.append(
                        f"{label}: abridged atomic-weight display must match value"
                    )
            elif kind == "mass-number":
                value = element.atomic_weight.value.get("value")
                if not _is_integer(value) or value <= 0:
                    errors.append(
                        f"{label}: mass-number atomic weight requires a positive integer"
                    )
                elif display != f"[{value}]":
                    errors.append(
                        f"{label}: mass-number display must be formatted as [{value}]"
                    )
        unknown_scales = set(element.electronegativity) - set(
            SUPPORTED_ELECTRONEGATIVITY_SCALES
        )
        if unknown_scales:
            errors.append(
                f"{label}: unknown electronegativity scales: {sorted(unknown_scales)}"
            )
        for scale, value in element.electronegativity.items():
            if not _is_number(value.value) or value.value <= 0:
                errors.append(f"{label}: {scale} electronegativity must be positive")
        states = element.oxidation_states.value
        if not isinstance(states, dict) or set(states) != {"main", "additional"}:
            errors.append(
                f"{label}: oxidation states require main and additional lists"
            )
        elif not all(isinstance(states[key], list) for key in ("main", "additional")):
            errors.append(f"{label}: oxidation-state groups must be lists")
        elif not all(
            _is_integer(state)
            for key in ("main", "additional")
            for state in states[key]
        ):
            errors.append(f"{label}: oxidation states must be integers")
        else:
            main = states["main"]
            additional = states["additional"]
            if main != sorted(set(main)) or additional != sorted(set(additional)):
                errors.append(
                    f"{label}: oxidation-state groups must be sorted and unique"
                )
            if set(main) & set(additional):
                errors.append(
                    f"{label}: main and additional oxidation states must be disjoint"
                )

        configuration = element.electron_configuration.value
        if not isinstance(configuration, str) or not configuration.strip():
            errors.append(f"{label}: electron configuration must be a non-empty string")

        sourced_values = [
            element.atomic_weight,
            element.first_ionisation_energy,
            element.oxidation_states,
            element.electron_configuration,
            element.has_no_stable_isotopes,
            *element.electronegativity.values(),
        ]
        for value in sourced_values:
            if value.source not in sources:
                errors.append(f"{label}: unknown source id {value.source!r}")

    if release:
        expected_numbers = set(range(1, 119))
        actual_numbers = set(numbers)
        missing = sorted(expected_numbers - actual_numbers)
        if missing:
            errors.append(f"dataset is missing atomic numbers: {missing}")
        if len(records) != 118:
            errors.append(
                f"release dataset must contain 118 elements, found {len(records)}"
            )

    return errors
