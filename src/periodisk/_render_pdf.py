"""PDF output derived from the canonical SVG renderer."""

from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from ._render_svg import SVG, render_svg

_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def _font_rules(style: str) -> list[tuple[set[str], bool, dict[str, str]]]:
    """Parse the renderer's own flat CSS into (selectors, is-type-rule, fonts)."""

    rules = []
    for selectors, body in _RULE.findall(style):
        declarations = {}
        for declaration in body.split(";"):
            name, _, value = declaration.partition(":")
            if name.strip() in {"font-family", "font-size", "font-weight"}:
                declarations[name.strip()] = value.strip()
        if not declarations:
            continue
        names = {selector.strip() for selector in selectors.split(",")}
        classes = {name[1:] for name in names if name.startswith(".")}
        rules.append((classes, "text" in names, declarations))
    return rules


def _font(
    node: ET.Element,
    rules: list[tuple[set[str], bool, dict[str, str]]],
    inherited: dict[str, str] | None = None,
) -> dict[str, str]:
    """Resolve a node's font as CairoSVG does: type rules, then class rules."""

    font = dict(inherited or {})
    classes = set(node.attrib.get("class", "").split())
    for _, is_type_rule, declarations in rules:
        if is_type_rule and inherited is None:
            font.update(declarations)
    for selector_classes, _, declarations in rules:
        if selector_classes & classes:
            font.update(declarations)
    return font


def _advance(context, text: str, font: dict[str, str]) -> float:
    import cairocffi as cairo

    family = font.get("font-family", "sans-serif").split(",")[0].strip("\"' ")
    weight = font.get("font-weight", "normal")
    bold = weight == "bold" or (weight.isdigit() and int(weight) >= 550)
    context.select_font_face(
        family,
        cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL,
    )
    context.set_font_size(float(font.get("font-size", "12").removesuffix("px")))
    return context.text_extents(text)[4]


def _anchor_mixed_text(root: ET.Element) -> None:
    """Left-align centred or right-aligned text that contains spans.

    CairoSVG aligns each span of a text element separately, so a span inside
    centred text (the fallback-font minus sign) overlaps its neighbours.
    Measure the spans with Cairo and start the text at the aligned position.
    """

    import cairocffi as cairo

    style = root.find(f"{{{SVG}}}style")
    rules = _font_rules(style.text or "") if style is not None else []
    surface = cairo.PDFSurface(None, 1, 1)
    context = cairo.Context(surface)
    options = cairo.FontOptions()
    options.set_hint_metrics(cairo.HINT_METRICS_OFF)
    context.set_font_options(options)
    for node in root.iter(f"{{{SVG}}}text"):
        anchor = node.attrib.get("text-anchor")
        if not len(node) or anchor not in {"middle", "end"}:
            continue
        font = _font(node, rules)
        width = _advance(context, node.text or "", font)
        for child in node:
            width += _advance(context, child.text or "", _font(child, rules, font))
            width += _advance(context, child.tail or "", font)
        shift = width / 2 if anchor == "middle" else width
        node.set("x", f"{float(node.attrib['x']) - shift:.2f}")
        node.set("text-anchor", "start")
        node.attrib.pop("textLength", None)
        node.attrib.pop("lengthAdjust", None)
    surface.finish()


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
        tree = ET.parse(svg)
        _anchor_mixed_text(tree.getroot())
        tree.write(svg, encoding="utf-8", xml_declaration=True)
        cairosvg.svg2pdf(url=str(svg), write_to=str(destination))
    return destination
