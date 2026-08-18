"""Accessible, source-traceable periodic tables."""

from ._render_pdf import render_pdf
from ._render_svg import SUPPORTED_CELL_STYLES, render_svg
from .data import load_elements, load_locale, load_sources
from .models import Element, Source
from .palettes import PALETTES, SUPPORTED_COLOUR_SCHEMES
from .render import render_table
from .settings import SUPPORTED_ELECTRONEGATIVITY_SCALES, SUPPORTED_LOCALES

__all__ = [
    "Element",
    "Source",
    "load_elements",
    "load_locale",
    "load_sources",
    "render_svg",
    "render_pdf",
    "render_table",
    "SUPPORTED_ELECTRONEGATIVITY_SCALES",
    "SUPPORTED_LOCALES",
    "PALETTES",
    "SUPPORTED_COLOUR_SCHEMES",
    "SUPPORTED_CELL_STYLES",
]
__version__ = "2026.4"
