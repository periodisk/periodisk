import pytest
from pypdf import PdfReader

from periodisk import render_pdf
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
    from xml.etree import ElementTree as ET

    from periodisk._render_pdf import _anchor_mixed_text
    from periodisk._render_svg import SVG

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
