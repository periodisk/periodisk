"""Format-neutral public rendering entry point."""

from __future__ import annotations

from pathlib import Path

from .render_pdf import render_pdf
from .render_svg import render_svg


def render_table(
    output: str | Path,
    *,
    language: str = "en_GB",
    electronegativity_scale: str = "pauling",
    page_size: str = "A3",
    output_format: str | None = None,
    colour_scheme: str = "default",
    rounded_corners: bool = False,
    cell_style: str = "full",
    content: str = "full",
    classification: str = "detailed",
) -> Path:
    """Render SVG or PDF, inferring the format from the output suffix by default."""

    destination = Path(output)
    selected = (output_format or destination.suffix.lstrip(".") or "svg").lower()
    options = {
        "language": language,
        "electronegativity_scale": electronegativity_scale,
        "page_size": page_size,
        "colour_scheme": colour_scheme,
        "rounded_corners": rounded_corners,
        "cell_style": cell_style,
        "content": content,
        "classification": classification,
    }
    if selected == "svg":
        return render_svg(destination, **options)
    if selected == "pdf":
        return render_pdf(destination, **options)
    raise ValueError(f"Unsupported output format: {selected!r}; choose svg or pdf")
