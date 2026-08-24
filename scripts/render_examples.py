#!/usr/bin/env python3
"""Regenerate the canonical English and Norwegian example outputs."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from periodisk import render_table

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "examples"
LOCALE_SLUGS = {"en_GB": "en", "nb_NO": "nb"}


@dataclass(frozen=True, slots=True)
class Example:
    """One documented example variant and its supported output formats."""

    suffix: str
    formats: tuple[str, ...]
    options: dict[str, object] = field(default_factory=dict)


EXAMPLES = (
    Example("a3", ("pdf", "svg"), {"page_size": "A3"}),
    Example("a4", ("pdf",), {"page_size": "A4"}),
    Example(
        "a3-broad-light-simplified-broad",
        ("pdf", "svg"),
        {
            "page_size": "A3",
            "colour_scheme": "broad-light",
            "content": "simplified",
            "classification": "broad",
        },
    ),
    Example(
        "a3-powder-gutters-rounded",
        ("pdf",),
        {
            "page_size": "A3",
            "colour_scheme": "powder",
            "cell_style": "gutters",
            "rounded_corners": True,
        },
    ),
)


def example_outputs(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    formats: Iterable[str] = ("pdf", "svg"),
) -> Iterator[tuple[Path, str, dict[str, object]]]:
    """Yield every canonical output path and its renderer options."""

    selected_formats = set(formats)
    for language, slug in LOCALE_SLUGS.items():
        for example in EXAMPLES:
            for output_format in example.formats:
                if output_format not in selected_formats:
                    continue
                filename = f"periodic-table-{slug}-{example.suffix}.{output_format}"
                output = output_root / language / output_format / filename
                yield output, output_format, {"language": language, **example.options}


def render_examples(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    formats: Iterable[str] = ("pdf", "svg"),
) -> tuple[Path, ...]:
    """Render the selected canonical examples and return their paths."""

    rendered = []
    for output, output_format, options in example_outputs(output_root, formats=formats):
        rendered.append(render_table(output, output_format=output_format, **options))
        print(f"Wrote {output}")
    return tuple(rendered)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--format",
        dest="formats",
        action="append",
        choices=("pdf", "svg"),
        help="render only this format; repeat to select both",
    )
    args = parser.parse_args()
    render_examples(args.output_root, formats=args.formats or ("pdf", "svg"))


if __name__ == "__main__":
    main()
