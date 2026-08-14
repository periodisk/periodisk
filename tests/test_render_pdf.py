import pytest
from pypdf import PdfReader

from periodisk.render import render_table
from periodisk.render_pdf import render_pdf


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
