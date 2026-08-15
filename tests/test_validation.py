from dataclasses import replace

import pytest

from periodisk.models import Element, Source, SourcedValue
from periodisk.validation import validate_dataset

SOURCE = Source(id="test", title="Test", citation="Test source")


def element(*, unit: str = "kJ/mol", source: str = "test") -> Element:
    sourced = SourcedValue(value="test", source=source)
    return Element(
        atomic_number=1,
        symbol="H",
        period=1,
        group=1,
        atomic_weight=SourcedValue(
            value={"kind": "abridged-standard", "display": "1.0080"}, source=source
        ),
        electronegativity={"pauling": SourcedValue(value=2.2, source=source)},
        first_ionisation_energy=SourcedValue(value=1312.0, source=source, unit=unit),
        oxidation_states=SourcedValue(
            value={"main": [1, -1], "additional": []}, source=source
        ),
        electron_configuration=sourced,
        has_no_stable_isotopes=SourcedValue(value=False, source=source),
        classifications=("reactive-nonmetal",),
    )


def test_valid_record_passes_structural_validation() -> None:
    assert validate_dataset([element()], {"test": SOURCE}) == []


def test_ionisation_energy_must_be_kilojoules_per_mole() -> None:
    errors = validate_dataset([element(unit="eV")], {"test": SOURCE})
    assert any("kJ/mol" in error for error in errors)


def test_unknown_source_is_rejected() -> None:
    errors = validate_dataset([element(source="missing")], {"test": SOURCE})
    assert any("unknown source id" in error for error in errors)


def test_release_validation_requires_all_elements() -> None:
    errors = validate_dataset([element()], {"test": SOURCE}, release=True)
    assert any("118 elements" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("atomic_number", "atomic number"),
        ("period", "period"),
        ("group", "group"),
    ],
)
def test_boolean_is_not_an_integer_field(field: str, message: str) -> None:
    record = replace(element(), **{field: True})
    errors = validate_dataset([record], {"test": SOURCE})
    assert any(message in error for error in errors)


def test_boolean_is_not_an_ionisation_energy() -> None:
    record = replace(
        element(),
        first_ionisation_energy=SourcedValue(
            value=True,
            source="test",
            unit="kJ/mol",
        ),
    )
    errors = validate_dataset([record], {"test": SOURCE})
    assert any("ionisation energy must be positive" in error for error in errors)


def test_boolean_is_not_an_electronegativity() -> None:
    record = replace(
        element(),
        electronegativity={"pauling": SourcedValue(value=True, source="test")},
    )
    errors = validate_dataset([record], {"test": SOURCE})
    assert any("electronegativity must be positive" in error for error in errors)


def test_boolean_is_not_an_oxidation_state() -> None:
    record = replace(
        element(),
        oxidation_states=SourcedValue(
            value={"main": [True], "additional": []},
            source="test",
        ),
    )
    errors = validate_dataset([record], {"test": SOURCE})
    assert any("oxidation states must be integers" in error for error in errors)
