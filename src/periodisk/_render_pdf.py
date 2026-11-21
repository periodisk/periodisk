"""PDF output derived from the canonical SVG renderer."""

from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from ._render_svg import SVG, render_svg

_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


FontRules = list[tuple[list[set[str]], bool, dict[str, str]]]


def _font_rules(style: str) -> FontRules:
    """Parse the renderer's own flat CSS into (selectors, is-type-rule, fonts).

    Each class selector is a set of classes, so a compound selector such as
    `.atomic-weight.simplified-top-number` matches only nodes with both.
    """

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
        classes = [set(name[1:].split(".")) for name in names if name.startswith(".")]
        rules.append((classes, "text" in names, declarations))
    return rules


def _font(
    node: ET.Element,
    rules: FontRules,
    inherited: dict[str, str] | None = None,
) -> dict[str, str]:
    """Resolve a node's font as CairoSVG does: type rules, then class rules."""

    font = dict(inherited or {})
    classes = set(node.attrib.get("class", "").split())
    for _, is_type_rule, declarations in rules:
        if is_type_rule and inherited is None:
            font.update(declarations)
    for selectors, _, declarations in rules:
        if any(selector <= classes for selector in selectors):
            font.update(declarations)
    return font


def _cairo_face(font: dict[str, str]) -> tuple[str, bool]:
    """Return the family and boldness CairoSVG selects for a resolved font.

    CairoSVG uses only the first family in a stack, and treats numeric weights
    from 550 upwards as bold.
    """

    family = font.get("font-family", "sans-serif").split(",")[0].strip("\"' ")
    weight = font.get("font-weight", "normal")
    return family, weight == "bold" or (weight.isdigit() and int(weight) >= 550)


def _select_font(context, font: dict[str, str]) -> None:
    import cairocffi as cairo

    family, bold = _cairo_face(font)
    context.select_font_face(
        family,
        cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL,
    )
    context.set_font_size(float(font.get("font-size", "12").removesuffix("px")))


def _advance(context, text: str, font: dict[str, str]) -> float:
    _select_font(context, font)
    return context.text_extents(text)[4]


def _text_runs(node: ET.Element, rules: FontRules) -> list[tuple[str, dict[str, str]]]:
    """Split a text element into (text, resolved font) runs, spans included."""

    font = _font(node, rules)
    runs = [(node.text or "", font)]
    for child in node:
        runs.append((child.text or "", _font(child, rules, font)))
        runs.append((child.tail or "", font))
    return runs


def _missing_glyphs(root: ET.Element) -> list[tuple[str, str, bool, str]]:
    """List characters the fonts CairoSVG will select cannot draw.

    Cairo has no per-glyph fallback, so a character missing from the selected
    font is drawn as a missing-glyph box in the PDF. Returns sorted, unique
    (character, family, bold, example text) entries; empty means every
    character has a glyph.
    """

    import cairocffi as cairo

    style = root.find(f"{{{SVG}}}style")
    rules = _font_rules(style.text or "") if style is not None else []
    surface = cairo.PDFSurface(None, 1, 1)
    context = cairo.Context(surface)
    known: dict[tuple[str, str, bool], bool] = {}
    missing: dict[tuple[str, str, bool], str] = {}
    for node in root.iter(f"{{{SVG}}}text"):
        runs = _text_runs(node, rules)
        example = "".join(text for text, _ in runs)
        for text, font in runs:
            family, bold = _cairo_face(font)
            for character in set(text) - set(" \t\n"):
                key = (character, family, bold)
                if key not in known:
                    _select_font(context, font)
                    glyphs = context.get_scaled_font().text_to_glyphs(
                        0, 0, character, False
                    )
                    known[key] = all(glyph[0] != 0 for glyph in glyphs)
                if not known[key]:
                    missing.setdefault(key, example)
    surface.finish()
    return sorted((*key, example) for key, example in missing.items())


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
        width = sum(
            _advance(context, text, font) for text, font in _text_runs(node, rules)
        )
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
