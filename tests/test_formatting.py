from periodisk.data import load_elements
from periodisk.formatting import electron_configuration, oxidation_states


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
