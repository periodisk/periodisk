# Visual design

The table prioritises readable scientific content and print suitability.
Chemical classification is encoded primarily by cell colour and identified by
the legend. The scientific values remain readable independently of that
classification cue. All palettes use near-black text. An
[automated test](../tests/test_render_svg.py) checks every
palette background against its text colour using the sRGB relative-luminance
and contrast-ratio formulas from WCAG 2.2.[^wcag] Each pair must meet the 4.5:1
Level AA minimum for normal text.

The test decodes each hexadecimal sRGB colour, linearises its three channels,
calculates relative luminance as `0.2126 R + 0.7152 G + 0.0722 B`, and compares
the lighter and darker luminances as `(L1 + 0.05) / (L2 + 0.05)`. It applies
this calculation to every entry in `PALETTES` against that scheme's text
colour, currently `#111111`.

This is a conservative numerical design check, including for text large enough
to qualify for WCAG's lower 3:1 threshold. It is not a claim of complete WCAG
conformance. It tests text–background contrast, not whether category colours
are distinguishable from one another, and does not model colour-vision
deficiencies, paper, ink, printer profiles, or viewing conditions.

## Colour and classification

The default is a ten-family adaptation of Paul Tol's Light qualitative
palette,[^tol] which was designed for labelled cells. `tol-light-inspired`
selects the same treatment explicitly. `classic` is derived from the
colour-universal palette developed by Masataka Okabe and Kei Ito[^okabe-ito]
and described by Bang Wong.[^wong] Other schemes provide lighter, muted,
vivid, greyscale, and print-oriented alternatives.

![Compare all selectable colour schemes](colour-schemes.svg)

The chart is generated from the renderer's palette definitions with:

```console
PYTHONPATH=src python scripts/render_palette_preview.py
```

The detailed classification has ten families. Po and At use diagonal split
fills, and elements whose chemistry is insufficiently characterised use a
neutral fill. The SVG retains conventional family information in
`data-classifications` even when the visible treatment is neutral.

The optional `broad` mode merges the families into metals, metalloids,
nonmetals, and noble gases. It preserves the neutral chemistry status and the
split treatment of Po and At. `broad-light` and `broad-tol-light` are designed
for this four-colour classification. `broad-tol-pale` lightens
`broad-tol-light` for on-screen reading: metals, which cover most of the
table, are mixed with 45 % white, metalloids and nonmetals with 40 %, and the
already light noble gases with 15 %, raising text contrast while keeping the
classes distinct. `broad-grey` is designed
for black-and-white printing: metals, the largest class, are white, the other
classes use light, distinct neutral greys, and incompletely characterised
elements are white with sparse diagonal hatching. White knock-outs behind each
label and the radioactivity symbol keep the hatching off the text. A white
text halo is not used because CairoSVG strokes text after filling it, which
would thin the glyphs. The hatching is the only non-colour encoding of a
category; a further grey step was too close to its neighbours on screen.

Noto Sans is the text font, but some distributions ship a build without
U+2212 MINUS SIGN, and CairoSVG has no per-glyph font fallback. Minus signs
are therefore set in a `minus` span whose font stack (DejaVu Sans, Liberation
Sans, Noto Sans Math) starts with fonts that contain the glyph. CairoSVG
only uses the first family in a stack and aligns each span separately, so
before PDF conversion centred and right-aligned text containing such a span is
measured with Cairo and redrawn left-aligned at the equivalent position.

A [test](../tests/test_render_pdf.py) renders every combination of language,
content, classification, and electronegativity scale, resolves each text
run's font as CairoSVG does, and fails if any character has no glyph in that
font. The result depends on the fonts installed where the tests run.

Every rendered table includes a legend that names the colour categories, but
the legend is not a redundant visual encoding. Readers who cannot distinguish
two fills may also be unable to assign the corresponding elements to their
classes. The SVG retains classification names as metadata; printed tables do
not currently provide a non-colour classification encoding.

## Cell content

The full layout contains atomic number, atomic weight, symbol, name,
electronegativity, first ionisation energy, oxidation states, and ground-state
electron configuration. Labels for the compact scientific fields are omitted
from individual cells. An enlarged uranium example explains their positions.
Its callouts also explain bracketed isotope mass numbers.

The simplified layout retains atomic number, atomic weight, symbol, name, and
the radioactivity marker, using larger type to make better use of each cell.

The radioactivity symbol means that an element has no stable isotopes. It is
drawn as native SVG geometry for consistent SVG and PDF output without a
platform-specific symbol font.

## Layout options

Cells are slightly taller than wide (22.2 × 24.5 mm in the canonical A3
layout) and have full fills by default. The independent visual options are:

- `--rounded-corners` for a 0.8 mm radius in the canonical A3 output;
- `--cell-style gutters` for narrow white separation between cells; and
- `--cell-style soft-rules` for thinner grey grid lines.

Colour scheme, classification mode, content density, cell style, and rounded
corners can be combined independently.

## References

[^wcag]: W3C, [*Web Content Accessibility Guidelines (WCAG) 2.2*, Success
    Criterion 1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum) and
    [relative-luminance
    definition](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance).

[^tol]: Paul Tol, [*Colour Schemes*, technical note SRON/EPS/TN/09-002, issue
    3.2](https://sronpersonalpages.nl/~pault/data/colourschemes.pdf) (2021).

[^okabe-ito]: Masataka Okabe and Kei Ito,
    [*Color Universal Design*](https://jfly.uni-koeln.de/color/) (2002–2008).

[^wong]: Bang Wong, “Color blindness,” *Nature Methods* **8**, 441 (2011),
    [doi:10.1038/nmeth.1618](https://doi.org/10.1038/nmeth.1618).
