"""Physical A3 layout independent of the SVG rendering implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Element


@dataclass(frozen=True, slots=True)
class Page:
    width: float = 420.0
    height: float = 297.0
    margin_x: float = 10.2
    table_y: float = 18.0
    cell_width: float = 22.2
    cell_height: float = 24.5
    f_block_y: float = 198.0


@dataclass(frozen=True, slots=True)
class Placement:
    element: Element
    x: float
    y: float
    row: int
    column: int
    section: str


DEFAULT_PAGE = Page()


def placements(
    elements: tuple[Element, ...], page: Page = DEFAULT_PAGE
) -> tuple[Placement, ...]:
    """Place every element once in the 18-column long-form arrangement."""

    result: list[Placement] = []
    for element in elements:
        number = element.atomic_number
        if 57 <= number <= 71:
            column = number - 54  # La starts below main-table group 3.
            row = 1
            y = page.f_block_y
            section = "lanthanides"
        elif 89 <= number <= 103:
            column = number - 86  # Ac starts below main-table group 3.
            row = 2
            y = page.f_block_y + page.cell_height
            section = "actinides"
        else:
            if element.group is None:
                raise ValueError(f"No main-table group for {element.symbol}")
            column = element.group
            row = element.period
            y = page.table_y + (row - 1) * page.cell_height
            section = "main"
        x = page.margin_x + (column - 1) * page.cell_width
        result.append(Placement(element, x, y, row, column, section))
    return tuple(result)


def placeholder_positions(
    page: Page = DEFAULT_PAGE,
) -> tuple[tuple[float, float, str], ...]:
    x = page.margin_x + 2 * page.cell_width
    return (
        (x, page.table_y + 5 * page.cell_height, "57–71"),
        (x, page.table_y + 6 * page.cell_height, "89–103"),
    )
