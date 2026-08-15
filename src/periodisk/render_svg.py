"""Render the canonical, resolution-independent SVG output."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from .data import load_elements, load_locale
from .formatting import (
    atomic_weight,
    electron_configuration,
    electronegativity,
    ionisation_energy,
    oxidation_states,
)
from .layout import Page, placeholder_positions, placements
from .models import Element
from .palettes import PALETTES, THEME, get_palette
from .settings import validate_electronegativity_scale

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)

CATEGORY_ORDER = (
    "alkali-metal",
    "alkaline-earth-metal",
    "transition-metal",
    "post-transition-metal",
    "metalloid",
    "reactive-nonmetal",
    "halogen",
    "noble-gas",
    "lanthanide",
    "actinide",
)

# Ten-family adaptation of Paul Tol's Light qualitative palette.
CATEGORY_COLOURS = PALETTES["default"]

PAGE_SIZES_MM = {
    "A3": (420.0, 297.0),
    "A4": (297.0, 210.0),
}

SUPPORTED_CELL_STYLES = (
    "full",
    "gutters",
    "soft-rules",
)
SUPPORTED_CONTENT_MODES = ("full", "simplified")
SUPPORTED_CLASSIFICATION_MODES = ("detailed", "broad")

METAL_CATEGORIES = {
    "alkali-metal",
    "alkaline-earth-metal",
    "transition-metal",
    "post-transition-metal",
    "lanthanide",
    "actinide",
}


def _display_categories(element: Element, classification: str) -> tuple[str, ...]:
    if classification == "detailed":
        return element.classifications
    mapped = []
    for category in element.classifications:
        if category in METAL_CATEGORIES:
            category = "transition-metal"
        elif category == "halogen":
            category = "reactive-nonmetal"
        if category not in mapped:
            mapped.append(category)
    return tuple(mapped)


def _node(parent: ET.Element, tag: str, **attributes: object) -> ET.Element:
    return ET.SubElement(
        parent,
        f"{{{SVG}}}{tag}",
        {key.replace("_", "-"): str(value) for key, value in attributes.items()},
    )


def _text(
    parent: ET.Element,
    text: str,
    x: float,
    y: float,
    css_class: str,
    *,
    anchor: str | None = None,
    max_width: float | None = None,
) -> ET.Element:
    attrs: dict[str, object] = {"x": f"{x:.2f}", "y": f"{y:.2f}", "class": css_class}
    if anchor:
        attrs["text_anchor"] = anchor
    if max_width is not None:
        attrs["textLength"] = f"{max_width:.2f}"
        attrs["lengthAdjust"] = "spacingAndGlyphs"
    node = _node(parent, "text", **attrs)
    node.text = text
    return node


def _fit_width(text: str, *, threshold: int, width: float) -> float | None:
    return width if len(text) > threshold else None


def _radioactive_symbol(
    parent: ET.Element,
    centre_x: float,
    centre_y: float,
    label: str,
) -> ET.Element:
    """Draw a compact radiation trefoil without relying on a symbol font."""

    group = _node(
        parent,
        "g",
        transform=f"translate({centre_x:.2f} {centre_y:.2f}) scale(1.28)",
        role="img",
        aria_label=label,
        **{"class": "radioactive"},
    )
    title = _node(group, "title")
    title.text = label
    _node(group, "circle", cx=0, cy=0, r=0.96, **{"class": "radioactive-ring"})
    # Broad, inward-curving blades and a generous centre follow the visual
    # proportions of Noto Sans Symbols 2 without embedding a font outline.
    blade = (
        "M 0,-0.81 "
        "C -0.22,-0.81 -0.34,-0.76 -0.41,-0.70 "
        "L -0.17,-0.30 "
        "C -0.13,-0.32 -0.05,-0.34 0,-0.34 "
        "C 0.06,-0.34 0.13,-0.32 0.17,-0.30 "
        "L 0.41,-0.70 "
        "C 0.34,-0.76 0.22,-0.81 0,-0.81 Z"
    )
    for rotation in (0, 120, 240):
        _node(
            group,
            "path",
            d=blade,
            transform=f"rotate({rotation})",
            **{"class": "radioactive-blade"},
        )
    _node(group, "circle", cx=0, cy=0, r=0.265, **{"class": "radioactive-centre"})
    return group


def _cell_background(
    group: ET.Element,
    element: Element,
    x: float,
    y: float,
    page: Page,
    colours: dict[str, str],
    corner_radius: float,
    clip_id: str,
    cell_style: str,
    categories: tuple[str, ...],
) -> None:
    inset = 0.45 if cell_style == "gutters" else 0.0
    x, y = x + inset, y + inset
    width, height = page.cell_width - 2 * inset, page.cell_height - 2 * inset
    rounded = {"rx": corner_radius, "ry": corner_radius} if corner_radius else {}
    if element.chemistry_status == "unknown":
        _node(
            group,
            "rect",
            x=f"{x:.2f}",
            y=f"{y:.2f}",
            width=width,
            height=height,
            fill=colours["unknown-chemistry"],
            **rounded,
            **{"class": "cell-fill unknown-fill"},
        )
        return

    if len(categories) == 2:
        first, second = categories
        _node(
            group,
            "polygon",
            points=f"{x:.2f},{y:.2f} {x + width:.2f},{y:.2f} {x:.2f},{y + height:.2f}",
            fill=colours[first],
            **{
                "class": f"cell-fill split-fill category-{first}",
                "clip-path": f"url(#{clip_id})",
            }
            if corner_radius
            else {"class": f"cell-fill split-fill category-{first}"},
        )
        _node(
            group,
            "polygon",
            points=f"{x + width:.2f},{y:.2f} {x + width:.2f},{y + height:.2f} {x:.2f},{y + height:.2f}",
            fill=colours[second],
            **{
                "class": f"cell-fill split-fill category-{second}",
                "clip-path": f"url(#{clip_id})",
            }
            if corner_radius
            else {"class": f"cell-fill split-fill category-{second}"},
        )
    else:
        category = categories[0]
        _node(
            group,
            "rect",
            x=f"{x:.2f}",
            y=f"{y:.2f}",
            width=width,
            height=height,
            fill=colours[category],
            **rounded,
            **{"class": f"cell-fill category-{category}"},
        )


def _legend(
    root: ET.Element,
    locale: dict,
    page: Page,
    colours: dict[str, str],
    classification: str,
) -> None:
    entries = (
        [*CATEGORY_ORDER, "unknown-chemistry", "split-classification"]
        if classification == "detailed"
        else [
            "transition-metal",
            "metalloid",
            "reactive-nonmetal",
            "noble-gas",
            "unknown-chemistry",
            "split-classification",
        ]
    )
    labels = dict(locale["classifications"])
    if classification == "broad":
        labels.update(locale["broad_classifications"])
    labels["unknown-chemistry"] = locale["labels"]["unknown_chemistry"]
    labels["split-classification"] = locale["labels"]["split_classification"]
    item_width = 66.0
    for index, category in enumerate(entries):
        row, column = divmod(index, 6)
        x = page.margin_x + column * item_width
        y = 251.0 + row * 8.0
        group = _node(root, "g", **{"class": "legend-item", "data-category": category})
        if category == "split-classification":
            _node(
                group,
                "polygon",
                points=f"{x:g},{y:g} {x + 8:g},{y:g} {x:g},{y + 5:g}",
                fill=colours[
                    "transition-metal"
                    if classification == "broad"
                    else "post-transition-metal"
                ],
                **{"class": "legend-split-fill"},
            )
            _node(
                group,
                "polygon",
                points=f"{x + 8:g},{y:g} {x + 8:g},{y + 5:g} {x:g},{y + 5:g}",
                fill=colours["metalloid"],
                **{"class": "legend-split-fill"},
            )
            _node(
                group,
                "rect",
                x=x,
                y=y,
                width=8,
                height=5,
                **{"class": "legend-swatch split-outline"},
            )
        else:
            _node(
                group,
                "rect",
                x=x,
                y=y,
                width=8,
                height=5,
                fill=colours[category],
                **{"class": "legend-swatch"},
            )
        label = labels[category]
        _text(
            group,
            label,
            x + 10,
            y + 3.6,
            "legend-label",
            max_width=_fit_width(label, threshold=27, width=54),
        )


def _render_cell(
    parent: ET.Element,
    element: Element,
    x: float,
    y: float,
    page: Page,
    locale: dict,
    scale: str,
    colours: dict[str, str],
    *,
    element_id: str | None = None,
    rounded_corners: bool = False,
    cell_style: str = "full",
    content: str = "full",
    classification: str = "detailed",
) -> None:
    resolved_id = element_id or f"element-{element.symbol}"
    corner_radius = 0.8 if rounded_corners else 0.0
    group = _node(
        parent,
        "g",
        id=resolved_id,
        **{
            "data-z": element.atomic_number,
            "data-classifications": " ".join(element.classifications),
            "data-chemistry-status": element.chemistry_status,
        },
    )
    clip_id = f"clip-{resolved_id}"
    inset = 0.45 if cell_style == "gutters" else 0.0
    cell_x, cell_y = x + inset, y + inset
    cell_width = page.cell_width - 2 * inset
    cell_height = page.cell_height - 2 * inset
    categories = _display_categories(element, classification)
    split_background = element.chemistry_status != "unknown" and len(categories) == 2
    if rounded_corners and split_background:
        clip = _node(group, "clipPath", id=clip_id)
        _node(
            clip,
            "rect",
            x=f"{cell_x:.2f}",
            y=f"{cell_y:.2f}",
            width=cell_width,
            height=cell_height,
            rx=corner_radius,
            ry=corner_radius,
        )
    _cell_background(
        group,
        element,
        x,
        y,
        page,
        colours,
        corner_radius,
        clip_id,
        cell_style,
        categories,
    )
    rounded = {"rx": corner_radius, "ry": corner_radius} if rounded_corners else {}
    _node(
        group,
        "rect",
        x=f"{cell_x:.2f}",
        y=f"{cell_y:.2f}",
        width=cell_width,
        height=cell_height,
        **rounded,
        **{"class": "element-cell"},
    )
    pad = 1.0
    centre = x + page.cell_width / 2
    right = x + page.cell_width - pad
    decimal = locale["decimal_separator"]
    missing = locale["missing_value"]

    simplified = content == "simplified"
    top_number_class = (
        "atomic-number simplified-top-number" if simplified else "atomic-number"
    )
    top_mass_class = (
        "atomic-weight simplified-top-number" if simplified else "atomic-weight"
    )
    _text(
        group,
        str(element.atomic_number),
        x + pad,
        y + 4.0 if simplified else y + 3.2,
        top_number_class,
    )
    mass = atomic_weight(element, decimal)
    _text(
        group,
        mass,
        right,
        y + 4.0 if simplified else y + 3.2,
        top_mass_class,
        anchor="end",
        max_width=_fit_width(
            mass, threshold=8 if simplified else 10, width=9.0 if simplified else 8.5
        ),
    )
    if element.has_no_stable_isotopes.value:
        _radioactive_symbol(group, centre, y + 2.35, locale["labels"]["radioactive"])
    _text(
        group,
        element.symbol,
        centre,
        y + (13.4 if simplified else 9.2),
        "symbol simplified-symbol" if simplified else "symbol",
        anchor="middle",
    )
    name = locale["element_names"][element.symbol]
    name_fit_threshold = 9 if simplified else 12
    _text(
        group,
        name,
        centre,
        y + (19.2 if simplified else 12.5),
        "name simplified-name" if simplified else "name",
        anchor="middle",
        max_width=_fit_width(
            name, threshold=name_fit_threshold, width=page.cell_width - 2
        ),
    )
    if simplified:
        return
    en = electronegativity(element, scale, decimal, missing)
    ie = ionisation_energy(element, decimal, missing)
    _text(group, en, x + pad, y + 16.0, "property")
    _text(group, ie, right, y + 16.0, "property", anchor="end")
    ox = oxidation_states(element, missing)
    _text(
        group,
        ox,
        centre,
        y + 19.2,
        "property",
        anchor="middle",
        max_width=_fit_width(ox, threshold=13, width=page.cell_width - 2),
    )
    config = electron_configuration(element)
    _text(
        group,
        config,
        centre,
        y + 23.0,
        "configuration",
        anchor="middle",
        max_width=_fit_width(config, threshold=18, width=page.cell_width - 2),
    )


def _guide_callout(
    parent: ET.Element,
    label: str,
    x: float,
    line_y: float,
    target_x: float,
    *,
    anchor: str,
) -> None:
    label_edge = x + 1.5 if anchor == "end" else x - 1.5
    _node(
        parent,
        "line",
        x1=label_edge,
        y1=line_y,
        x2=target_x,
        y2=line_y,
        **{"class": "guide-line"},
    )
    _text(parent, label, x, line_y + 0.9, "guide-label", anchor=anchor)


def _uranium_guide(
    root: ET.Element,
    elements: tuple[Element, ...],
    locale: dict,
    scale: str,
    page: Page,
    colours: dict[str, str],
    rounded_corners: bool,
    cell_style: str,
    content: str,
    classification: str,
) -> None:
    uranium = next(element for element in elements if element.symbol == "U")
    x, y, factor = 136.0, 42.0, 1.35
    width = page.cell_width * factor
    wrapper = _node(
        root,
        "g",
        transform=f"translate({x:g} {y:g}) scale({factor:g})",
        **{"class": "uranium-guide"},
    )
    _render_cell(
        wrapper,
        uranium,
        0,
        0,
        page,
        locale,
        scale,
        colours,
        element_id="guide-U",
        rounded_corners=rounded_corners,
        cell_style=cell_style,
        content=content,
        classification=classification,
    )

    left, right = x - 7, x + width + 7
    # End leaders just outside the rendered values. The enlarged cell scales
    # its internal padding, so targeting those text anchors directly makes the
    # rules appear to touch—or, for a wide value, cross—the glyphs.
    left_value_edge = x + 0.4
    right_value_edge = x + width - 0.4
    _guide_callout(
        root,
        locale["labels"]["atomic_number"],
        left,
        y + 3.0,
        left_value_edge,
        anchor="end",
    )
    _guide_callout(
        root,
        locale["labels"]["atomic_weight"],
        right,
        y + 3.0,
        right_value_edge,
        anchor="start",
    )
    _guide_callout(
        root,
        locale["labels"]["element_symbol"],
        right,
        y + (13.1 if content == "simplified" else 8.9),
        x + width / 2 + 6.8,
        anchor="start",
    )
    _guide_callout(
        root,
        locale["labels"]["element_name"],
        right,
        y + (19.2 if content == "simplified" else 15.7),
        x + width / 2 + 6.2,
        anchor="start",
    )
    if content == "simplified":
        _text(
            root,
            locale["labels"]["radioactive_sign"],
            x + width / 2,
            y - 2.2,
            "guide-label",
            anchor="middle",
        )
        _node(
            root,
            "line",
            x1=x + width / 2,
            y1=y - 1.4,
            x2=x + width / 2,
            y2=y + 1.2,
            **{"class": "guide-line"},
        )
        return
    _guide_callout(
        root,
        locale["labels"]["electronegativity"],
        left,
        y + 20.6,
        left_value_edge,
        anchor="end",
    )
    _guide_callout(
        root,
        f"{locale['labels']['first_ionisation_energy']} ({locale['units']['first_ionisation_energy']})",
        right,
        y + 20.6,
        right_value_edge,
        anchor="start",
    )
    _guide_callout(
        root,
        locale["labels"]["oxidation_states"],
        left,
        y + 24.8,
        x + width / 2 - 9.4,
        anchor="end",
    )
    _guide_callout(
        root,
        locale["labels"]["electron_configuration"],
        right,
        y + 29.7,
        x + width / 2 + 11.5,
        anchor="start",
    )
    _text(
        root,
        locale["labels"]["radioactive_sign"],
        x + width / 2,
        y - 2.2,
        "guide-label",
        anchor="middle",
    )
    _node(
        root,
        "line",
        x1=x + width / 2,
        y1=y - 1.4,
        x2=x + width / 2,
        y2=y + 1.2,
        **{"class": "guide-line"},
    )


def render_svg(
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
    """Write a landscape SVG at the requested physical page size."""

    validate_electronegativity_scale(electronegativity_scale)
    if cell_style not in SUPPORTED_CELL_STYLES:
        choices = ", ".join(SUPPORTED_CELL_STYLES)
        raise ValueError(f"Unsupported cell style: {cell_style!r}; choose {choices}")
    if content not in SUPPORTED_CONTENT_MODES:
        choices = ", ".join(SUPPORTED_CONTENT_MODES)
        raise ValueError(f"Unsupported content mode: {content!r}; choose {choices}")
    if classification not in SUPPORTED_CLASSIFICATION_MODES:
        choices = ", ".join(SUPPORTED_CLASSIFICATION_MODES)
        raise ValueError(
            f"Unsupported classification mode: {classification!r}; choose {choices}"
        )
    colours = get_palette(colour_scheme)
    theme = THEME
    page_size = page_size.upper()
    if page_size not in PAGE_SIZES_MM:
        raise ValueError(f"Unsupported page size: {page_size!r}; choose A3 or A4")
    page = Page()
    physical_width, physical_height = PAGE_SIZES_MM[page_size]
    locale = load_locale(language)
    root = ET.Element(
        f"{{{SVG}}}svg",
        {
            "width": f"{physical_width:g}mm",
            "height": f"{physical_height:g}mm",
            "viewBox": f"0 0 {page.width:g} {page.height:g}",
            "role": "img",
            "aria-labelledby": "title description",
        },
    )
    title = _node(root, "title", id="title")
    title.text = locale["labels"]["title"]
    description = _node(root, "desc", id="description")
    description.text = (
        f"{page_size} landscape periodic table containing 118 chemical elements. "
        "Solid colours identify chemical classifications."
    )
    metadata = _node(root, "metadata")
    metadata.text = (
        "Copyright 2026 Periodisk contributors. Original table design "
        "and explanatory content licensed under CC BY 4.0: "
        "https://creativecommons.org/licenses/by/4.0/. The Python software "
        "used to generate this table is separately licensed under MIT."
    )
    style = _node(root, "style")
    cell_rule = theme["soft_rule"] if cell_style == "soft-rules" else theme["rule"]
    cell_rule_width = "0.16" if cell_style == "soft-rules" else "0.25"
    style.text = f"""
      text {{ fill: {theme["text"]}; font-family: \"Noto Sans\", \"DejaVu Sans\", sans-serif; }}
      .page-title {{ font-size: 6.5px; font-weight: 700; }}
      .group-number, .period-number {{ font-size: 3px; font-weight: 700; }}
      .footer {{ fill: #666666; font-size: 2.2px; }}
      .source {{ fill: {theme["source"]}; font-size: 2.2px; }}
      .element-cell {{ fill: none; stroke: {cell_rule}; stroke-width: {cell_rule_width}; }}
      .cell-fill {{ stroke: none; }}
      .placeholder {{ fill: {theme["placeholder"]}; stroke: {theme["rule"]}; stroke-width: 0.25; }}
      .placeholder {{ stroke-dasharray: 1 0.7; }}
      .atomic-number {{ font-size: 2.55px; font-weight: 600; }}
      .radioactive {{ fill: {theme["text"]}; }}
      .radioactive-ring {{ fill: none; stroke: {theme["text"]}; stroke-width: 0.11; }}
      .symbol {{ font-size: 6.2px; font-weight: 700; }}
      .name {{ font-size: 2.3px; }}
      .simplified-top-number {{ font-size: 3.55px; font-weight: 650; }}
      .simplified-symbol {{ font-size: 9.5px; }}
      .simplified-name {{ font-size: 3.1px; font-weight: 500; }}
      .atomic-weight {{ font-size: 2.35px; font-weight: 600; }}
      .property {{ font-size: 2.05px; }}
      .configuration {{ font-size: 2.45px; }}
      .series-label {{ font-size: 3.2px; font-weight: 650; }}
      .legend-swatch {{ stroke: {theme["rule"]}; stroke-width: 0.25; }}
      .split-outline {{ fill: none; }}
      .legend-label {{ font-size: 2.6px; font-weight: 500; }}
      .guide-label {{ font-size: 2.9px; font-weight: 600; }}
      .guide-line {{ stroke: {theme["guide"]}; stroke-width: 0.25; }}
    """
    _node(
        root, "rect", x=0, y=0, width=page.width, height=page.height, fill=theme["page"]
    )
    heading_x = 45.0
    _text(
        root, locale["labels"]["title"], heading_x, 23.5, "page-title", anchor="start"
    )
    for group_number in range(1, 19):
        x = page.margin_x + (group_number - 0.5) * page.cell_width
        _text(root, str(group_number), x, 16.1, "group-number", anchor="middle")

    for period_number in range(1, 8):
        y = page.table_y + (period_number - 0.5) * page.cell_height + 1
        _text(
            root,
            str(period_number),
            page.margin_x - 2.0,
            y,
            "period-number",
            anchor="end",
        )

    elements = load_elements()
    for placement in placements(elements, page):
        _render_cell(
            root,
            placement.element,
            placement.x,
            placement.y,
            page,
            locale,
            electronegativity_scale,
            colours,
            rounded_corners=rounded_corners,
            cell_style=cell_style,
            content=content,
            classification=classification,
        )
    for x, y, label in placeholder_positions(page):
        rounded = {"rx": 0.8, "ry": 0.8} if rounded_corners else {}
        inset = 0.45 if cell_style == "gutters" else 0.0
        _node(
            root,
            "rect",
            x=f"{x + inset:.2f}",
            y=f"{y + inset:.2f}",
            width=page.cell_width - 2 * inset,
            height=page.cell_height - 2 * inset,
            **rounded,
            **{"class": "placeholder"},
        )
        _text(
            root,
            label,
            x + page.cell_width / 2,
            y + 12,
            "series-label",
            anchor="middle",
        )

    series_label_x = page.margin_x + 2 * page.cell_width - 2
    _text(
        root,
        locale["classifications"]["lanthanide"],
        series_label_x,
        page.f_block_y + 13,
        "series-label",
        anchor="end",
    )
    _text(
        root,
        locale["classifications"]["actinide"],
        series_label_x,
        page.f_block_y + page.cell_height + 13,
        "series-label",
        anchor="end",
    )
    _uranium_guide(
        root,
        elements,
        locale,
        electronegativity_scale,
        page,
        colours,
        rounded_corners,
        cell_style,
        content,
        classification,
    )
    _legend(root, locale, page, colours, classification)
    electronegativity_source = locale["source_notes"][electronegativity_scale]
    footer_line_1 = (
        f"{locale['labels']['sources']}: "
        f"CIAAW 2024 ({locale['source_notes']['atomic_masses']})   ·   "
        f"NIST ASD ({locale['source_notes']['ionisation_energies']})   ·   "
        f"{electronegativity_source}"
    )
    footer_line_2 = (
        f"Mendeleev 1.2.0 ({locale['source_notes']['electron_configurations']})"
        f"   ·   {locale['source_notes']['oxidation_states']}"
    )
    if content == "simplified":
        footer_line_1 = f"{locale['labels']['sources']}: CIAAW 2024 ({locale['source_notes']['atomic_masses']})"
        _text(root, footer_line_1, heading_x, 28.0, "source", anchor="start")
    else:
        _text(root, footer_line_1, heading_x, 28.0, "source", anchor="start")
        _text(root, footer_line_2, heading_x, 32.0, "source", anchor="start")
    _text(
        root,
        "© 2026 Periodisk contributors · CC BY 4.0",
        page.width - page.margin_x,
        277.0,
        "footer",
        anchor="end",
    )

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)
    return destination
