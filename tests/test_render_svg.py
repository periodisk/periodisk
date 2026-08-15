from dataclasses import replace
from xml.etree import ElementTree as ET

import pytest

from periodisk import render_svg
from periodisk._render_svg import CATEGORY_COLOURS, SVG, _render_cell
from periodisk.data import load_elements, load_locale
from periodisk.layout import Page
from periodisk.palettes import PALETTES, THEME


def _relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def test_rendered_svg_is_a3_and_contains_every_element(tmp_path) -> None:
    output = render_svg(tmp_path / "table.svg")
    root = ET.parse(output).getroot()
    assert root.attrib["width"] == "420mm"
    assert root.attrib["height"] == "297mm"
    assert root.attrib["viewBox"] == "0 0 420 297"
    groups = root.findall(f".//{{{SVG}}}g")
    element_groups = [
        group for group in groups if group.attrib.get("id", "").startswith("element-")
    ]
    assert len(element_groups) == 118
    assert root.find(f".//{{{SVG}}}g[@id='element-U']") is not None


def test_a4_svg_uses_a4_physical_size_with_same_vector_layout(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table-a4.svg", page_size="A4")).getroot()
    assert root.attrib["width"] == "297mm"
    assert root.attrib["height"] == "210mm"
    assert root.attrib["viewBox"] == "0 0 420 297"


def test_norwegian_rendering_uses_decimal_comma(tmp_path) -> None:
    output = render_svg(tmp_path / "table-nb.svg", language="nb_NO")
    text = output.read_text(encoding="utf-8")
    assert "Periodesystemet" in text
    assert "1,0080" in text
    assert "røntgenium" in text


def test_electronegativity_scale_is_selectable_and_localised(tmp_path) -> None:
    output = render_svg(
        tmp_path / "table-nb-allred.svg",
        language="nb_NO",
        electronegativity_scale="allred-rochow",
    )
    text = output.read_text(encoding="utf-8")
    assert "Allred–Rochow/Pyykkö (beregnet elektronegativitet)" in text
    assert ">4,25</text>" in text

    allen = render_svg(
        tmp_path / "table-nb-allen.svg",
        language="nb_NO",
        electronegativity_scale="allen",
    ).read_text(encoding="utf-8")
    assert "Allen/Mendeleev 1.2.0 (reskalert Allen-elektronegativitet)" in allen
    assert ">2,3</text>" in allen


def test_unknown_electronegativity_scale_is_rejected(tmp_path) -> None:
    with pytest.raises(ValueError, match="Unsupported electronegativity"):
        render_svg(tmp_path / "bad.svg", electronegativity_scale="made-up")


def test_categories_have_solid_colour_legend(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table.svg")).getroot()
    assert root.findall(f".//{{{SVG}}}pattern") == []
    legend = root.findall(f".//{{{SVG}}}g[@class='legend-item']")
    assert len(legend) == 12
    fills = {
        item.attrib["data-category"]: item.find(f"{{{SVG}}}rect").attrib["fill"]
        for item in legend
        if item.attrib["data-category"] != "split-classification"
    }
    assert fills == CATEGORY_COLOURS

    split = next(
        item
        for item in legend
        if item.attrib["data-category"] == "split-classification"
    )
    assert len(split.findall(f"{{{SVG}}}polygon")) == 2
    assert any(
        node.text == "Two classifications" for node in split.findall(f"{{{SVG}}}text")
    )


def test_palette_has_at_least_wcag_aa_contrast_with_its_text_colour() -> None:
    assert all(
        _contrast(colour, THEME["text"]) >= 4.5
        for palette in PALETTES.values()
        for colour in palette.values()
    )


def test_colour_scheme_is_selectable_and_rejects_unknown_names(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "light.svg", colour_scheme="light")).getroot()
    hydrogen = root.find(f".//{{{SVG}}}g[@id='element-H']")
    assert hydrogen is not None
    assert (
        hydrogen.find(
            f"{{{SVG}}}rect[@class='cell-fill category-reactive-nonmetal']"
        ).attrib["fill"]
        == PALETTES["light"]["reactive-nonmetal"]
    )
    powder = ET.parse(
        render_svg(tmp_path / "powder.svg", colour_scheme="powder")
    ).getroot()
    powder_hydrogen = powder.find(f".//{{{SVG}}}g[@id='element-H']")
    assert powder_hydrogen is not None
    assert (
        powder_hydrogen.find(
            f"{{{SVG}}}rect[@class='cell-fill category-reactive-nonmetal']"
        ).attrib["fill"]
        == "#C3DBFE"
    )
    blue_ramp = ET.parse(
        render_svg(tmp_path / "blue-ramp.svg", colour_scheme="blue-ramp")
    ).getroot()
    blue_ramp_hydrogen = blue_ramp.find(f".//{{{SVG}}}g[@id='element-H']")
    assert blue_ramp_hydrogen is not None
    assert (
        blue_ramp_hydrogen.find(
            f"{{{SVG}}}rect[@class='cell-fill category-reactive-nonmetal']"
        ).attrib["fill"]
        == "#F9CCCC"
    )
    tol_light = ET.parse(
        render_svg(tmp_path / "tol-light.svg", colour_scheme="tol-light-inspired")
    ).getroot()
    tol_light_hydrogen = tol_light.find(f".//{{{SVG}}}g[@id='element-H']")
    assert tol_light_hydrogen is not None
    assert (
        tol_light_hydrogen.find(
            f"{{{SVG}}}rect[@class='cell-fill category-reactive-nonmetal']"
        ).attrib["fill"]
        == "#BBCC33"
    )
    with pytest.raises(ValueError, match="Unsupported colour scheme"):
        render_svg(tmp_path / "bad.svg", colour_scheme="fluorescent")


def test_default_palette_is_tol_light_inspired_and_classic_is_preserved() -> None:
    assert PALETTES["default"] is PALETTES["tol-light-inspired"]
    assert PALETTES["classic"]["transition-metal"] == "#8EC9E6"


def test_simplified_content_keeps_identity_and_mass_but_omits_properties(
    tmp_path,
) -> None:
    root = ET.parse(
        render_svg(tmp_path / "simplified.svg", language="nb_NO", content="simplified")
    ).getroot()
    hydrogen = root.find(f".//{{{SVG}}}g[@id='element-H']")
    assert hydrogen is not None
    texts = hydrogen.findall(f"{{{SVG}}}text")
    assert {node.text for node in texts} == {"1", "1,0080", "H", "hydrogen"}
    assert (
        hydrogen.find(f"{{{SVG}}}text[@class='symbol simplified-symbol']") is not None
    )
    assert root.find(f".//{{{SVG}}}g[@id='guide-U']") is not None
    with pytest.raises(ValueError, match="Unsupported content mode"):
        render_svg(tmp_path / "bad-content.svg", content="minimalish")


def test_broad_classification_merges_families_and_preserves_splits(tmp_path) -> None:
    root = ET.parse(
        render_svg(tmp_path / "broad.svg", language="nb_NO", classification="broad")
    ).getroot()
    lithium = root.find(f".//{{{SVG}}}g[@id='element-Li']")
    iron = root.find(f".//{{{SVG}}}g[@id='element-Fe']")
    chlorine = root.find(f".//{{{SVG}}}g[@id='element-Cl']")
    assert lithium is not None and iron is not None and chlorine is not None
    assert (
        lithium.find(f"{{{SVG}}}rect[@class='cell-fill category-transition-metal']")
        is not None
    )
    assert (
        iron.find(f"{{{SVG}}}rect[@class='cell-fill category-transition-metal']")
        is not None
    )
    assert (
        chlorine.find(f"{{{SVG}}}rect[@class='cell-fill category-reactive-nonmetal']")
        is not None
    )
    astatine = root.find(f".//{{{SVG}}}g[@id='element-At']")
    assert astatine is not None
    assert len(astatine.findall(f"{{{SVG}}}polygon")) == 2
    legend_labels = {
        node.text
        for node in root.findall(f".//{{{SVG}}}g[@class='legend-item']/{{{SVG}}}text")
    }
    assert {"Metaller", "Halvmetaller", "Ikke-metaller", "Edelgasser"} <= legend_labels
    with pytest.raises(ValueError, match="Unsupported classification mode"):
        render_svg(tmp_path / "bad-classification.svg", classification="elementary")


def test_broad_light_palette_uses_one_colour_per_broad_class(tmp_path) -> None:
    root = ET.parse(
        render_svg(
            tmp_path / "broad-light.svg",
            colour_scheme="broad-light",
            classification="broad",
        )
    ).getroot()
    expected = {
        "Li": "#A8CBEB",
        "Fe": "#A8CBEB",
        "B": "#8FC47A",
        "O": "#F9CCCC",
        "Ne": "#D7B3EC",
    }
    for symbol, colour in expected.items():
        element = root.find(f".//{{{SVG}}}g[@id='element-{symbol}']")
        assert element is not None
        fill = next(
            node
            for node in element.findall(f"{{{SVG}}}rect")
            if node.attrib.get("class", "").startswith("cell-fill")
        )
        assert fill.attrib["fill"] == colour


def test_broad_tol_light_uses_tol_light_subset(tmp_path) -> None:
    root = ET.parse(
        render_svg(
            tmp_path / "broad-tol-light.svg",
            colour_scheme="broad-tol-light",
            classification="broad",
        )
    ).getroot()
    expected = {"Fe": "#77AADD", "B": "#44BB99", "O": "#EE8866", "Ne": "#FFAABB"}
    for symbol, colour in expected.items():
        element = root.find(f".//{{{SVG}}}g[@id='element-{symbol}']")
        assert element is not None
        fill = next(
            node
            for node in element.findall(f"{{{SVG}}}rect")
            if node.attrib.get("class", "").startswith("cell-fill")
        )
        assert fill.attrib["fill"] == colour


def test_cell_styles_are_selectable_and_structurally_distinct(tmp_path) -> None:
    gutters = ET.parse(
        render_svg(tmp_path / "gutters.svg", cell_style="gutters")
    ).getroot()
    gutters_h = gutters.find(f".//{{{SVG}}}g[@id='element-H']")
    assert gutters_h is not None
    assert (
        gutters_h.find(f"{{{SVG}}}rect[@class='element-cell']").attrib["x"] == "10.65"
    )

    soft = render_svg(tmp_path / "soft.svg", cell_style="soft-rules").read_text()
    assert f"stroke: {THEME['soft_rule']}; stroke-width: 0.16" in soft

    rounded_gutters = ET.parse(
        render_svg(
            tmp_path / "rounded-gutters.svg",
            cell_style="gutters",
            rounded_corners=True,
        )
    ).getroot()
    rounded_h = rounded_gutters.find(f".//{{{SVG}}}g[@id='element-H']")
    assert rounded_h is not None
    outline = rounded_h.find(f"{{{SVG}}}rect[@class='element-cell']")
    assert outline.attrib["x"] == "10.65"
    assert outline.attrib["rx"] == "0.8"

    with pytest.raises(ValueError, match="Unsupported cell style"):
        render_svg(tmp_path / "bad-style.svg", cell_style="embossed")


def test_rounded_corners_are_opt_in_and_clip_split_cells(tmp_path) -> None:
    square = ET.parse(render_svg(tmp_path / "square.svg")).getroot()
    square_h = square.find(f".//{{{SVG}}}g[@id='element-H']")
    assert square_h is not None
    assert "rx" not in square_h.find(f"{{{SVG}}}rect[@class='element-cell']").attrib

    rounded = ET.parse(
        render_svg(tmp_path / "rounded.svg", rounded_corners=True)
    ).getroot()
    rounded_h = rounded.find(f".//{{{SVG}}}g[@id='element-H']")
    assert rounded_h is not None
    assert rounded_h.find(f"{{{SVG}}}rect[@class='element-cell']").attrib["rx"] == "0.8"
    polonium = rounded.find(f".//{{{SVG}}}g[@id='element-Po']")
    assert polonium is not None
    assert polonium.find(f"{{{SVG}}}clipPath[@id='clip-element-Po']") is not None
    assert all(
        polygon.attrib["clip-path"] == "url(#clip-element-Po)"
        for polygon in polonium.findall(f"{{{SVG}}}polygon")
    )


def test_broad_classification_does_not_clip_collapsed_detailed_split() -> None:
    element = replace(
        load_elements()[2],
        classifications=("alkali-metal", "transition-metal"),
    )
    group = ET.Element(f"{{{SVG}}}svg")

    _render_cell(
        group,
        element,
        0,
        0,
        Page(),
        load_locale("en_GB"),
        "pauling",
        CATEGORY_COLOURS,
        rounded_corners=True,
        classification="broad",
    )

    assert group.find(f".//{{{SVG}}}clipPath") is None
    assert (
        group.find(f".//{{{SVG}}}rect[@class='cell-fill category-transition-metal']")
        is not None
    )


def test_po_and_at_have_diagonal_split_fills(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table.svg")).getroot()
    for symbol in ("Po", "At"):
        group = root.find(f".//{{{SVG}}}g[@id='element-{symbol}']")
        assert group is not None
        assert len(group.findall(f"{{{SVG}}}polygon")) == 2
        assert len(group.findall(f"{{{SVG}}}line")) == 0


def test_unknown_chemistry_uses_neutral_fill_without_question_mark(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table.svg")).getroot()
    for symbol in ("Mt", "Ds", "Rg", "Lv", "Ts", "Og"):
        group = root.find(f".//{{{SVG}}}g[@id='element-{symbol}']")
        assert group is not None
        assert group.attrib["data-chemistry-status"] == "unknown"
        fills = group.findall(f"{{{SVG}}}rect[@class='cell-fill unknown-fill']")
        assert len(fills) == 1
        assert fills[0].attrib["fill"] == CATEGORY_COLOURS["unknown-chemistry"]
        assert not any(node.text == "?" for node in group.findall(f"{{{SVG}}}text"))


def test_cell_positions_mass_radioactivity_and_unlabelled_properties(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table.svg")).getroot()
    technetium = root.find(f".//{{{SVG}}}g[@id='element-Tc']")
    assert technetium is not None
    texts = technetium.findall(f"{{{SVG}}}text")
    by_class = {
        node.attrib["class"]: node
        for node in texts
        if node.attrib["class"] in {"atomic-number", "atomic-weight"}
    }
    assert by_class["atomic-number"].attrib.get("text-anchor") is None
    assert by_class["atomic-weight"].attrib["text-anchor"] == "end"
    radioactive = technetium.find(f"{{{SVG}}}g[@class='radioactive']")
    assert radioactive is not None
    assert radioactive.attrib["role"] == "img"
    assert radioactive.attrib["aria-label"] == "No stable isotopes"
    assert len(radioactive.findall(f"{{{SVG}}}path[@class='radioactive-blade']")) == 3
    assert radioactive.find(f"{{{SVG}}}circle[@class='radioactive-ring']") is not None
    assert radioactive.find(f"{{{SVG}}}circle[@class='radioactive-centre']") is not None
    assert not any(node.text == "☢" for node in texts)
    assert all(
        not (node.text or "").startswith(("χ ", "IE ", "ox ", "oks ")) for node in texts
    )


def test_unheaded_uranium_guide_and_period_numbers_are_present(tmp_path) -> None:
    root = ET.parse(render_svg(tmp_path / "table.svg")).getroot()
    assert root.find(f".//{{{SVG}}}g[@id='guide-U']") is not None
    assert not any(
        node.text == "How to read an element"
        for node in root.findall(f".//{{{SVG}}}text")
    )
    periods = root.findall(f".//{{{SVG}}}text[@class='period-number']")
    assert [node.text for node in periods] == list("1234567")
    leaders = root.findall(f".//{{{SVG}}}line[@class='guide-line']")
    assert (
        len([line for line in leaders if line.attrib["y1"] == line.attrib["y2"]]) == 8
    )
    assert (
        len([line for line in leaders if line.attrib["x1"] == line.attrib["x2"]]) == 1
    )
    horizontal_by_y = {
        float(line.attrib["y1"]): line
        for line in leaders
        if line.attrib["y1"] == line.attrib["y2"]
    }
    top_lines = sorted(
        (line for line in leaders if float(line.attrib["y1"]) == 45.0),
        key=lambda line: float(line.attrib["x1"]),
    )
    atomic_number_line, mass_line = top_lines
    assert float(atomic_number_line.attrib["x2"]) <= 136.5
    assert float(mass_line.attrib["x2"]) >= 165.5
    oxidation_line = horizontal_by_y[66.8]
    assert float(oxidation_line.attrib["x2"]) <= 142.0
    guide_labels = [
        node.text for node in root.findall(f".//{{{SVG}}}text[@class='guide-label']")
    ]
    assert "Atomic mass ([ ] = mass number of longest-lived isotope)" in guide_labels
    assert "Electron configuration (ground state; predicted for Rf–Og)" in guide_labels


def test_scientific_sources_are_in_heading_block(tmp_path) -> None:
    root = ET.parse(
        render_svg(tmp_path / "table.svg", electronegativity_scale="pauling")
    ).getroot()
    sources = root.findall(f".//{{{SVG}}}text[@class='source']")
    source_text = " ".join(node.text or "" for node in sources)
    assert "Sources: CIAAW 2024 (atomic masses)" in source_text
    assert "NIST ASD (ionisation energies)" in source_text
    assert "CRC Handbook (Pauling electronegativity)" in source_text
    assert "Mendeleev 1.2.0" in source_text
    assert "Oxidation states: selection adapted from Mendeleev 1.2.0" in source_text
    assert "DATA_SOURCES.md" not in source_text
    assert "provisional oxidation states" not in source_text
    assert "Data snapshot" not in source_text
    assert "MIT licensed" not in source_text
    footers = root.findall(f".//{{{SVG}}}text[@class='footer']")
    footer_text = " ".join(node.text or "" for node in footers)
    assert "Periodisk contributors · CC BY 4.0" in footer_text
    assert len(footers) == 1
    assert float(footers[0].attrib["x"]) == 409.8
    assert footers[0].attrib["text-anchor"] == "end"
    style = root.find(f"{{{SVG}}}style")
    assert style is not None
    assert ".footer { fill: #666666;" in (style.text or "")
    metadata = root.find(f"{{{SVG}}}metadata")
    assert metadata is not None
    assert "separately licensed under MIT" in (metadata.text or "")


def test_norwegian_uses_lantanoider_and_actinoider(tmp_path) -> None:
    text = render_svg(tmp_path / "nb.svg", language="nb_NO").read_text(encoding="utf-8")
    assert "Lantanoider" in text
    assert "Actinoider" in text
    assert "Lantanider" not in text
    assert "Aktinider" not in text
