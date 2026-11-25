from periodisk.data import load_elements
from periodisk.formatting import (
    electron_configuration,
    electronegativity,
    oxidation_states,
)
from periodisk.models import SourcedValue


def test_configuration_shows_single_electrons_and_has_no_spaces() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert electron_configuration(by_symbol["H"]) == "1s¹"
    assert electron_configuration(by_symbol["U"]) == "[Rn]5f³6d¹7s²"


def test_long_configuration_is_compact_and_explicit() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert electron_configuration(by_symbol["Og"]) == "[Rn]5f¹⁴6d¹⁰7s²7p⁶"


def test_carbon_complete_integer_range_has_compact_display() -> None:
    carbon = next(element for element in load_elements() if element.symbol == "C")
    assert carbon.oxidation_states.value["main"] == list(range(-4, 5))
    assert oxidation_states(carbon) == "−4…+4"


def test_negative_oxidation_states_use_true_minus_sign() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert oxidation_states(by_symbol["H"]) == "\u22121 +1"
    assert all("-" not in oxidation_states(element) for element in load_elements())


def test_pauling_electronegativity_keeps_source_precision() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    expected = {
        "H": "2,20",
        "Ca": "1,00",
        "Cu": "1,90",
        "Nb": "1,6",
        "Xe": "2,60",
        "Lu": "1,0",
        "Po": "2,0",
        "U": "1,7",
    }
    for symbol, text in expected.items():
        assert electronegativity(by_symbol[symbol], "pauling", ",") == text
    assert electronegativity(by_symbol["He"], "pauling", ",") == "—"


def test_calculated_electronegativities_show_two_decimals() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert electronegativity(by_symbol["Ra"], "allred-rochow", ".") == "1.00"
    assert electronegativity(by_symbol["H"], "allen", ".") == "2.30"


def test_electronegativity_without_display_falls_back_to_value() -> None:
    from dataclasses import replace

    hydrogen = next(element for element in load_elements() if element.symbol == "H")
    plain = replace(
        hydrogen,
        electronegativity={"pauling": SourcedValue(value=2.2, source="test")},
    )
    assert electronegativity(plain, "pauling", ",") == "2,2"
