"""Validation rules shared by development scripts, tests, and releases."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping

from .models import IONISATION_ENERGY_UNIT, Element, Source

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
        if not 1 <= element.atomic_number <= 118:
            errors.append(f"{label}: atomic number must be between 1 and 118")
        if not 1 <= element.period <= 7:
            errors.append(f"{label}: period must be between 1 and 7")
        if element.group is not None and not 1 <= element.group <= 18:
            errors.append(f"{label}: group must be between 1 and 18 or null")
        if not 1 <= len(element.classifications) <= 2:
            errors.append(f"{label}: must have one or two classifications")
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
        if energy is not None and (not isinstance(energy, (int, float)) or energy <= 0):
            errors.append(f"{label}: first ionisation energy must be positive or null")
        if not isinstance(element.has_no_stable_isotopes.value, bool):
            errors.append(f"{label}: stable-isotope flag must be boolean")
        if not isinstance(element.atomic_weight.value, dict):
            errors.append(f"{label}: atomic weight must be a structured object")
        else:
            kind = element.atomic_weight.value.get("kind")
            if kind not in {"abridged-standard", "mass-number"}:
                errors.append(f"{label}: invalid atomic-weight kind {kind!r}")
            if not element.atomic_weight.value.get("display"):
                errors.append(f"{label}: atomic weight requires a display value")
        for scale, value in element.electronegativity.items():
            if not isinstance(value.value, (int, float)) or value.value <= 0:
                errors.append(f"{label}: {scale} electronegativity must be positive")
        states = element.oxidation_states.value
        if not isinstance(states, dict) or set(states) != {"main", "additional"}:
            errors.append(
                f"{label}: oxidation states require main and additional lists"
            )
        elif not all(isinstance(states[key], list) for key in ("main", "additional")):
            errors.append(f"{label}: oxidation-state groups must be lists")

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
