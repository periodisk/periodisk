# Third-party notices

The package contains a source-traceable scientific dataset assembled from the
sources listed in [`DATA_SOURCES.md`](docs/DATA_SOURCES.md). Individual
scientific facts are not claimed as original project content. Copyright,
database rights, and other rights in source material remain with their
respective holders.

## Mendeleev data

Some values in `src/periodisk/resources/elements.json` were imported or
calculated from data distributed by
[*mendeleev-data* 1.2.0](https://github.com/lmmentel/mendeleev-data), including
electron configurations, electronegativities, ionisation energies, covalent
radii, and effective nuclear charges. The data repository is distributed under
the following licence:

> MIT License
>
> Copyright (c) 2024 Lukasz Mentel
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

Mendeleev identifies further scientific sources for individual fields. Its MIT
licence does not replace any rights that may apply to those upstream sources;
they are identified in `docs/DATA_SOURCES.md` and in the machine-readable source
registry.

## Wikipedia comparison data

The maintenance-only oxidation-state snapshot in
`curation/oxidation_states/wikipedia.json` is derived from Wikipedia under
CC BY-SA 4.0. It records the authorship attribution, permanent revision URL,
retrieval time, and licence. It is not included in the installed Python
package or used as the runtime dataset.
