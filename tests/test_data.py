import pytest

from periodisk.data import (
    _validate_locale,
    load_elements,
    load_locale,
    load_sources,
)


def test_complete_resources_load() -> None:
    elements = load_elements()
    assert len(elements) == 118
    assert [element.atomic_number for element in elements] == list(range(1, 119))
    assert "giuliani-et-al-2019" in load_sources()


def test_british_and_norwegian_names() -> None:
    symbols = {element.symbol for element in load_elements()}
    english = load_locale("en_GB")["element_names"]
    norwegian = load_locale("nb_NO")["element_names"]
    assert english["Al"] == "aluminium"
    assert english["Cs"] == "caesium"
    assert norwegian["Fe"] == "jern"
    assert set(english) == set(norwegian) == symbols


def test_ciaaw_2024_abridged_atomic_weights_use_one_display_value() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert by_symbol["H"].atomic_weight.value == {
        "kind": "abridged-standard",
        "value": "1.0080",
        "uncertainty": "0.0002",
        "display": "1.0080",
        "ciaaw_notes": ["m"],
    }
    assert by_symbol["Zr"].atomic_weight.value["display"] == "91.222"
    assert by_symbol["Gd"].atomic_weight.value["display"] == "157.25"
    assert by_symbol["Lu"].atomic_weight.value["display"] == "174.97"
    assert by_symbol["Tc"].atomic_weight.value == {
        "kind": "mass-number",
        "value": 97,
        "display": "[97]",
    }
    assert by_symbol["Lr"].atomic_weight.value["display"] == "[266]"
    assert by_symbol["Nh"].atomic_weight.value["display"] == "[286]"
    assert by_symbol["Fl"].atomic_weight.value["display"] == "[290]"
    assert by_symbol["Mc"].atomic_weight.value["display"] == "[290]"
    assert by_symbol["Lv"].atomic_weight.value["display"] == "[293]"


def test_sensitive_classification_and_measurement_cases() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert by_symbol["Po"].classifications == ("post-transition-metal", "metalloid")
    assert by_symbol["At"].classifications == ("halogen", "metalloid")
    for symbol in ("Mt", "Ds", "Rg", "Lv", "Ts", "Og"):
        assert by_symbol[symbol].chemistry_status == "unknown"
        assert by_symbol[symbol].first_ionisation_energy.value is None
        assert by_symbol[symbol].electronegativity == {}


def test_reviewed_transactinide_configuration_overrides() -> None:
    elements = load_elements()
    by_symbol = {element.symbol: element for element in elements}
    by_number = {element.atomic_number: element for element in elements}
    assert by_symbol["Ds"].electron_configuration.value == "[Rn] 5f14 6d8 7s2"
    assert by_symbol["Ds"].electron_configuration.source == "hoffman-lee-pershina-2006"
    assert by_symbol["Rg"].electron_configuration.value == "[Rn] 5f14 6d9 7s2"
    assert by_symbol["Rg"].electron_configuration.source == "kaygorodov-et-al-2022"
    for number in range(104, 119):
        note = by_number[number].electron_configuration.note
        assert note is not None
        assert "Predicted" in note


def test_no_stable_isotope_flag_includes_bismuth() -> None:
    by_symbol = {element.symbol: element for element in load_elements()}
    assert by_symbol["Pb"].has_no_stable_isotopes.value is False
    assert by_symbol["Bi"].has_no_stable_isotopes.value is True
    assert by_symbol["Th"].has_no_stable_isotopes.value is True


def test_ionisation_energy_is_converted_to_kilojoules_per_mole() -> None:
    hydrogen = load_elements()[0]
    assert hydrogen.first_ionisation_energy.unit == "kJ/mol"
    assert hydrogen.first_ionisation_energy.value == pytest.approx(1312.05, abs=0.001)


def test_locales_use_requested_decimal_separators() -> None:
    assert load_locale("en_GB")["decimal_separator"] == "."
    assert load_locale("nb_NO")["decimal_separator"] == ","
    assert load_locale("en_GB")["abbreviations"]["oxidation_states"] == "ox"
    assert load_locale("nb_NO")["abbreviations"]["oxidation_states"] == "oks"
    assert (
        load_locale("en_GB")["source_notes"]["oxidation_states"]
        == "Oxidation states: selection adapted from Mendeleev 1.2.0"
    )
    assert (
        load_locale("nb_NO")["labels"]["unknown_chemistry"]
        == "Ufullstendig karakterisert"
    )
    assert (
        load_locale("nb_NO")["source_notes"]["electron_configurations"]
        == "elektronkonfigurasjoner; Ds og Rg fra nyere beregninger"
    )
    assert (
        load_locale("nb_NO")["source_notes"]["oxidation_states"]
        == "Oksidasjonstall: utvalg bearbeidet fra Mendeleev 1.2.0"
    )


def test_incomplete_locale_is_rejected() -> None:
    with pytest.raises(ValueError, match="element_names"):
        _validate_locale({"locale": "en_GB", "decimal_separator": "."}, "en_GB")


def test_unknown_locale_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported locale"):
        load_locale("en_US")
