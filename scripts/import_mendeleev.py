"""Build the reviewed dataset from pinned local and authoritative snapshots.

This maintenance command is deliberately separate from the runtime package.
It requires mendeleev 1.2.0 and HTML snapshots downloaded from the two CIAAW
pages named below. It never runs while a periodic table is being rendered.
"""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from mendeleev import element

EV_TO_KJ_PER_MOL = 96.48533212331002
ALLEN_TO_PAULING_UNITS = 0.169
EXPECTED_MENDELEEV_VERSION = "1.2.0"


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] = []
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"}:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row:
            self.rows.append(self._row)


def _rows(path: Path) -> list[list[str]]:
    parser = _TableParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.rows


def _atomic_weights(path: Path) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for row in _rows(path):
        if len(row) != 5 or not row[0].isdigit():
            continue
        number = int(row[0])
        display = row[3].replace(" ", "")
        if display == "—":
            continue
        match = re.fullmatch(r"([^±]+)±(.+)", display)
        if match is None:
            raise ValueError(
                f"Unexpected CIAAW abridged value for Z={number}: {display}"
            )
        value: dict[str, Any] = {
            "kind": "abridged-standard",
            "value": match.group(1),
            "uncertainty": match.group(2),
            "display": match.group(1),
        }
        if row[4]:
            value["ciaaw_notes"] = row[4].split()
        result[number] = value
    return result


def _half_life_seconds(text: str) -> float:
    """Return the recommended central half-life in a common unit."""

    match = re.search(r"(?:approx\.\s*)?([0-9]+(?:\.[0-9]+)?)", text)
    if match is None:
        raise ValueError(f"Unexpected CIAAW half-life: {text!r}")
    factors = {
        "Ma": 1_000_000 * 365.25 * 86_400,
        "ka": 1_000 * 365.25 * 86_400,
        "a": 365.25 * 86_400,
        "d": 86_400,
        "h": 3_600,
        "min": 60,
        "ms": 0.001,
        "s": 1,
    }
    unit = next((unit for unit in factors if text.rstrip().endswith(unit)), None)
    if unit is None:
        raise ValueError(f"Unexpected CIAAW half-life unit: {text!r}")
    return float(match.group(1)) * factors[unit]


def _radioactive_mass_numbers(path: Path) -> dict[int, int]:
    """Select the isotope with the largest CIAAW recommended central half-life."""

    candidates: dict[int, list[tuple[int, float]]] = {}
    current_number: int | None = None
    for row in _rows(path):
        if len(row) == 5 and row[0].isdigit() and row[1].isalpha():
            current_number = int(row[0])
            candidates.setdefault(current_number, []).append(
                (int(row[3]), _half_life_seconds(row[4]))
            )
        elif len(row) == 2 and current_number is not None and row[0].isdigit():
            candidates[current_number].append((int(row[0]), _half_life_seconds(row[1])))
    return {
        number: max(isotopes, key=lambda isotope: isotope[1])[0]
        for number, isotopes in candidates.items()
    }


def _classification(number: int, group: int | None) -> list[str]:
    explicit: dict[int, list[str]] = {
        1: ["reactive-nonmetal"],
        2: ["noble-gas"],
        5: ["metalloid"],
        6: ["reactive-nonmetal"],
        7: ["reactive-nonmetal"],
        8: ["reactive-nonmetal"],
        14: ["metalloid"],
        15: ["reactive-nonmetal"],
        16: ["reactive-nonmetal"],
        32: ["metalloid"],
        33: ["metalloid"],
        34: ["reactive-nonmetal"],
        51: ["metalloid"],
        52: ["metalloid"],
        84: ["post-transition-metal", "metalloid"],
        85: ["halogen", "metalloid"],
    }
    if number in explicit:
        return explicit[number]
    if 57 <= number <= 71:
        return ["lanthanide"]
    if 89 <= number <= 103:
        return ["actinide"]
    if group == 1:
        return ["alkali-metal"]
    if group == 2:
        return ["alkaline-earth-metal"]
    if group is not None and 3 <= group <= 12:
        return ["transition-metal"]
    if group == 17:
        return ["halogen"]
    if group == 18:
        return ["noble-gas"]
    return ["post-transition-metal"]


def _sourced(
    value: Any, source: str, unit: str | None = None, note: str | None = None
) -> dict[str, Any]:
    record: dict[str, Any] = {"value": value, "source": source}
    if unit is not None:
        record["unit"] = unit
    if note is not None:
        record["note"] = note
    return record


def build(ciaaw_weights: Path, ciaaw_radioactive: Path) -> dict[str, Any]:
    import mendeleev

    if mendeleev.__version__ != EXPECTED_MENDELEEV_VERSION:
        raise RuntimeError(
            f"Expected mendeleev {EXPECTED_MENDELEEV_VERSION}, found {mendeleev.__version__}"
        )
    weights = _atomic_weights(ciaaw_weights)
    mass_numbers = _radioactive_mass_numbers(ciaaw_radioactive)
    if set(weights) | set(mass_numbers) != set(range(1, 119)):
        raise ValueError("CIAAW snapshots do not cover atomic numbers 1–118")

    records = []
    unknown_chemistry = {109, 110, 111, 116, 117, 118}
    no_stable_isotopes = {43, 61, *range(83, 119)}
    configuration_overrides = {
        110: (
            "[Rn] 5f14 6d8 7s2",
            "hoffman-lee-pershina-2006",
            "Predicted neutral-atom ground-state configuration; reviewed override of Mendeleev 1.2.0.",
        ),
        111: (
            "[Rn] 5f14 6d9 7s2",
            "kaygorodov-et-al-2022",
            "Predicted neutral-atom ground-state configuration; reviewed override of Mendeleev 1.2.0.",
        ),
    }
    oxidation_main_overrides = {
        # Provisional general-chemistry selection; see the curation worksheet.
        6: list(range(-4, 5)),
        7: [-3, 1, 2, 3, 4, 5],
        22: [2, 3, 4],
        23: [2, 3, 4, 5],
        24: [2, 3, 6],
        25: [2, 3, 4, 6, 7],
        26: [2, 3, 6],
        28: [2, 3],
        29: [1, 2],
        35: [-1, 1, 3, 5, 7],
        41: [3, 5],
        44: [2, 3, 4, 8],
        45: [1, 3],
        49: [1, 3],
        54: [2, 4, 6, 8],
        59: [3, 4],
        62: [2, 3],
        65: [3, 4],
        69: [2, 3],
        70: [2, 3],
        75: [4, 7],
        76: [2, 3, 4, 8],
        79: [1, 3],
        83: [3, 5],
        91: [4, 5],
        92: [3, 4, 5, 6],
        93: [3, 4, 5, 6, 7],
        94: [3, 4, 5, 6],
        97: [3, 4],
        101: [2, 3],
        102: [2, 3],
    }
    for number in range(1, 119):
        item = element(number)
        group = item.group_id
        weight = weights.get(number)
        weight_source = "ciaaw-abridged-atomic-weights-2024"
        if weight is None:
            mass_number = mass_numbers[number]
            weight = {
                "kind": "mass-number",
                "value": mass_number,
                "display": f"[{mass_number}]",
            }
            weight_source = "ciaaw-radioactive-elements-2024"

        electronegativity: dict[str, Any] = {}
        if item.en_pauling is not None:
            electronegativity["pauling"] = _sourced(item.en_pauling, "crc-handbook-95")
        allen = item.electronegativity("allen")
        if allen is not None:
            electronegativity["allen"] = _sourced(
                round(allen * ALLEN_TO_PAULING_UNITS, 2),
                "allen-electronegativity-via-mendeleev",
                note="Mendeleev configuration energy in eV multiplied by 0.169 and rounded to two decimal places.",
            )
        raw_allred_rochow = item.electronegativity("allred-rochow")
        if raw_allred_rochow is not None and number not in unknown_chemistry:
            # Original scale: chi = 0.359 * Z_eff/r(angstrom)^2 + 0.744.
            value = round(3590 * raw_allred_rochow + 0.744, 2)
            electronegativity["allred-rochow"] = _sourced(
                value,
                "allred-rochow-calculated",
                note="Calculated with Slater effective charge and Pyykkö single-bond covalent radius.",
            )

        ionisation = item.ionenergies.get(1)
        ie_value = (
            None if ionisation is None else round(ionisation * EV_TO_KJ_PER_MOL, 3)
        )
        ie_note = None
        if ionisation is not None:
            ie_note = f"Converted from {ionisation:g} eV using 1 eV/particle = {EV_TO_KJ_PER_MOL:g} kJ/mol."

        main_states = item.oxidation_states("main")
        all_states = item.oxidation_states("all")
        main_states = oxidation_main_overrides.get(number, main_states)
        additional = [state for state in all_states if state not in main_states]
        chemistry_status = "unknown" if number in unknown_chemistry else "established"

        configuration = configuration_overrides.get(number)
        if configuration is None:
            configuration_value = item.econf
            configuration_source = "mendeleev-electron-configurations-1.2.0"
            configuration_note = (
                "Predicted neutral-atom ground-state configuration."
                if number >= 104
                else None
            )
        else:
            configuration_value, configuration_source, configuration_note = (
                configuration
            )

        records.append(
            {
                "atomic_number": number,
                "symbol": item.symbol,
                "period": item.period,
                "group": group,
                "atomic_weight": _sourced(weight, weight_source),
                "electronegativity": electronegativity,
                "first_ionisation_energy": _sourced(
                    ie_value, "nist-asd-5.11-via-mendeleev", "kJ/mol", ie_note
                ),
                "oxidation_states": _sourced(
                    {"main": main_states, "additional": additional},
                    "mendeleev-oxidation-states-2024",
                    note=(
                        "Provisional general-chemistry selection under oxidation-state review; all values occur in the imported Mendeleev data."
                        if number in oxidation_main_overrides
                        else "Main/extended categorisation imported from Mendeleev; see docs/DATA_SOURCES.md limitations."
                    ),
                ),
                "electron_configuration": _sourced(
                    configuration_value, configuration_source, note=configuration_note
                ),
                "has_no_stable_isotopes": _sourced(
                    number in no_stable_isotopes, "nubase-2020"
                ),
                "classifications": _classification(number, group),
                "chemistry_status": chemistry_status,
            }
        )
    return {
        "schema": 1,
        "status": "review-candidate",
        "generated": "2026-08-11",
        "generator": "scripts/import_mendeleev.py",
        "provenance": {
            "atomic_numbers_symbols_periods_groups": "iupac-periodic-table-2022",
        },
        "elements": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ciaaw-weights",
        type=Path,
        required=True,
        help="downloaded CIAAW abridged-atomic-weights.htm",
    )
    parser.add_argument("--ciaaw-radioactive", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("src/periodisk/resources/elements.json"),
    )
    args = parser.parse_args()
    data = build(args.ciaaw_weights, args.ciaaw_radioactive)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
