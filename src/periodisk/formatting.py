"""Locale-aware, compact formatting for element-cell content."""

from __future__ import annotations

from typing import Any

from .models import Element

SUPERSCRIPTS = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")


def localise_number(text: str, decimal_separator: str) -> str:
    return text if decimal_separator == "." else text.replace(".", decimal_separator)


def atomic_weight(element: Element, decimal_separator: str) -> str:
    return localise_number(element.atomic_weight.value["display"], decimal_separator)


def electronegativity(
    element: Element, scale: str, decimal_separator: str, missing: str = "—"
) -> str:
    sourced = element.electronegativity.get(scale)
    if sourced is None:
        return missing
    return localise_number(f"{sourced.value:g}", decimal_separator)


def ionisation_energy(
    element: Element, decimal_separator: str, missing: str = "—"
) -> str:
    value = element.first_ionisation_energy.value
    if value is None:
        return missing
    return localise_number(f"{value:.1f}", decimal_separator)


def oxidation_states(element: Element, missing: str = "—") -> str:
    states: list[int] = element.oxidation_states.value["main"]
    if not states:
        return missing
    if states == list(range(-4, 5)):
        return "−4…+4"
    return " ".join(f"{state:+d}" if state else "0" for state in states)


def electron_configuration(element: Element) -> str:
    """Use compact notation with an explicit superscript occupancy per subshell."""

    import re

    value = str(element.electron_configuration.value)
    formatted: list[str] = []
    for token in value.split():
        if token.startswith("["):
            formatted.append(token)
            continue
        match = re.fullmatch(r"(\d+)([spdfg])(\d*)", token)
        if match is None:
            formatted.append(token)
            continue
        shell, subshell, occupancy = match.groups()
        formatted.append(
            f"{shell}{subshell}{(occupancy or '1').translate(SUPERSCRIPTS)}"
        )
    return "".join(formatted)


def text_value(value: Any) -> str:
    return "—" if value is None else str(value)
