#!/usr/bin/env python3
"""Render the documented colour-scheme comparison from the package palettes."""

from pathlib import Path
from xml.etree import ElementTree as ET

from periodisk.palettes import PALETTES

SVG = "http://www.w3.org/2000/svg"
OUTPUT = Path(__file__).parents[1] / "docs" / "colour-schemes.svg"
CATEGORIES = {
    "alkali-metal": ("Alkali", "metal"),
    "alkaline-earth-metal": ("Alkaline-earth", "metal"),
    "transition-metal": ("Transition", "metal"),
    "post-transition-metal": ("Post-transition", "metal"),
    "metalloid": ("Metalloid",),
    "reactive-nonmetal": ("Nonmetal",),
    "halogen": ("Halogen",),
    "noble-gas": ("Noble gas",),
    "lanthanide": ("Lanthanide",),
    "actinide": ("Actinide",),
    "unknown-chemistry": ("Unknown", "chemistry"),
}


def _text(
    parent: ET.Element, x: float, y: float, value: str, **attrs: str
) -> ET.Element:
    node = ET.SubElement(parent, "text", {"x": str(x), "y": str(y), **attrs})
    node.text = value
    return node


def render(output: Path = OUTPUT) -> Path:
    left, top, cell_width, cell_height = 170, 80, 96, 38
    width = left + cell_width * len(CATEGORIES) + 20
    height = top + cell_height * len(PALETTES) + 42
    root = ET.Element(
        "svg",
        {
            "xmlns": SVG,
            "viewBox": f"0 0 {width} {height}",
            "role": "img",
            "aria-labelledby": "title description",
        },
    )
    ET.SubElement(root, "title", {"id": "title"}).text = "Periodic-table colour schemes"
    ET.SubElement(
        root, "desc", {"id": "description"}
    ).text = "Rows compare the category colours in every selectable scheme."
    ET.SubElement(root, "rect", {"width": "100%", "height": "100%", "fill": "#FFFFFF"})
    style = ET.SubElement(root, "style")
    style.text = "text{font-family:Arial,sans-serif;fill:#111} .scheme{font-size:13px;font-weight:700} .category{font-size:10px;font-weight:700;text-anchor:middle} .hex{font-size:10px;text-anchor:middle}"

    for column, labels in enumerate(CATEGORIES.values()):
        x = left + column * cell_width + cell_width / 2
        label = ET.SubElement(
            root, "text", {"class": "category", "x": str(x), "y": "45"}
        )
        for line, value in enumerate(labels):
            ET.SubElement(
                label, "tspan", {"x": str(x), "dy": "0" if line == 0 else "12"}
            ).text = value

    for row, (scheme, palette) in enumerate(PALETTES.items()):
        y = top + row * cell_height
        _text(root, 12, y + 24, scheme, **{"class": "scheme"})
        for column, category in enumerate(CATEGORIES):
            x = left + column * cell_width
            colour = palette[category]
            rect = ET.SubElement(
                root,
                "rect",
                {
                    "x": str(x + 2),
                    "y": str(y + 2),
                    "width": str(cell_width - 4),
                    "height": str(cell_height - 4),
                    "rx": "3",
                    "fill": colour,
                    "stroke": "#333333",
                    "stroke-width": "0.7",
                },
            )
            ET.SubElement(rect, "title").text = f"{scheme} · {category}: {colour}"
            _text(root, x + cell_width / 2, y + 25, colour, **{"class": "hex"})

    ET.indent(root)
    output.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(render())
