from periodisk.data import load_elements
from periodisk.layout import Page, placements


def test_all_elements_are_placed_once_inside_page() -> None:
    page = Page()
    result = placements(load_elements(), page)
    assert len(result) == 118
    assert len({item.element.symbol for item in result}) == 118
    assert all(0 <= item.x <= page.width - page.cell_width for item in result)
    assert all(0 <= item.y <= page.height - page.cell_height for item in result)


def test_long_form_and_f_block_positions() -> None:
    by_symbol = {item.element.symbol: item for item in placements(load_elements())}
    assert (by_symbol["H"].row, by_symbol["H"].column) == (1, 1)
    assert (by_symbol["He"].row, by_symbol["He"].column) == (1, 18)
    assert (by_symbol["Fe"].row, by_symbol["Fe"].column) == (4, 8)
    assert (by_symbol["La"].section, by_symbol["La"].column) == ("lanthanides", 3)
    assert (by_symbol["Lu"].section, by_symbol["Lu"].column) == ("lanthanides", 17)
    assert (by_symbol["Ac"].section, by_symbol["Ac"].column) == ("actinides", 3)
