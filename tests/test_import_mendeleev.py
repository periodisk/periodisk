import pytest

from scripts.import_mendeleev import _half_life_seconds, pauling_display

SECONDS_PER_YEAR = 365.25 * 86_400


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2 s", 2.0),
        ("2 ms", 0.002),
        ("3 min", 180.0),
        ("4.2(2) h", 4.2 * 3_600),
        ("approx. 1.2e3 a", 1_200 * SECONDS_PER_YEAR),
        ("1.5E+2 ka", 150_000 * SECONDS_PER_YEAR),
        ("2 Ma", 2_000_000 * SECONDS_PER_YEAR),
    ],
)
def test_half_life_parser_normalises_supported_values(
    text: str, expected: float
) -> None:
    assert _half_life_seconds(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text",
    ["1.2e a", "< 1 s", "2 weeks", "unknown", "1 s trailing"],
)
def test_half_life_parser_rejects_malformed_values(text: str) -> None:
    with pytest.raises(ValueError, match="Unexpected CIAAW half-life"):
        _half_life_seconds(text)


def test_pauling_display_restores_crc_trailing_zeros() -> None:
    assert pauling_display("Ca", 1.0) == "1.00"
    assert pauling_display("Po", 2.0) == "2.0"
    assert pauling_display("Nb", 1.6) == "1.6"
    assert pauling_display("Fe", 1.83) == "1.83"


def test_pauling_display_rejects_a_changed_source_value() -> None:
    with pytest.raises(ValueError, match="does not equal"):
        pauling_display("Ca", 1.1)
