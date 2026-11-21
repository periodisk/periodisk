import itertools
from xml.etree import ElementTree as ET

import pytest
from pypdf import PdfReader

from periodisk import render_pdf
from periodisk._render_pdf import _font, _font_rules, _missing_glyphs
from periodisk._render_svg import SVG, render_svg
from periodisk.render import render_table


def _page_size_points(path):
    page = PdfReader(path).pages[0]
    return float(page.mediabox.width), float(page.mediabox.height)


def test_a3_pdf_has_exact_landscape_page_size_without_symbol_font(tmp_path) -> None:
    output = render_pdf(tmp_path / "table-a3.pdf")
    reader = PdfReader(output)
    assert len(reader.pages) == 1
    width, height = _page_size_points(output)
    assert width == pytest.approx(1190.55, abs=0.1)
    assert height == pytest.approx(841.89, abs=0.1)
    fonts = reader.pages[0]["/Resources"].get("/Font")
    assert fonts
    base_fonts = {str(font.get_object().get("/BaseFont")) for font in fonts.values()}
    assert not any("NotoSansSymbols2" in name for name in base_fonts)


def test_a4_pdf_has_exact_landscape_page_size(tmp_path) -> None:
    output = render_pdf(tmp_path / "table-a4.pdf", page_size="A4", language="nb_NO")
    width, height = _page_size_points(output)
    assert width == pytest.approx(841.89, abs=0.1)
    assert height == pytest.approx(595.28, abs=0.1)


def test_format_is_inferred_from_output_suffix(tmp_path) -> None:
    output = render_table(tmp_path / "inferred.pdf")
    assert output.read_bytes().startswith(b"%PDF-")


def test_mixed_font_text_is_left_aligned_at_its_measured_position() -> None:
    from periodisk._render_pdf import _anchor_mixed_text

    root = ET.fromstring(
        f'<svg xmlns="{SVG}"><style>'
        'text { font-family: "Noto Sans"; } .ox { font-size: 10px; } '
        '.minus { font-family: "DejaVu Sans"; }</style>'
        '<text x="50" y="10" class="ox" text-anchor="middle" textLength="9">'
        '<tspan class="minus">−</tspan>1 +1</text>'
        '<text x="50" y="20" class="ox" text-anchor="middle">+1</text></svg>'
    )
    _anchor_mixed_text(root)
    mixed, plain = root.findall(f"{{{SVG}}}text")
    assert mixed.attrib["text-anchor"] == "start"
    assert "textLength" not in mixed.attrib
    # Centred on x = 50: starts left of the centre by half its natural width.
    assert 30 < float(mixed.attrib["x"]) < 49
    assert plain.attrib == {
        "x": "50",
        "y": "20",
        "class": "ox",
        "text-anchor": "middle",
    }


def test_pdf_minus_signs_extract_as_text(tmp_path) -> None:
    output = render_pdf(tmp_path / "table.pdf", page_size="A4")
    text = PdfReader(output).pages[0].extract_text()
    assert "−1 +1" in text


@pytest.mark.parametrize(
    ("language", "content", "classification", "scale"),
    list(
        itertools.product(
            ("en_GB", "nb_NO"),
            ("full", "simplified"),
            ("detailed", "broad"),
            ("pauling", "allred-rochow", "allen"),
        )
    ),
)
def test_every_rendered_character_has_a_glyph_in_its_pdf_font(
    tmp_path, language, content, classification, scale
) -> None:
    # Cairo has no per-glyph font fallback, so a character missing from the
    # selected font becomes a box in the PDF (as U+2212 did in 2026.5 with
    # Debian's Noto Sans). The result depends on the fonts installed here.
    root = ET.parse(
        render_svg(
            tmp_path / "table.svg",
            language=language,
            content=content,
            classification=classification,
            electronegativity_scale=scale,
        )
    ).getroot()
    missing = [
        f"U+{ord(character):04X} {character!r} in {family}"
        f"{' Bold' if bold else ''} (in {example!r})"
        for character, family, bold, example in _missing_glyphs(root)
    ]
    assert not missing, "Characters without a glyph:\n" + "\n".join(missing)


def test_missing_glyph_check_reports_characters_no_font_has() -> None:
    unassigned = chr(0x0378)  # No font can have a glyph for an unassigned code point.
    root = ET.fromstring(
        f'<svg xmlns="{SVG}"><style>'
        'text { font-family: "Noto Sans"; } .label { font-weight: 700; }'
        "</style>"
        f'<text x="0" y="10">A{unassigned}</text>'
        f'<text x="0" y="20">ok <tspan class="label">{unassigned}</tspan></text>'
        "</svg>"
    )
    # Reported once per character and font, with the span checked in its own
    # (bold) font rather than its parent's.
    assert _missing_glyphs(root) == [
        (unassigned, "Noto Sans", False, f"A{unassigned}"),
        (unassigned, "Noto Sans", True, f"ok {unassigned}"),
    ]


def test_compound_class_selectors_require_every_class() -> None:
    rules = _font_rules(
        "text { font-family: A; } .x { font-size: 2px; } "
        ".x.y { font-size: 3px; } .p, .q { font-weight: 700; }"
    )
    assert _font(ET.Element("text", {"class": "x"}), rules)["font-size"] == "2px"
    assert _font(ET.Element("text", {"class": "x y"}), rules)["font-size"] == "3px"
    assert _font(ET.Element("text", {"class": "y"}), rules).get("font-size") is None
    assert _font(ET.Element("text", {"class": "q"}), rules)["font-weight"] == "700"
