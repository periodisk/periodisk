# Changelog

Periodisk uses calendar-based versions in the form `YYYY.N`. This file records
user-visible changes. Scientific data decisions and limitations are documented
separately in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Unreleased

## 2026.6 — 2026-11-21

### Fixes

- Fixed minus signs rendering as missing-glyph boxes in PDFs on systems whose
  Noto Sans lacks U+2212; minus signs now use a fallback font that has it.

### Colour schemes

- Lightened `broad-grey` (metalloids `#E6E6E6`, nonmetals `#CCCCCC`, noble
  gases `#B3B3B3`). Its hatching is darker and sparser, with white
  knock-outs behind every label so it never crosses text.

### Examples and documentation

- Added A4 exam examples in `broad-tol-light` and `broad-grey`, and a
  simplified A4 example, for both locales.
- Reorganised the README around side-by-side detailed and simplified English
  previews and a download table of ready-made PDFs for readers who do not
  install the package.
- Tightened documentation wording and made the suggested content-licence
  attribution version-neutral.

## 2026.5 — 2026-11-18

### Terminology

- Audited every displayed Bokmål term against Bokmålsordboka, NAOB, Store
  norske leksikon, and IUPAC, with validated curation records for the 118
  element names, the classification terms and their scope, and the labels,
  source notes, and units.
- Labelled the displayed standard atomic weights as `Relativ atommasse` and
  `Atomic weight`; the bracket explanation moves to a second guide line.
- Renamed the detailed nonmetal category to `Andre ikke-metaller` and
  `Other nonmetals`, since halogens and noble gases are also nonmetals; broad
  mode keeps `Ikke-metaller` and `Nonmetals`.
- Labelled the English f-block series `Lanthanoids` and `Actinoids`, following
  the IUPAC periodic table and recommendations.
- Replaced `reskalert` with `skalert` in the Norwegian Allen source note.
- Used a true minus sign (−) for negative oxidation states in element cells.

### Colour schemes

- Added `broad-grey` for black-and-white printing, with clearly separated grey
  steps and hatched cells for incompletely characterised elements.
- Added `broad-tol-pale`, a lighter `broad-tol-light` for on-screen reading.
- Made incompletely characterised elements white in `broad-tol-light`,
  separating Og from the noble gases more clearly.

### Other changes

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

- Added a PyPI README with working documentation links.
- Refined installation, usage, development, and licensing documentation.

## 2026.1 — 2026-08-14

- Published the initial Periodisk package and release workflow.
