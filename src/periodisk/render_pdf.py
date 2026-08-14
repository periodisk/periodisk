"""PDF output derived from the canonical SVG renderer."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .render_svg import render_svg


def render_pdf(
    output: str | Path,
    *,
    language: str = "en_GB",
    electronegativity_scale: str = "pauling",
    page_size: str = "A3",
    colour_scheme: str = "default",
    rounded_corners: bool = False,
    cell_style: str = "full",
    content: str = "full",
    classification: str = "detailed",
) -> Path:
    """Render one vector PDF page and return its path."""

    try:
        import cairosvg
    except ImportError as error:  # pragma: no cover - installation problem
        raise RuntimeError("PDF output requires CairoSVG") from error

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="periodisk-") as directory:
        svg = render_svg(
            Path(directory) / "table.svg",
            language=language,
            electronegativity_scale=electronegativity_scale,
            page_size=page_size,
            colour_scheme=colour_scheme,
            rounded_corners=rounded_corners,
            cell_style=cell_style,
            content=content,
            classification=classification,
        )
        cairosvg.svg2pdf(url=str(svg), write_to=str(destination))
    return destination
