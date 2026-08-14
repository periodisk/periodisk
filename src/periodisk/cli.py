"""Command-line interface for dataset maintenance and rendering."""

from __future__ import annotations

import argparse

from .data import load_elements, load_sources
from .palettes import SUPPORTED_COLOUR_SCHEMES
from .render import render_table
from .render_svg import (
    SUPPORTED_CELL_STYLES,
    SUPPORTED_CLASSIFICATION_MODES,
    SUPPORTED_CONTENT_MODES,
)
from .settings import SUPPORTED_ELECTRONEGATIVITY_SCALES, SUPPORTED_LOCALES
from .validation import validate_dataset


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="periodisk")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate bundled scientific data")
    validate.add_argument(
        "--release",
        action="store_true",
        help="also require all 118 elements and both supported languages",
    )
    render = commands.add_parser("render", help="render a landscape SVG or PDF table")
    render.add_argument("output", help="output path; suffix selects SVG or PDF")
    render.add_argument("--format", choices=("svg", "pdf"), default=None)
    render.add_argument("--page-size", choices=("A3", "A4"), default="A3")
    render.add_argument("--language", choices=SUPPORTED_LOCALES, default="en_GB")
    render.add_argument(
        "--colour-scheme", choices=SUPPORTED_COLOUR_SCHEMES, default="default"
    )
    render.add_argument(
        "--rounded-corners",
        action="store_true",
        help="use a subtle 0.8 mm radius on element and placeholder cells",
    )
    render.add_argument(
        "--cell-style",
        choices=SUPPORTED_CELL_STYLES,
        default="full",
        help="select the cell fill and rule treatment",
    )
    render.add_argument(
        "--content",
        choices=SUPPORTED_CONTENT_MODES,
        default="full",
        help="select full scientific content or simplified element cells",
    )
    render.add_argument(
        "--classification",
        choices=SUPPORTED_CLASSIFICATION_MODES,
        default="detailed",
        help="select detailed families or broad chemical classes",
    )
    render.add_argument(
        "--electronegativity-scale",
        choices=SUPPORTED_ELECTRONEGATIVITY_SCALES,
        default="pauling",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate":
        errors = validate_dataset(load_elements(), load_sources(), release=args.release)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        mode = "release" if args.release else "structural"
        print(f"Dataset passed {mode} validation.")
        return 0
    if args.command == "render":
        output = render_table(
            args.output,
            language=args.language,
            electronegativity_scale=args.electronegativity_scale,
            page_size=args.page_size,
            output_format=args.format,
            colour_scheme=args.colour_scheme,
            rounded_corners=args.rounded_corners,
            cell_style=args.cell_style,
            content=args.content,
            classification=args.classification,
        )
        print(f"Wrote {output}")
        return 0
    return 2
