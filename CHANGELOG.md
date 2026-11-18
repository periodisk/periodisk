# Changelog

Periodisk uses calendar-based versions in the form `YYYY.N`. This file records
user-visible changes. Scientific data decisions and limitations are documented
separately in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Unreleased

- Renamed the detailed nonmetal category to `Andre ikke-metaller` and
  `Other nonmetals`, since halogens and noble gases are also nonmetals; broad
  mode keeps `Ikke-metaller` and `Nonmetals`.
- Added a sourced audit of the Bokmål classification terms and their scope.
- Made incompletely characterised elements white in `broad-tol-light`, separating
  Og from the noble gases more clearly.
- Added the `broad-grey` colour scheme for black-and-white printing.
- Added a sourced audit of all 118 Bokmål element names; every name was retained.
- Used a true minus sign (−) for negative oxidation states in element cells.
- Corrected leader alignment in the enlarged simplified element guide.
- Strengthened scientific-resource and locale validation.
- Localised SVG accessibility descriptions and language metadata.
- Added reproducible generation and freshness checks for rendered examples.

## 2026.4 — 2026-08-18

- Corrected the Norwegian spelling of ruthenium.
- Strengthened locale and scientific-data validation.
- Added installed-wheel validation and rendering before PyPI publication.

## 2026.3 — 2026-08-15

- Simplified formatting and SVG rendering internals.
- Removed module-name collisions from the public rendering API.
- Deduplicated palette and theme definitions.
- Required successful tests before release publication.
- Corrected and clarified design and usage documentation.

## 2026.2 — 2026-08-15

- Added a concise, self-contained PyPI README with working documentation links.
- Refined installation, usage, development, and licensing documentation.

## 2026.1 — 2026-08-14

- Published the initial Periodisk package and release workflow.
