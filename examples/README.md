# Rendered examples

Outputs are grouped by locale and format:

```text
examples/
├── en_GB/
│   ├── pdf/
│   └── svg/
└── nb_NO/
    ├── pdf/
    └── svg/
```

`pdf/` contains print-ready files. `svg/` contains editable,
resolution-independent renders for the canonical tables and selected variants.

## Included outputs

Files without a variant suffix use Pauling electronegativity, full scientific
content, detailed classification, and the default Tol Light–inspired colours.

Each locale contains the same six outputs:

| Variant | PDF | SVG |
|---|:---:|:---:|
| Default, full content, A3 | Yes | Yes |
| Default, full content, A4 | Yes | — |
| `broad-light`, simplified broad classification, A3 | Yes | Yes |
| Powder, gutters and rounded corners, A3 | Yes | — |

A3 is recommended for the dense full-data layout. A4 uses the same vector
composition at a smaller physical scale.

English and Norwegian therefore have equal format and feature coverage. The
example set demonstrates the main use cases without duplicating every palette;
all selectable colours are shown in
[`../docs/colour-schemes.svg`](../docs/colour-schemes.svg).

## Filenames

The base form is `periodic-table-{language}-{page-size}`. The included variant
suffixes are:

- `-broad-light-simplified-broad`
- `-powder-gutters-rounded`

Suffixes describe non-default choices in this order: colour scheme, cell
treatment, content mode, and classification mode. Other palettes, soft rules,
Allen electronegativity, and calculated Allred–Rochow electronegativity remain
selectable through the renderer but are not duplicated in the example set.
