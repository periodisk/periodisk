# Periodisk

Periodisk is an open-source Python package for generating accessible,
source-traceable periodic tables for chemistry teaching. It produces SVG and
PDF files using an offline dataset of all 118 elements.

## Ready-made tables

Print-ready PDFs can be downloaded without installing Periodisk:

| Table | English | Norwegian Bokmål |
| --- | :---: | :---: |
| Detailed, A3 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a3.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a3.pdf) |
| Detailed, A4 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a4.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a4.pdf) |
| Simplified, A3 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a3-broad-light-simplified-broad.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a3-broad-light-simplified-broad.pdf) |
| Simplified, A4 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a4-broad-light-simplified-broad.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a4-broad-light-simplified-broad.pdf) |
| Exam, colour, A4 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a4-broad-tol-light-broad.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a4-broad-tol-light-broad.pdf) |
| Exam, black and white, A4 | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/en_GB/pdf/periodic-table-en-a4-broad-grey-broad.pdf) | [PDF](https://github.com/periodisk/periodisk/blob/main/examples/nb_NO/pdf/periodic-table-nb-a4-broad-grey-broad.pdf) |

These files are generated from the main branch on GitHub and may include
changes made after this release.

## Installation

Periodisk requires Python 3.13 or newer.

```console
python -m pip install periodisk
```

## Usage

### Command line

The `periodisk render` command writes a periodic table to an SVG or PDF file.
The output format is inferred from the filename extension. For example, render
the default English table on an A3 page with:

```console
periodisk render periodic-table.pdf --language en_GB --page-size A3
```

Run `periodisk render --help` for every option and its description.

### Python API

The same table can be generated through the Python API:

```python
from periodisk import render_table

render_table(
    "periodic-table.pdf",
    language="en_GB",
    page_size="A3",
)
```

Periodisk supports:

- British English and Norwegian Bokmål (`nb_NO`)
- Detailed and simplified table content
- Detailed and broad element classifications
- Multiple accessible, print-oriented colour schemes
- Configurable cell styles and rounded corners
- Pauling, Allred–Rochow, and Allen electronegativity scales
- SVG and PDF output

## Documentation

The [GitHub repository](https://github.com/periodisk/periodisk) contains the
full documentation and rendered examples:

- [Examples](https://github.com/periodisk/periodisk/tree/main/examples)
- [Scientific data sources and methods](https://github.com/periodisk/periodisk/blob/main/docs/DATA_SOURCES.md)
- [Design and colour schemes](https://github.com/periodisk/periodisk/blob/main/docs/DESIGN.md)
- [Localisation](https://github.com/periodisk/periodisk/blob/main/docs/LOCALISATION.md)

## Licence

The Python source code is available under the
[MIT License](https://github.com/periodisk/periodisk/blob/main/LICENSE).
Original documentation and rendered periodic tables are available under
[CC BY 4.0](https://github.com/periodisk/periodisk/blob/main/LICENSE-CONTENT.md).
Scientific provenance and third-party notices are documented in the
[repository](https://github.com/periodisk/periodisk/blob/main/THIRD_PARTY_NOTICES.md).
