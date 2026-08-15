# Periodisk

Periodisk is an open-source Python package for generating accessible,
source-traceable periodic tables for chemistry teaching. It produces SVG and
PDF files using an offline dataset of all 118 elements.

## Installation

Periodisk requires Python 3.13 or newer.

```console
python -m pip install periodisk
```

## Usage

Render an English A3 periodic table from the command line:

```console
periodisk render periodic-table.pdf --language en_GB --page-size A3
```

The equivalent Python API is:

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
- Pauling, Allred-Rochow, and Allen electronegativity scales
- SVG and PDF output

Run `periodisk render --help` for the complete set of options.

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
