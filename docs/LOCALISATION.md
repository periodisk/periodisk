# Localisation

The renderer currently supports British English (`en_GB`) and Norwegian
Bokmål (`nb_NO`). Scientific data stay language-neutral and localisation is
applied only while rendering.

Each JSON file in `src/periodisk/resources/locales/` defines:

- the decimal separator and missing-value mark;
- table, accessibility, and scientific-field labels;
- all 118 localised element names, keyed by symbol;
- chemical-classification names; and
- displayed units.

Element names live only in the locale resources. The scientific element
records therefore remain language-independent. Each locale also identifies
the source of its element-name list. Locale resources are validated when
loaded, so an incomplete set of 118 names, an empty name, or a missing section
fails before rendering.

The SVG root uses the locale identifier as a BCP 47 language tag, and its
accessible title and description are taken from the locale resource.

To add a language, create a complete locale JSON resource containing the 118
element names, add its identifier to `SUPPORTED_LOCALES` in `settings.py`, and
extend the localisation/rendering tests. Decimal punctuation must never be
written into the underlying numeric scientific values.

Electronegativity scales are registered independently in
`SUPPORTED_ELECTRONEGATIVITY_SCALES`. A scale needs sourced values in the
element records and a translated display name in every locale. Missing values
render as an em dash rather than zero.
