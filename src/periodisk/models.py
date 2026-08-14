"""Small, dependency-free models for the reviewed periodic-table dataset."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

IONISATION_ENERGY_UNIT = "kJ/mol"

Classification = Literal[
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
]
ChemistryStatus = Literal["established", "partly-characterised", "unknown"]


@dataclass(frozen=True, slots=True)
class Source:
    """A bibliographic record referenced by stable identifier."""

    id: str
    title: str
    citation: str
    url: str | None = None
    doi: str | None = None
    accessed: str | None = None
    data_url: str | None = None
    license: str | None = None

    @classmethod
    def from_dict(cls, source_id: str, raw: dict[str, Any]) -> Source:
        return cls(id=source_id, **raw)


@dataclass(frozen=True, slots=True)
class SourcedValue:
    """A value with its unit and provenance kept alongside it."""

    value: Any
    source: str
    unit: str | None = None
    note: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SourcedValue:
        return cls(**raw)


@dataclass(frozen=True, slots=True)
class Element:
    """Scientific and presentation data for one chemical element."""

    atomic_number: int
    symbol: str
    period: int
    group: int | None
    atomic_weight: SourcedValue
    electronegativity: dict[str, SourcedValue]
    first_ionisation_energy: SourcedValue
    oxidation_states: SourcedValue
    electron_configuration: SourcedValue
    has_no_stable_isotopes: SourcedValue
    classifications: tuple[Classification, ...]
    chemistry_status: ChemistryStatus = "established"
    note: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Element:
        values = dict(raw)
        for field in (
            "atomic_weight",
            "first_ionisation_energy",
            "oxidation_states",
            "electron_configuration",
            "has_no_stable_isotopes",
        ):
            values[field] = SourcedValue.from_dict(values[field])
        values["electronegativity"] = {
            scale: SourcedValue.from_dict(value)
            for scale, value in values["electronegativity"].items()
        }
        values["classifications"] = tuple(values["classifications"])
        return cls(**values)
